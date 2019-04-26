package de.mogwailabs.MogwaiLabsMJET;

public interface MogwaiLabsPayloadMBean {
    
    public abstract String runCMD(String passwd, String cmd);
    public abstract String runJS(String passwd, String js);
    public abstract boolean changePassword(String oldPass, String newPass);
    
}

