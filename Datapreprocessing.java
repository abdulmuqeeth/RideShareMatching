package assignment.main.application;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.sql.DriverManager;
import java.util.*;
import java.time.format.DateTimeFormatter;
import java.time.LocalDate;
import java.time.LocalTime;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.lang.System;

public class Application {

  public static void main(String args[]) throws IOException, SQLException, FileNotFoundException {
    String JDBC_DRIVER = "com.mysql.jdbc.Driver";
    String DB_URL = "jdbc:mysql://localhost:3306/rideshare";

    //  Database credentials
    String USER = "root";
    String PASS = "root";
    String occupation[] = {"business","student","engineer","doctor"};
    String language[] = {"ENG", "HIN", "FRE","SPA", "CHI"};
    int a[]={0,1};
    String array1[] = new String[158136];
    String array2[] = new String[158136];
    String array3[] = new String[158136];
    String array4[] = new String[158136];
    long min[] = new long[158136];


      Connection conn = null;
      Statement stmt = null;
      Statement stmt1= null;
        System.out.println("Connecting to database...");
        conn = DriverManager.getConnection(DB_URL,USER,PASS);
        System.out.println("Creating statement...");
        stmt = conn.createStatement();
      stmt1 = conn.createStatement();
        String sql;
        String query;
        String l;
        ResultSet rs;

          query= "Select stdate,stime,enddate,etime from trips";
          rs=stmt.executeQuery(query);
          //sql= "Update trips set delay =
         // stmt.executeUpdate(sql);

        int j=1;
       while(rs.next()){
          array1[j]= rs.getString("stdate");
          array2[j]= rs.getString("stime");
          array3[j]=rs.getString("enddate");
          array4[j]=rs.getString("etime");
           DateTimeFormatter DateFormatter;

           if(array1[j].length() == 6)
               DateFormatter = DateTimeFormatter.ofPattern("M/d/yy");
           else
               DateFormatter = DateTimeFormatter.ofPattern("M/dd/yy");


           LocalDate startDate = LocalDate.parse(array1[j], DateFormatter);
           if(array3[j].length() == 6)
               DateFormatter = DateTimeFormatter.ofPattern("M/d/yy");
           else
               DateFormatter = DateTimeFormatter.ofPattern("M/dd/yy");
           LocalDate endDate = LocalDate.parse(array3[j], DateFormatter);

           if(array2[j].length()== 7)
               array2[j]= '0'+array2[j];
                       if(array4[j].length()==7)
                           array4[j] = '0' + array4[j];
           DateTimeFormatter TimeFormatter = DateTimeFormatter.ofPattern("kk:mm:ss");
           LocalTime startTime = LocalTime.parse(array2[j], TimeFormatter);
           LocalTime endTime = LocalTime.parse(array4[j], TimeFormatter);


           LocalDateTime start = LocalDateTime.of(startDate, startTime);
           LocalDateTime end = LocalDateTime.of(endDate, endTime);
           
            min[j] = ChronoUnit.MINUTES.between(start, end);
           sql= "Update trips set duration=\""+min[j]+"\" where sno =\""+j+"\"";
           stmt1.executeUpdate(sql);
          j++;




       for(int i=1;i<158138;i++){
          Random rand = new Random();
          int r1= rand.nextInt(4);
          int r2= rand.nextInt(5);
          int r3= rand.nextInt(2);
          int r4= rand.nextInt(2);
         sql= "Update trips set gender=\""+a[r4]+"\" , gp=\""+a[r3]+"\" , occupation=\""+occupation[r1]+"\" , op=\""+occupation[r1]+"\" , smoker=\""+a[r3]+"\" , sp=\""+a[r3]+"\" , maritalstatus=\""+a[r3]+"\" , mp=\""+a[r4]+"\" , lang=\""+language[r2]+"\" , lp=\""+language[r2]+"\" where id =\""+i+"\"";

         stmt.executeUpdate(sql);
        } 


      }
      stmt.close();
       stmt1.close();
      conn.close();
  }
  }

