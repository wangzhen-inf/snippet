package cc.sf.experiment;

import com.lmax.disruptor.EventFactory;

/**
 * Created with IntelliJ IDEA.
 * User: wangzhen
 * Date: 3/4/13
 * Time: 9:05 AM
 * To change this template use File | Settings | File Templates.
 */
public class TicketEventFactory implements EventFactory<TicketEvent> {
    public static final TicketEventFactory INSTANCE = new TicketEventFactory();

    @Override
    public TicketEvent newInstance() {
        return new TicketEvent();  //To change body of implemented methods use File | Settings | File Templates.
    }
}
