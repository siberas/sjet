package de.mogwailabs.mlet;

public interface MogwaiLabsPayloadMBean {
	
	public String runCMD(String passwd, String cmd);
	public String runJS(String passwd, String js);
	public boolean changePassword(String oldPass, String newPass);
	
}
