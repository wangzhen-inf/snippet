package cc.sf.experiment;

import com.lmax.disruptor.*;
import com.lmax.disruptor.dsl.Disruptor;
import com.lmax.disruptor.dsl.ProducerType;
import org.junit.Before;
import org.junit.Test;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import static org.junit.Assert.assertEquals;

public class DisruptorExperiment
{
    private long _journalistCount = 0L;
    // 用来验证日志线程看到的最后一个事件值
    private int _lastEventValue = 0;
    // 用来验证日志线程看到了所有生产线程产生的事件
    private int _journalistValueSum = 0;
    // 将事件保存在硬盘里的书记员线程
    final EventHandler<TicketEvent> _journalist =
            new EventHandler<TicketEvent>() {
                public void onEvent(final TicketEvent event,
                                    final long sequence,
                                    final boolean endOfBatch) throws Exception {
                    _journalistCount++;
                    _lastEventValue = event.getValue();
                    _journalistValueSum += _lastEventValue;
                    System.out.println("Journalist " + _lastEventValue);
                }
            };

    private long _replicatorCount = 0L;
    // 用来验证备份线程看到了所有生产线程产生的事件
    private int _replicatorValueSum = 0;
    // 将事件发送到备份服务器保存的备份线程
    final EventHandler<TicketEvent> _replicator =
            new EventHandler<TicketEvent>() {
                public void onEvent(final TicketEvent event,
                                    final long sequence,
                                    final boolean endOfBatch) throws Exception {
                    _replicatorCount++;
                    _replicatorValueSum += event.getValue();
                    System.out.println("Replicator " + event.getValue());
                }
            };

    final EventHandler<TicketEvent> _eventProcessor =
            new EventHandler<TicketEvent>() {
                public void onEvent(final TicketEvent event,
                                    final long sequence,
                                    final boolean endOfBatch) throws Exception {
                    System.out.println("[processor] " + new Long(sequence).toString());
                }
            };

    private int RING_SIZE = 128;
    private final ExecutorService EXECUTOR =
            Executors.newCachedThreadPool();

    @Before
    public void setUp() throws Exception {
        _journalistCount = _replicatorCount = _lastEventValue = 0;
    }

    @Test
    public void testDisruptorDSL() throws Exception {
        Disruptor<TicketEvent> disruptor =
                new Disruptor<TicketEvent>
                        (
                                TicketEventFactory.INSTANCE,
                                RING_SIZE,
                                EXECUTOR,
                                ProducerType.SINGLE,
                                new BlockingWaitStrategy()
                        );
        // 注册日志和备份线程
        disruptor.handleEventsWith(_journalist);
        disruptor.handleEventsWith(_replicator);
        disruptor.after(_journalist,_replicator).handleEventsWith(_eventProcessor);

        // 启动disruptor,等待publish事件
        RingBuffer<TicketEvent> ringBuffer = disruptor.start();

        // 添加一些事件
        for ( int i = 0; i < RING_SIZE; ++i ) {
            long sequence = ringBuffer.next();
            TicketEvent event = ringBuffer.getPreallocated(sequence);
            event.setValue(i);
            ringBuffer.publish(sequence);
        }

        Thread.sleep(1000);
        assertEquals(RING_SIZE, _journalistCount);
        assertEquals(RING_SIZE, _replicatorCount);

        // 对于日志和备份线程,应该是串行执行每一个事件的
        assertEquals(RING_SIZE - 1, _lastEventValue);

        // 还有一个问题,就是确认所有事件是否真的已经处理了？
        int expected = (0 + RING_SIZE - 1) * RING_SIZE / 2;
        assertEquals(expected, _journalistValueSum);
        assertEquals(expected, _replicatorValueSum);
    }
}