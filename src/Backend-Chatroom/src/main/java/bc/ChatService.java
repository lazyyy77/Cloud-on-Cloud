package bc;

import java.io.IOException;
import java.sql.SQLException;
import java.util.List;

public class ChatService {

    private MessageDAO messageDAO = new MessageDAO();
    private OpenAIClient openAIClient = new OpenAIClient();

    public void handleNewMessage(Message message) throws IOException, InterruptedException {
        String analysisResult = openAIClient.analyzeMessage(message.getContent());
        if (!isNotCompliant(analysisResult)) { // 仅在消息合规时保存消息
            try {
                messageDAO.saveMessage(message);
            } catch (SQLException e) {
                e.printStackTrace();
            }
        } else {
            throw new IOException("Message is not compliant");
        }
    }

    public void handleLikeMessage(String messageId) {
        try {
            messageDAO.likeMessage(messageId);
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    public void handleUnlikeMessage(String messageId) {
        try {
            messageDAO.unlikeMessage(messageId);
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    public Message getMessage(String messageId) {
        try {
            return messageDAO.getMessage(messageId);
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return null;
    }

    public List<Message> getMessages(String chatroom) {
        try {
            return messageDAO.getMessages(chatroom);
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return null;
    }

    public List<Message> getHighlightedMessages(String chatroom) {
        try {
            List<Message> messages = messageDAO.getHighlightedMessages(chatroom);
            messages.removeIf(message -> {
                try {
                    return isNotRelevantToWeather(message.getContent());
                } catch (IOException | InterruptedException e) {
                    e.printStackTrace();
                    return false;
                }
            });
            return messages;
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return null;
    }

    private boolean isNotCompliant(String analysisResult) {
        return analysisResult.toLowerCase().contains("not compliant");
    }

    public boolean isNotRelevantToWeather(String content) throws IOException, InterruptedException {
        String analysisResult = openAIClient.analyzeMessage(content);
        return analysisResult.toLowerCase().contains("not relevant");
    }
}
