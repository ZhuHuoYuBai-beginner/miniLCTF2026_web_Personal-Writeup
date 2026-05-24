import org.apache.fury.Fury;
import org.apache.fury.config.Language;

import java.util.Base64;

public class GenData {
    public static void main(String[] args) {
        Fury fury = Fury.builder()
                .withLanguage(Language.JAVA)
                .requireClassRegistration(false)
                .withRefTracking(true)
                .build();

        byte[] payload = fury.serialize("hello");
        String data = Base64.getEncoder().encodeToString(payload);

        System.out.println(data);
        System.out.println("length = " + data.length());
    }
}