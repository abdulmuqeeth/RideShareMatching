#!/usr/bin/env python

from dbconfig import *
import MySQLdb
import json
import sys

"""
TODO: Convert units
"""

"""
Connect to Database
"""
def make_connection():
    conn = MySQLdb.connect(host=hostname, user=username, passwd=password, db=database)

    return conn

"""
Load data from preprocessed .csv files
"""
def get_trips(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM trips WHERE stdate='1/25/16'")
    return cur.fetchall()

"""
Returns all the trips as a set of 3/5/7 minute pools
"""
def get_pools(all_trips, total_trips, pool_size):
    pools_per_day = (24 * 60) / pool_size
    pools_per_hour = 60 / pool_size
    pools = [ [] for i  in range(pools_per_day)]

    pool_start_time  = 0
    prev_hour = 0
    trips_pooled = 0
    for i in range(pools_per_day):
        if pool_start_time >= 60:
            pool_start_time = 0

        for j in range(trips_pooled, total_trips):
            trip_start_minutes = int(all_trips[j][5].split(":")[1])
            trip_start_hour = int(all_trips[j][5].split(":")[0])

            if prev_hour == trip_start_hour:
                # if i == 12:
                #     print prev_hour, "==", trip_start_hour, trip_start_minutes, "<",  pool_start_time + pool_size
                if trip_start_minutes >= pool_start_time and trip_start_minutes < pool_start_time + pool_size:
                    pools[i].append(all_trips[j][0])
                    trips_pooled += 1

        # break
        pool_start_time += pool_size
        if ((i + 1) % pools_per_hour) == 0:
            prev_hour += 1

    return pools

"""
Perform distance and delay constraint checks for trips a and b
"""
def check(conn, trip_a, trip_b):
    # ha_hb = trip_a[9] + trip_b[9]
    # url_ab = "http://router.project-osrm.org/route/v1/driving/" + trip_a[3] + "," + trip_a[2] + ";" + trip_b[3] + "," + trip_b[2] + "?annotations=distance"
    # response  = requests.get(url_ab).text
    # json_response = json.loads(response)
    #
    # url_ba = "http://router.project-osrm.org/route/v1/driving/" + trip_b[3] + "," + trip_b[2] + ";" + trip_a[3] + "," + trip_a[2] + "?annotations=distance"
    # dist_ab =
    # dist_ba =
    # ha_ab =
    # hb_ba =
    # if ha_hb > ha_ab or ha_hb > hb_ba:
    #
    # else:
    pass

"""
Calculate the social score for trips a and b
"""
def calc_social_score(trip_a, trip_b):
    social_score = 0.0
    matched_a = 0
    matched_b = 0
    # print trip_a[15]

    # preferences matched for a
    if trip_a[16] == trip_b[15]:
        matched_a += 1
    if trip_a[18] == trip_b[17]:
        matched_a += 1
    if trip_a[20] == trip_b[19]:
        matched_a += 1
    if trip_a[22] == trip_b[21]:
        matched_a += 1
    if trip_a[24] == trip_b[23]:
        matched_a += 1

    # preferences matched for b
    if trip_b[16] == trip_a[15]:
        matched_b += 1
    if trip_b[18] == trip_a[17]:
        matched_b += 1
    if trip_b[20] == trip_a[19]:
        matched_b += 1
    if trip_b[22] == trip_a[21]:
        matched_b += 1
    if trip_b[24] == trip_a[23]:
        matched_b += 1

    print matched_a, matched_b

    social_score = 0.1 * (matched_a / 5.0) + 0.1 * (matched_b / 5.0)
    return social_score

"""
Main function
"""
def main():
    conn = make_connection()

    all_trips = get_trips(conn)
    total_trips = len(all_trips)

    pools = get_pools(all_trips, total_trips, 5)

    print calc_social_score(all_trips[0], all_trips[1])

    # for pool in range(len(pools)):
    #     for i in range(len(pools[pool])):
    #         for j in range(i, len(pools[pool])):
    #             a = int(pools[pool][i]) - int(all_trips[0][0])
    #             b = int(pools[pool][j]) - int(all_trips[0][0])
    #             print a, b
    #             check(conn, all_trips[a], all_trips[b])


    conn.close()

if __name__ == "__main__":
    main()
