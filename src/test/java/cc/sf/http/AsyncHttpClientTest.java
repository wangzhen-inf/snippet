package cc.sf.http;

import java.io.IOException;
import java.util.concurrent.ExecutionException;

import com.ning.http.client.*;
import com.ning.http.client.providers.netty.NettyAsyncHttpProvider;
import org.junit.Before;
import org.junit.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AsyncHttpClientTest {

    AsyncHttpClient asyncHttpClient;
    Logger logger = LoggerFactory.getLogger(this.getClass());

    @Before
    public void init() {
        AsyncHttpClientConfig config = new AsyncHttpClientConfig.Builder().setUseRawUrl(false).build();
        asyncHttpClient = new AsyncHttpClient(new NettyAsyncHttpProvider(config));
    }

    @Test
    public void test() throws IOException {
        try {
            String url = "https://localhost:9443/callout";
            url = "https://localhost:8000/";
            url = "https://localhost:7071/callout/newProduct?name=wz&subscriptionid=132413421342";
            Request request = new RequestBuilder().setMethod("POST").setUrl(url).build();
            ListenableFuture<String> future = asyncHttpClient.prepareRequest(request).setBody("subscriptionid=QKDOSASDGJAS-SGFLKER").execute(new AsyncCompletionHandler<String>() {

                @Override
                public String onCompleted(Response response) throws Exception {
                    logger.debug("onCompleted: " + response.getResponseBody());
                    return response.getResponseBody();
                }

                @Override
                public STATE onStatusReceived(HttpResponseStatus status) throws Exception {
                    logger.debug("onStatusReceived: " + status.getStatusText());
                    return super.onStatusReceived(status);
                }

                @Override
                public STATE onBodyPartReceived(HttpResponseBodyPart content) throws Exception {
                    logger.debug("onBodyPartReceived");
                    return super.onBodyPartReceived(content);
                }

                @Override
                public STATE onHeadersReceived(HttpResponseHeaders headers) throws Exception {
                    logger.debug("onHeadersReceived");
                    return super.onHeadersReceived(headers);
                }

                @Override
                public void onThrowable(Throwable t) {
                    logger.debug("onThrowable" , t);
                    super.onThrowable(t);
                }

                @Override
                public STATE onHeaderWriteCompleted() {
                    logger.debug("onHeaderWriteCompleted");
                    return super.onHeaderWriteCompleted();
                }

                @Override
                public STATE onContentWriteCompleted() {
                    logger.debug("onContentWriteCompleted");
                    return super.onContentWriteCompleted();
                }

                @Override
                public STATE onContentWriteProgress(long amount, long current, long total) {
                    logger.debug("onContentWriteProgress");
                    return super.onContentWriteProgress(amount, current, total);
                }


            });
            future.get();
        }
        catch (IOException e) {
            logger.error("IO Exception happens",e);
        }
        catch (InterruptedException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        catch (ExecutionException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }

    }

}
