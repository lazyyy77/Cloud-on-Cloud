package bc;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;

public class MessageDAO {

    public void saveMessage(Message message) throws SQLException {
        String query = "INSERT INTO weather_messages (id, userId, content, likes, timestamp, chatroom) VALUES (?, ?, ?, ?, ?, ?)";
        Database db = new Database();
        try (Connection connection = db.getConnection();
            PreparedStatement statement = connection.prepareStatement(query)) {
            statement.setString(1, message.getId());
            statement.setString(2, message.getUserId());
            statement.setString(3, message.getContent());
            statement.setInt(4, message.getLikes());
            statement.setLong(5, message.getTimestamp());
            statement.setString(6, message.getChatroom());
            statement.executeUpdate();
        }
    }

    public void likeMessage(String messageId) throws SQLException {
        String query = "UPDATE weather_messages SET likes = likes + 1 WHERE id = ?";
        Database db = new Database();
        try (Connection connection = db.getConnection();
            PreparedStatement statement = connection.prepareStatement(query)) {
            statement.setString(1, messageId);
            statement.executeUpdate();
        }
    }

    public void unlikeMessage(String messageId) throws SQLException {
        String query = "UPDATE weather_messages SET likes = likes - 1 WHERE id = ?";
        Database db = new Database();
        try (Connection connection = db.getConnection();
            PreparedStatement statement = connection.prepareStatement(query)) {
            statement.setString(1, messageId);
            statement.executeUpdate();
        }
    }

    public Message getMessage(String messageId) throws SQLException {
        String query = "SELECT * FROM mweather_messages WHERE id = ?";
        Database db = new Database();
        try (Connection connection = db.getConnection();
            PreparedStatement statement = connection.prepareStatement(query)) {
            statement.setString(1, messageId);
            ResultSet resultSet = statement.executeQuery();
            if (resultSet.next()) {
                return new Message(
                        resultSet.getString("id"),
                        resultSet.getString("content"),
                        resultSet.getString("userId"),
                        resultSet.getInt("likes"),
                        resultSet.getLong("timestamp"),
                        resultSet.getString("chatroom")
                );
            }
        }
        return null;
    }

    public List<Message> getMessages(String chatroom) throws SQLException {
        String query = "SELECT * FROM weather_messages WHERE chatroom = ?";
        List<Message> messages = new ArrayList<>();
        Database db = new Database();
        try (Connection connection = db.getConnection();
            PreparedStatement statement = connection.prepareStatement(query)) {
            statement.setString(1, chatroom);
            ResultSet resultSet = statement.executeQuery();
            while (resultSet.next()) {
                messages.add(new Message(
                        resultSet.getString("id"),
                        resultSet.getString("content"),
                        resultSet.getString("userId"),
                        resultSet.getInt("likes"),
                        resultSet.getLong("timestamp"),
                        resultSet.getString("chatroom")
                ));
            }
        }
        return messages;
    }

    public List<Message> getHighlightedMessages(String chatroom) throws SQLException {
        String query = "SELECT * FROM weather_messages WHERE likes >= 5 AND chatroom = ?";
        List<Message> messages = new ArrayList<>();
        Database db = new Database();
        try (Connection connection = db.getConnection();
            PreparedStatement statement = connection.prepareStatement(query)) {
            statement.setString(1, chatroom);
            ResultSet resultSet = statement.executeQuery();
            while (resultSet.next()) {
                messages.add(new Message(
                        resultSet.getString("id"),
                        resultSet.getString("content"),
                        resultSet.getString("userId"),
                        resultSet.getInt("likes"),
                        resultSet.getLong("timestamp"),
                        resultSet.getString("chatroom")
                ));
            }
        }
        return messages;
    }

    public void deleteOldMessages() throws SQLException {
        long currentTime = System.currentTimeMillis();
        long oneHourAgo = currentTime - 3600000; // 一小时的毫秒数
        String query = "DELETE FROM weather_messages WHERE likes < 5 AND timestamp < ?";
        Database db = new Database();
        try (Connection connection = db.getConnection();
             PreparedStatement statement = connection.prepareStatement(query)) {
            statement.setLong(1, oneHourAgo);
            statement.executeUpdate();
        }
    }
}
