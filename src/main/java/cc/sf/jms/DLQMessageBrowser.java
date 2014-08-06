package cc.sf.jms;

import java.sql.Timestamp;
import java.util.Enumeration;

import javax.jms.*;

import org.apache.activemq.ActiveMQConnection;
import org.apache.activemq.ActiveMQConnectionFactory;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.Configuration;

/**
 * Created with IntelliJ IDEA.
 * User: zhenwang
 * Date: 3/13/14
 * Time: 8:56 AM
 * To change this template use File | Settings | File Templates.
 */
@Configuration
public class DLQMessageBrowser {
    public static void main(String[] args){
        Logger logger = LoggerFactory.getLogger("DLQ Message Browser");
        ActiveMQConnectionFactory connectionFactory = new ActiveMQConnectionFactory();

        try {
            ActiveMQConnection connection = (ActiveMQConnection) connectionFactory.createConnection();
            connection.start();
            Session session = connection.createSession(true, Session.AUTO_ACKNOWLEDGE);
            Queue queue = session.createQueue("wz.test.queue");
            QueueBrowser browser = session.createBrowser(queue);
            Enumeration enumeration = browser.getEnumeration();
            while (enumeration.hasMoreElements()){
                Message msg = (Message) enumeration.nextElement();
                logger.info("Get message {}" , new Timestamp(msg.getJMSTimestamp()));
            }
            connection.close();
        } catch (JMSException e) {
            e.printStackTrace();  //To change body of catch statement use File | Settings | File Templates.
        }
    }
}
