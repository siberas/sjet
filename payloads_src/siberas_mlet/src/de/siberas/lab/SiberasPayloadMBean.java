 package de.siberas.lab;

public interface SiberasPayloadMBean {
	
	public String runCMD(String passwd, String cmd);
	public String runJS(String passwd, String js);
	public boolean changePassword(String oldPass, String newPass);
	
}
