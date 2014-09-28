
Depdep is a merciless sentinel which will seek sensitive files containing critical info leaking through your network. Basically, it is a fast and practical sensitive data search tool maintaining personal & commercial data privacy for companies and institutions. It can very well be used by auditors making sure that their network doesn't leak any unauthorized non-compliant data through windows & unix/linux shares.
The usage is easy and configurable, however, certain technical knowledge is necessary, such as using linux console, ability of writing and understanding basic regular expressions, tough the configuration file comes with several sensitive information patterns, etc.  

### Installation
In order to run depdep succesfully, you have to install some packages. Packages needed to run depdep succesfully are shown below;  
nmap -> to scan network and detect opened 445/tcp ports
cifs-utils -> to mount windows shares from linux machine
mount -> to mount and umount operations
smbclient -> to list windows shares
samba4-clients -> other operations for listing and accessing windows shares from linux machine
findutils -> the find command utility
curl -> to upload files to tika and get results
For installation, you can use apt-get. For Kali Linux :

```
 #apt-get install nmap cifs-utils mount smbclient samba4-clients findutils curl
```

There is tika binary in the script directory. In order to run tika, java must be installed on the system. You can achieve this using apt-get like below;  
```
 # apt-get install openjdk-6-jre-headless:amd64
```
Then you must download tika from internet and run like below. You can download Apache Tika at *http://mvnrepository.com/artifact/org.apache.tika/tika-server*. Most recent version is 1.5 so that this version can be used to extract files. 
```
 # cd /opt/tika
 # wget http://central.maven.org/maven2/org/apache/tika/tika-server/1.5/tika-server-1.5.jar  
 # /usr/bin/java -jar /opt/tika/tika-server-1.5.jar >/dev/null 2>/dev/null &  
```
Also depdep comes with a script (script/tika.sh) that you can use for managing tika easily. Copy it under /etc/init.d/ and use it below. But at first you must download tika and move it into /opt/tika directory and move tika.sh script into the /etc/init.d directory.  
```
 # mkdir /opt/tika  
 # cp script/tika.sh /etc/init.d/tika  
 # /etc/init.d/tika.sh start  
[+] Tika has been started ...  
```

In order to check whether the tika process is running use ps command;
```
 # ps -ef | grep java | grep -v grep
root     13066     1 99 15:52 pts/3    00:00:01 /usr/bin/java -jar /opt/tika/tika-server-1.4.jar
```
After that, you have to configure depdep configuration file, **config/depdep.xml**, to run depdep. The configuration is easy to understand and contains directive comments.

Also installation script comes with depdep (**script/installation.sh**). You can easily install depdep via this script. Only thing which you should specify which distro you want to run on. For instance, in order to install depdep on kali follow steps below;  
```
 # chmod 755 script/installation.sh  
 # .script/installation.sh kali  
```

 ArchAssault has this prepackaged in their repo, you can install it with "**pacman -S depdep-git**".
```
 # pacman -S depdep-git  
```
Once you have installed depdep, you should start tika via tika.sh script like below;
```
 # /etc/init.d/tika.sh start
```

###Basic Usage

```
 # python depdep.py --config config/depdep.xml
```
Without "**-w 1**" option, depdep will resume from its previous work. If you don't want depdep to resume, but start fresh please start it like below;
```
 # python depdep.py --config config/depdep.xml -w 1
```

Also if you want to see debug message you should use "-v 1" option. 
```
 # python depdep.py --config config/depdep.xml -w 1 -v 1
```

### To Do:
- Process using hostname or ip address
- Advanced logging operations
- Advanced debugging operations
- Detect & process linux shares (NFS)
- Detect & process FTP shares 

