Snippet
=======

#Java

##Asynchronizer
We need do some seperately works in parallel.
The Asynchronizer could execute works by servral threads asynchronizely, and blocked until the all works were over.

1. The work don't need initialization.

```java
Asynchronizer asyner = new Asynchronizer();
for(int index = 0 ; index < size ; index ++){
	asyner.execute(new Callable(){
			public Object call() throws Exception {
			//TODO Do Something
			}
		}
	);
}
asyner.waitUntilAllOver();

2. The works need the same initialization.

```java
final static int Thread_Number = 8;
Asynchronizer asyner = new Asynchronizer(Thread_Number, new new AsynWorkLifeCycleListener() {
				
				public void beforeRun(AsynWorkLifeCycleEvent event) {
					
				}
				
				public void afterRun(AsynWorkLifeCycleEvent event) {
					if(event.getResult() != null){
						results.add(event.getResult());
					}
				}
			});
for(int index = 0 ; index < size ; index ++){
	asyner.execute(new Callable(){
			public Object call() throws Exception {
			//TODO Do Something
			}
		}
	);
}
asyner.waitUntilAllOver();

3. The works need different initialization.

```java
Asynchronizer asyner = new Asynchronizer();
for(int index = 0 ; index < size ; index ++){
	asyner.execute(new Callable(){
			public Object call() throws Exception {
			//TODO Do Something
			}
		},new AsynWorkLifeCycleListener() {
				
				public void beforeRun(AsynWorkLifeCycleEvent event) {
					//TODO before the work run	
				}
				
				public void afterRun(AsynWorkLifeCycleEvent event) {
					//TODO after the work complete
				}
		}
	);
}
asyner.waitUntilAllOver();

