package bc;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Scanner;

public class Database {
    private static final String URL =  "jdbc:mysql://m-svc:3306/weather";//System.getenv("SQL-URL"); 
    private static final String USER = "root"; //System.getenv("SQL-USR"); 
    private static final String PASSWORD = System.getenv("SQL-PWD"); 

    private Connection connection;

    public Connection getConnection(){
        try {
            Class.forName("com.mysql.cj.jdbc.Driver");
            connection = DriverManager.getConnection(URL, USER, PASSWORD);
        } catch (ClassNotFoundException e) {
            System.out.println("bad connection class");
        } catch (SQLException e) {
            System.out.println("bad connection sql");
        }
        System.out.println("good connection");
        return connection;
    }
}
