package cc.sf.concurrency;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


public final class Asynchronizer {
	private static int DEFAULT_THREAD_NUM = 4;
	public static AsynWorkLifeCycleListener NULL_LISTENER = new AsynWorkLifeCycleListener() {
		
		public void beforeRun(AsynWorkLifeCycleEvent event) {
		}
		
		public void afterRun(AsynWorkLifeCycleEvent event) {
		}
	};
//	public static AsynWorkLifeCycleListener HIBERNATE_SESSION_LISTENER = new HibernateSessionAsynWorkListener(); 
	
	private ExecutorService executorService;
	private final int threadNum;
	private final CountDownLatch poisonLatch;
	private final CountDownLatch allOverLatch;
	private final List<AsynWorkLifeCycleListener> listeners;
	private final AtomicInteger success;
	private final AtomicInteger fail;
	private final AtomicInteger total;
	
	private Logger logger = LoggerFactory.getLogger(Asynchronizer.class);
	
	public Asynchronizer(){
		this(DEFAULT_THREAD_NUM , NULL_LISTENER);
	}
	public Asynchronizer(AsynWorkLifeCycleListener lifeCycleListener){
		this(DEFAULT_THREAD_NUM , lifeCycleListener);
	}
	
	public Asynchronizer(int threadNumber , AsynWorkLifeCycleListener... lifeCycleListeners) {
		this(threadNumber);
		for(AsynWorkLifeCycleListener listener : lifeCycleListeners){
			listeners.add(listener);
		}
	}
	public Asynchronizer(int threadNumber) {
		success = new AtomicInteger(0);
		fail = new AtomicInteger(0);
		total = new AtomicInteger(0);
		threadNum = threadNumber;
		executorService = Executors.newFixedThreadPool(threadNum);
		poisonLatch = new CountDownLatch(threadNum);
		allOverLatch = new CountDownLatch(1);
		listeners = new ArrayList<Asynchronizer.AsynWorkLifeCycleListener>(1);
	}

	public void execute(final Callable work){
		this.execute(work, NULL_LISTENER);
	}
	
	/**
	 * @param work
	 * @param singleListener will be callback in single work
	 */
	public void execute(final Callable work , final AsynWorkLifeCycleListener singleListener){
		total.incrementAndGet();
		executorService.execute(new Runnable() {
			
			public void run() {
				Object result = null;
				try {
					AsynWorkLifeCycleEvent beforeEvent = new AsynWorkLifeCycleEvent();
					fireBeforeRun(beforeEvent);
					singleListener.beforeRun(beforeEvent);
					result = work.call();
				} catch (Exception e) {
					logger.error("Exception happens while running single work",e);
				}finally{
					AsynWorkLifeCycleEvent afterEvent = new AsynWorkLifeCycleEvent();
					afterEvent.setResult(result);
					if(result != null){
						success.incrementAndGet();
					}else{
						fail.incrementAndGet();
					}
					singleListener.afterRun(afterEvent);
					fireAfterRun(afterEvent);
				}
			}

		});
	}
	
	/**
	 * Wait until the all works are over
	 */
	public void waitUntilAllOver(){
		logger.info("Wait until all over");		
		try {
			for(int index = 0 ; index < this.threadNum ; index ++){
				this.executorService.execute(new Poison());
			}
			poisonLatch.await();
		} catch (InterruptedException e) {
			logger.error("The thread has been interrupted when wait for poison.",e);
		}finally{
			executorService.shutdown();
			allOverLatch.countDown();
		}
	}
	
	/**
	 * @param listener will be callback in all works
	 */
	public void addAsynWorkLifeCycleListener(AsynWorkLifeCycleListener listener){
		listeners.add(listener);
	}
	
	public void removeAsynWorkLifeCycleListener(AsynWorkLifeCycleListener listener){
		listeners.remove(listener);
	}
	
	public AtomicInteger getSuccess() {
		return success;
	}
	public AtomicInteger getFail() {
		return fail;
	}
	public AtomicInteger getTotal() {
		return total;
	}
	private void fireBeforeRun(AsynWorkLifeCycleEvent beforeEvent) {
		for (Iterator iterator = listeners.iterator(); iterator.hasNext();) {
			AsynWorkLifeCycleListener listener = (AsynWorkLifeCycleListener) iterator.next();
			listener.beforeRun(beforeEvent);
		}
	}
	
	private void fireAfterRun(AsynWorkLifeCycleEvent afterEvent) {
		for (Iterator iterator = listeners.iterator(); iterator.hasNext();) {
			AsynWorkLifeCycleListener listener = (AsynWorkLifeCycleListener) iterator.next();
			listener.afterRun(afterEvent);
		}
	}
	
	
	private class Poison implements Runnable{

		public void run() {
			poisonLatch.countDown();
			logger.debug("A thread has been poisoned. There are {} poison pills",poisonLatch.getCount());
			try {
				allOverLatch.await();
			} catch (InterruptedException e) {
				logger.error("Poison thread has been interrupted.",e);
			}
		}
		
	}
	
	public class AsynWorkLifeCycleEvent{
		private Object result;
		public AsynWorkLifeCycleEvent() {
		}
		public Object getResult() {
			return result;
		}
		public void setResult(Object result) {
			this.result = result;
		}
	}
	
	public interface AsynWorkLifeCycleListener{
		void beforeRun(AsynWorkLifeCycleEvent event);
		void afterRun(AsynWorkLifeCycleEvent event);
	}
}
