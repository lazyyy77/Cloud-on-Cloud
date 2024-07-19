package bc;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.List;
import java.util.Map;
import java.util.logging.Logger;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;

public class OpenAIClient {
    private static final String API_URL = "https://api.openai.com/v1/chat/completions"; // 更新为 chat/completions 端点
    private static final String API_KEY = System.getenv("API_URL");
    private static final Logger LOGGER = Logger.getLogger(OpenAIClient.class.getName());

    public String analyzeMessage(String message) throws IOException, InterruptedException {
        HttpClient client = HttpClient.newHttpClient();
        ObjectMapper objectMapper = new ObjectMapper();

        // 解码消息内容
        String decodedMessage = URLDecoder.decode(message, StandardCharsets.UTF_8);

        String prompt = "分析以下消息以确定其是否包含不宜放上网络的信息，例如脏话、暴力因素、色情因素、政治敏感话题、攻击性话语等。如果合适，则返回“compliant”。如果不符合要求，则返回“not compliant”。另外，确定该消息是否与讨论天气相关，如果不相关，请添加“not relative”。（若是链接则默认compliant）信息：" + decodedMessage;
        String requestBody = objectMapper.writeValueAsString(Map.of(
                "model", "gpt-3.5-turbo", // 使用支持的模型
                "messages", List.of(Map.of("role", "user", "content", prompt))
        ));

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(API_URL))
                .header("Content-Type", "application/json")
                .header("Authorization", "Bearer " + API_KEY)
                .POST(HttpRequest.BodyPublishers.ofString(requestBody))
                .build();

        LOGGER.info("Sending request to OpenAI API: " + requestBody);

        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());

        LOGGER.info("Received response from OpenAI API: " + response.body());

        if (response.statusCode() != 200) {
            throw new IOException("Failed to get response from OpenAI: " + response.body());
        }

        Map<String, Object> result = objectMapper.readValue(response.body(), Map.class);
        List<Map<String, Object>> choices = (List<Map<String, Object>>) result.get("choices");

        if (choices == null || choices.isEmpty()) {
            throw new IOException("Invalid response format from OpenAI: " + response.body());
        }

        Map<String, Object> messageContent = (Map<String, Object>) choices.get(0).get("message");
        String completion = (String) messageContent.get("content");
        if (completion == null) {
            throw new IOException("Completion text is null in OpenAI response: " + response.body());
        }

        LOGGER.info("Parsed completion: " + completion.trim());

        return completion.trim();
    }
}
