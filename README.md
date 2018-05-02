# RIDE SHARING

This project evaluates ride-sharing algorithms on spatio-temporal data. The orginal dataset is obtained from NYC government website. The orginal dataset consisted of nearly 9 million trips in New York City, which is cut down to 157.3 thousand after cleaning the dataset considering various assumptions. 

The ojective of this project is to merge trips that maximizes the total benefit (includes social preferences and distance saved). 

Orginal Dataset: http://www.nyc.gov/html/tlc/html/about/trip_record_data.shtml

### **DATA PREPROCESSING**
----
1. Removed all trips that orginated out of JFK
2. Removed trips with missing data values (latitude, longitude missing).
3. Calculated trip duration for each trip in dataset.
4. Calculated the delay as 20% of the trip duration
5. Randomly assigned social preferences for each trip.
6. Calculated the speed factor.
7. Mapped the destination of each trip to nearest intersection.


### **PREREQUISITES**
----
- Python version 2
- MySQL
- networkx (`pip install networkx`)
- MySQLdb (`pip install MySQL-python`)

### **STEPS TO RUN**
----
1. Install MySQL and all the prerequisites.
2. Import the dataset trips into database using `queries.sql` file.
3. Set the username and password of the database in `dbconfig.py`.
3. Run `ride_share.py` using the command `python ride_share.py`

To Run using the precomputed intersection to intersection data

1. Import `final_int_int.csv` into the database.
2. Make following change in `ride_share.py`
 At line #246 change  
```check(conn, all_trips[a], all_trips[b], G, benefit_G, delay)```  
to  
```check(conn, all_trips[a], all_trips[b], G, benefit_G, delay, false)```
3. Run `ride_share.py` using the command `python ride_share.py`

> Note:  
> Database name: rideshare  
> **Default parameters:**  
> Delay: 20%(Trip duration)   
> Pool size: 5 minutes  
               

