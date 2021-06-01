package de.mogwailabs.MogwaiLabsMJET;

public interface MogwaiLabsPayloadMBean {
    
    public abstract String runCMD(String passwd, String cmd, String shell);
    public abstract String runJS(String passwd, String js);
    public abstract boolean changePassword(String oldPass, String newPass);
    
}

