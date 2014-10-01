
try:
	import sys
	import re
	import os
	import subprocess
	from nmap import Nmap
	from core.common import *
	from core.configparser import ConfigParser
	from mount_detect import MountDetect
	from core.threadpool import Worker,ThreadPool
except ImportError,e:
        import sys
        sys.stdout.write("%s\n" %e)
        sys.exit(1)


class Main:
	"""
		Main Class and Functions ...
	"""

	def __init__(self, config_file, verbose, wipe = None):
		"""
			Nmap init functions set variables
		"""

		self.config_file = config_file
		self.wipe = wipe
		self.verbose = verbose
		self.session_id = 0

		self.share_reg = re.compile("^Disk\|[^$]+\|")
		self.status_reg = re.compile("[0-9]+")
		self.share_file_reg = re.compile("[0-9]+,")

		current_dir = os.getcwd()
		self.share_session = current_dir + "/" + "sessions/share.session"
		self.sharestatus_session =  current_dir + "/" + "sessions/sharestatus.session"

		self.nmap_path = "/usr/bin/nmap"
                self.mount_cifs_path = "/sbin/mount.cifs"
		self.mount_path = "/bin/mount"
		self.umount_path = "/bin/umount"
                self.smbclient_path = "/usr/bin/smbclient"
                self.find_path = "/usr/bin/find"
		self.curl_path = "/usr/bin/curl"
		self.java = "/usr/bin/java"

                packages = [ self.nmap_path, self.mount_cifs_path, self.umount_path, self.mount_path, self.smbclient_path, self.find_path, self.curl_path, self.java] 
                for pkg in packages:
                        if not os.path.isfile(pkg):
                                        print >> sys.stderr,  bcolors.OKBLUE + "Error : " + bcolors.ENDC + bcolors.FAIL + "Package %s doesn't exists"%(pkg) + bcolors.OKBLUE  + bcolors.ENDC
                                        sys.exit(1)

                self.config_result = ConfigParser.parse(self.config_file)
		


	def is_sharestatus_file(self):
		"""
			Check sharestatus.session file and whether there are some records in it or not ...
		"""

		if not os.path.isfile(self.sharestatus_session):
			return None

		try:
			read_file = open(self.sharestatus_session, "r").read().splitlines()
		except:
			return None

		for line in read_file:
			if re.match(self.status_reg, line):
		 		return line

		return None				
	

	def is_share_file(self):
                """     
                        Check sharestatus.session file and whether there are some records in it or not ...
                """
                
                if not os.path.isfile(self.share_session):
                        return None
                
		try:
                	read_file = open(self.share_session, "r").read().splitlines()
		except:
			return None

                for line in read_file:
                        if re.match(self.share_file_reg, line):
                                return True
                return None


	def feed_sessions(self, ip, path):
		"""
			Feed Sessions ...
		"""
		
		try:
			session_file = open(self.share_session,"a")		
		except Exception, err_mess:
			print err_mess
			sys.exit(1)

		sess_id = str(self.session_id) + "," + ip + "," + path + "\n"

		session_file.write(sess_id)	
		session_file.close()
		self.session_id = self.session_id + 1


	def list_sharing(self, ip, output_file):
		"""
			Listing sharing ...
		"""

		if self.config_result["username"] and self.config_result["password"] and self.config_result["domain"]:
			creds = "'" + self.config_result["domain"] + "\\" + self.config_result["username"] + "%" + self.config_result["password"] + "'"
			run_smbclient = "%s -L %s -U %s -g 2>/dev/null"% (self.smbclient_path, ip, creds)
		else:
			run_smbclient = "%s -L %s -N -g 2>/dev/null"% (self.smbclient_path, ip)

		# debug
		if self.verbose > 0:
			print "   [+] Command to run: " + run_smbclient

                proc = subprocess.Popen([run_smbclient], shell = True, stdout = subprocess.PIPE,)

                share_name = None
                for line in iter(proc.stdout.readline,''):
                        share_result = line.rstrip()
                        if re.match(self.share_reg, share_result):
                                if not share_name:
                                        share_name = str(share_result.split("|")[1])
                                else:
                                        share_name = share_name + ":" + str(share_result.split("|")[1])
                if share_name:
                        self.feed_sessions(ip, share_name)



	def run(self):
		"""
			Run Nmap Operations ..
		"""

		# if wipe is 1, remove all session file
		if self.wipe == 1:
			try:
                		os.remove(self.share_session)
                        	os.remove(self.sharestatus_session)
                      	except: 
                                pass

			include_ip = self.config_result["include_ip"]
			exclude_ip = self.config_result["exclude_ip"]
	
			self.nmap = Nmap(self.nmap_path)

			nmap_result = self.nmap.port_scan(include_ip, exclude_ip)
			if nmap_result:
				thread_count = int(self.config_result["scanning_thread"])
                        	output_file = self.config_result["output_file"]	
			
				# debug
				if self.verbose > 0:
					print "   [+] Thread count to run nmap %s"% thread_count

                        	pool = ThreadPool(thread_count)
                        	for ip in nmap_result:
                                	pool.add_task(self.list_sharing, ip, output_file)
                        	pool.wait_completion()


		try:
			mount_detect =  MountDetect(self.config_file, self.share_session, self.sharestatus_session, self.mount_path, self.umount_path, self.find_path, self.curl_path, self.verbose)
		except:
			print >> sys.stderr, "Error when initializing mountdetect class !!!"
			sys.exit(1)

		share_status = self.is_sharestatus_file()

		# if share status file exists
		if share_status :
			#debug
			if self.verbose > 0:
				print "   [+] SessionStatus exists , go go go ..."

			rest_line = self.is_sharestatus_file()
			if rest_line:
				mount_detect.run(int(rest_line))
			else:
				print "Error getting data from SessionStatus file"
				sys.exit(1)

		# if share status file doesn't exists
		else:
			share_file = self.is_share_file()
			# if share.session file exists
			if share_file:
				#debug
				if self.verbose > 0:
					print "   [+] There is no SessionStatus file but Share file exists , go go go ..."
				mount_detect.run(0)
			# if share.session file doesn't exists
			else:
				#debug
				if self.verbose > 0:
					print "   [+] There is no session file. Bye ..."
				sys.exit(1)

