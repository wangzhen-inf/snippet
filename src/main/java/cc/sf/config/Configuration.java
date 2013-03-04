package cc.sf.config;

import java.io.Serializable;

public interface Configuration extends Serializable{

	public Object getValue(Object key);
}
