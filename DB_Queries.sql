create database rideshare;

use rideshare;

CREATE TABLE `trips` (
  `sno` varchar(10) DEFAULT NULL,
  `id` varchar(15) DEFAULT NULL,
  `maplat` DECIMAL(6,4) DEFAULT NULL,
  `maplong` DECIMAL(6,4) DEFAULT NULL,
  `stdate` varchar(15) DEFAULT NULL,
  `stime` varchar(20) DEFAULT NULL,
  `enddate` varchar(15) DEFAULT NULL,
  `etime` varchar(20) DEFAULT NULL,
  `pcount` varchar(10) DEFAULT NULL,
  `distance` varchar(10) DEFAULT NULL,
  `plo` DECIMAL(6,4) DEFAULT NULL,
  `pla` DECIMAL(6,4) DEFAULT NULL,
  `dlo` DECIMAL(6,4) DEFAULT NULL,
  `dla` DECIMAL(6,4) DEFAULT NULL,
  `delay` varchar(10) DEFAULT NULL,
  `gender` varchar(2) DEFAULT NULL,
  `gp` varchar(2) DEFAULT NULL,
  `occupation` varchar(10) DEFAULT NULL,
  `op` varchar(10) DEFAULT NULL,
  `smoker` varchar(10) DEFAULT NULL,
  `sp` varchar(5) DEFAULT NULL,
  `maritalstatus` varchar(4) DEFAULT NULL,
  `mp` varchar(4) DEFAULT NULL,
  `lang` varchar(50) DEFAULT NULL,
  `lp` varchar(10) DEFAULT NULL,
  `duration` varchar(7) DEFAULT NULL,
  `speed` varchar(10) DEFAULT NULL,
  `timediff` varchar(20) DEFAULT NULL,
  `dur` varchar(7) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

LOAD DATA  LOCAL INFILE  '/Users/abdulmuqeethmohammed/Documents/datasettrip.csv'
INTO TABLE trips
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

Create table delayconstraint (
id varchar(20),
lat DECIMAL(6,4),
lon DECIMAL(6,4),
distance varchar(20),
ttime varchar(20) );

LOAD DATA  LOCAL INFILE  '/Users/abdulmuqeethmohammed/Documents/Final_JFK_Intersection.csv'
INTO TABLE delayconstraint
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 0 ROWS;

CREATE TABLE `lookup` (
  `trip_a_id` int(11) DEFAULT NULL,
  `trip_b_id` int(11) DEFAULT NULL,
  `lat` decimal(6,4) DEFAULT NULL,
  `lng` decimal(6,4) DEFAULT NULL,
  `distance` varchar(10) DEFAULT NULL,
  `duration` varchar(7) DEFAULT NULL,
  KEY `IX_int` (`trip_a_id`,`trip_b_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8

LOAD DATA LOCAL INFILE '/Users/sndpkiran/Downloads/final_int_int.csv' 
INTO TABLE lookup
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n' 
IGNORE 0 ROWS;



