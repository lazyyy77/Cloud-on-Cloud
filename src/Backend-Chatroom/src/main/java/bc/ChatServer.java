package bc;

import org.java_websocket.server.WebSocketServer;
import org.java_websocket.WebSocket;
import org.java_websocket.handshake.ClientHandshake;

import java.net.InetSocketAddress;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class ChatServer extends WebSocketServer {

    private ChatService chatService = new ChatService();
    private Map<WebSocket, String> connections = new ConcurrentHashMap<>();

    public static void main(String[] args) {
        String host = "0.0.0.0";
        int port = 8887;
        ChatServer server = new ChatServer(new InetSocketAddress(host, port));
        server.start();
    }

    public ChatServer(InetSocketAddress address) {
        super(address);
    }

    @Override
    public void onOpen(WebSocket conn, ClientHandshake handshake) {
        System.out.println("New connection: " + conn.getRemoteSocketAddress());

        // When a new connection is established, no chatroom is initially selected,
        // so no highlighted messages are sent here. Once the user selects a chatroom,
        // highlighted messages will be sent in the onMessage method.

        broadcastOnlineUsers();
    }

    @Override
    public void onClose(WebSocket conn, int code, String reason, boolean remote) {
        System.out.println("Closed connection: " + conn.getRemoteSocketAddress());
        connections.remove(conn);
        broadcastOnlineUsers();
    }

    @Override
    public void onMessage(WebSocket conn, String message) {
        System.out.println("Received message: " + message);

        if (message.startsWith("CHATROOM:")) {
            String chatroom = message.substring(9);
            connections.put(conn, chatroom);
            List<Message> messages = chatService.getMessages(chatroom);
            for (Message msg : messages) {
                conn.send("NEW:" + msg.getId() + ":" + msg.getUserId() + ":" + msg.getContent() + ":" + msg.getLikes() + ":" + msg.getTimestamp());
            }
            // Load and send highlighted messages for the selected chatroom
            List<Message> highlightedMessages = chatService.getHighlightedMessages(chatroom);
            for (Message msg : highlightedMessages) {
                conn.send("HIGHLIGHT:" + msg.getId() + ":" + msg.getContent() + ":" + msg.getLikes() + ":" + msg.getTimestamp());
            }
            broadcastOnlineUsers();
        } else if (message.startsWith("LIKE:")) {
            String messageId = message.substring(5);
            chatService.handleLikeMessage(messageId);
            broadcastMessageUpdate(messageId);
        } else if (message.startsWith("UNLIKE:")) {
            String messageId = message.substring(7);
            chatService.handleUnlikeMessage(messageId);
            broadcastMessageUpdate(messageId);
        } else {
            String[] parts = message.split(":", 4);
            String messageId = parts[0];
            String userId = parts[1];
            String chatroom = parts[2];
            String content = parts[3];
            Message newMessage = new Message(messageId, content, userId, 0, System.currentTimeMillis(), chatroom);
            try {
                chatService.handleNewMessage(newMessage);
                broadcastNewMessage(newMessage);
            } catch (IOException | InterruptedException e) {
                conn.send("ERROR:Message is not compliant or relevant to weather");
                e.printStackTrace();
            }
        }
    }

    @Override
    public void onError(WebSocket conn, Exception ex) {
        ex.printStackTrace();
    }

    @Override
    public void onStart() {
        System.out.println("Server started!");
    }

    private void broadcastOnlineUsers() {
        int onlineUsers = connections.size();
        for (WebSocket connection : connections.keySet()) {
            connection.send("ONLINE_USERS:" + onlineUsers);
        }
    }

    private void broadcastMessageUpdate(String messageId) {
        Message updatedMessage = chatService.getMessage(messageId);
        if (updatedMessage != null) {
            broadcast("UPDATE:" + updatedMessage.getId() + ":" + updatedMessage.getLikes());
        }
    }

    private void broadcastNewMessage(Message newMessage) {
        broadcast("NEW:" + newMessage.getId() + ":" + newMessage.getUserId() + ":" + newMessage.getContent() + ":" + newMessage.getLikes() + ":" + newMessage.getTimestamp());
    }

}
