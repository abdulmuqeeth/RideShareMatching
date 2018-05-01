RIDE SHARING
This project evaluates ride-sharing algorithms on spatio-temporal data. The orginal dataset is obtained from NYC government website. The orginal dataset consisted of nearly 9 million trips in New York City, which is cut down to 157.3 thousand after cleaning the dataset considering various assumptions. 

The ojective of this project is to merge trips that maximizes the total benefit (includes social preferences and distance saved). 

Orginal Dataset: http://www.nyc.gov/html/tlc/html/about/trip_record_data.shtml

Data Preprocessing:
1. Removed all trips that orginated out of JFK
2. Removed trips with missing data values (latitude, longitude missing).
3. Calculated trip duration for each trip in dataset.
4. Calculated the delay as 20% of the trip duration
5. Randomly assigned social preferences for each trip.
6. Calculated the speed factor.
7. Mapped the destination of each trip to nearest intersection.


REQUIREMENTS:
	
	Python version 2
	MySQL db
	Internet connectivity

STEPS TO RUN:

1. Install MySQL DB.
2. Import the dataset trips into database using queries.sql file.
3. Set the username and password of the database using dbconfig.py.
3. Run rideshare.py using the command python rideshare.py


Note:
Database name: rideshare
Default parameters: 
Delay: 20%(Trip duration)
Pool size: 5 minutes
               

