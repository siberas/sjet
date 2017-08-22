// define Java classes in JavaScript
var System = Java.type("java.lang.System");
var properties = System.getProperties();

for each (var key in properties.keySet())  {
	print(key + "=" + properties[key]); 
}
