package bc;

public class Message {
    private String id;
    private String userId;
    private String content;
    private int likes;
    private long timestamp;
    private String chatroom; // 新增字段

    // 构造函数、getter和setter方法
    public Message(String id, String content, String userId, int likes, long timestamp, String chatroom) {
        this.id = id;
        this.content = content;
        this.userId = userId;
        this.likes = likes;
        this.timestamp = timestamp;
        this.chatroom = chatroom;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getUserId() {
        return userId;
    }

    public void setUserId(String userId) {
        this.userId = userId;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }

    public int getLikes() {
        return likes;
    }

    public void setLikes(int likes) {
        this.likes = likes;
    }

    public long getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(long timestamp) {
        this.timestamp = timestamp;
    }

    public String getChatroom() {
        return chatroom;
    }

    public void setChatroom(String chatroom) {
        this.chatroom = chatroom;
    }

}
