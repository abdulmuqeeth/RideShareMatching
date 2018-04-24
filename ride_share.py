#!/usr/bin/env python

from dbconfig import *
import MySQLdb
import json
import sys
import requests
import urllib
import time
import networkx as nx

# TODO: Convert units

def make_connection():
    """
    Connect to Database
    """
    conn = MySQLdb.connect(host=hostname, user=username, passwd=password, db=database)

    return conn

def get_trips(conn):
    """
    Load data from preprocessed .csv files
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM trips WHERE stdate='1/1/16'")
    return cur.fetchall()

def get_pools(all_trips, total_trips, pool_size):
    """
    Returns all the trips as a set of 3/5/7 minute pools
    """
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
                if trip_start_minutes >= pool_start_time and trip_start_minutes < pool_start_time + pool_size:
                    pools[i].append(all_trips[j][0])
                    trips_pooled += 1

        pool_start_time += pool_size
        if ((i + 1) % pools_per_hour) == 0:
            prev_hour += 1

    return pools


def check(conn, trip_a, trip_b, G, benefit_G, delay_factor, callApi=True):
    """
    Perform distance and delay constraint checks for trips a and b
    """
    if int(trip_a[8]) + int(trip_b[8]) > 4:
        return
    social_score =0

    if(str(trip_a[3])==str(trip_b[3]) and str(trip_a[2])==str(trip_b[2])):
        benefit = .5;
        social_score = calc_social_score(trip_a, trip_b)[0]
        G.add_edge(trip_a[0], trip_b[0], weight=10000*(benefit*2*.8 + social_score))
        benefit_G.add_edge(trip_a[0], trip_b[0], weight=max(trip_a[9], trip_b[9]))

        return

    # print "Flag: %s" % callApi

    if callApi:
        url_ab = "http://router.project-osrm.org/route/v1/driving/" + str(trip_a[3]) + "," + str(trip_a[2]) + ";" + str(trip_b[3]) + "," + str(trip_b[2]) + "?annotations=distance"
        response  = requests.get(url_ab).text
        json_response = json.loads(response)
        dist_ab = json_response["routes"][0]["distance"] * 0.00062137
        time_ab = json_response["routes"][0]["duration"] / 60.0
        speed_ab = dist_ab / time_ab

        url_ba = "http://router.project-osrm.org/route/v1/driving/" + str(trip_b[3]) + "," + str(trip_b[2]) + ";" + str(trip_a[3]) + "," + str(trip_a[2]) + "?annotations=distance"
        response  = requests.get(url_ba).text
        json_response = json.loads(response)
        dist_ba = json_response["routes"][0]["distance"] * 0.00062137
        time_ba = json_response["routes"][0]["duration"] / 60.0
        speed_ba = dist_ba / time_ba

        ha_hb = float(trip_a[9]) + float(trip_b[9])
        ha_ab = float(trip_a[9]) + dist_ab
        hb_ba = float(trip_b[9]) + dist_ba
    else:
        cur = conn.cursor()
        q = "SELECT distance, duration from lookup WHERE trip_a_id=" + trip_a[1] + " and trip_b_id=" + trip_b[1]
        # print q
        cur.execute(q)

        result = cur.fetchall()
        # print "ab"
        # print result
        ha_hb = float(trip_a[9]) + float(trip_b[9])
        dist_ab = float(result[0][0])
        print "ab"
        print dist_ab
        time_ab = float(result[0][1]) / 60.0
        ha_ab = float(trip_a[9]) + dist_ab
        speed_ab = dist_ab / time_ab

        cur = conn.cursor()
        q = "SELECT distance, duration from lookup WHERE trip_a_id=" + trip_b[1] + " and trip_b_id=" + trip_a[1]
        cur.execute(q)
        result = cur.fetchall()
        # print "ba"
        # print result
        dist_ba = float(result[0][0])
        print "ba"
        print dist_ba
        time_ba = float(result[0][1]) / 60.0
        hb_ba = float(trip_b[9]) + dist_ba
        speed_ba = dist_ba / time_ba

    cur = conn.cursor()
    lat = str(trip_a[2])
    lon = str(trip_a[3])

    q = "SELECT distance, ttime from delayconstraint where lat = " + lat + " and lon = " + lon
    cur.execute(q)
    result = cur.fetchall()
    dist_ha_osrm = float(result[0][0]) * 0.00062137
    time_ha_osrm = float(result[0][1]) / 60.0
    speed_ha_osrm = dist_ha_osrm / time_ha_osrm
    speed_ha_ds = float(trip_a[26])

    lat = str(trip_b[2])
    lon = str(trip_b[3])
    q = "SELECT distance, ttime from delayconstraint where lat = " + lat + " and lon = " + lon
    cur.execute(q)
    result = cur.fetchall()
    dist_hb_osrm = float(result[0][0]) * 0.00062137
    time_hb_osrm = float(result[0][1]) / 60.0
    speed_hb_osrm = dist_hb_osrm / time_hb_osrm
    speed_hb_ds = float(trip_b[26])

    speed_max_ab = max(speed_ab, speed_ba)
    factor = ((speed_ha_ds / speed_ha_osrm) + (speed_hb_ds / speed_hb_osrm)) / 2.0

    flag_ab = 0
    flag_ba = 0
    benefit_ab = 0
    benefit_ba = 0
    arri_time_a = float(trip_a[28])
    arri_time_b = float(trip_b[28])

    if ha_hb > ha_ab:
        drop_time = arri_time_a + (dist_ab / (factor * speed_max_ab))
        if drop_time <= arri_time_b + delay_factor * arri_time_b:
            flag_ab = 1
            benefit_ab = (ha_hb - ha_ab) / ha_hb

    if ha_hb > hb_ba:
        drop_time = arri_time_b + (dist_ba / (factor * speed_max_ab))
        if drop_time <= arri_time_a + delay_factor * arri_time_a:
            flag_ba = 1
            benefit_ba = (ha_hb - hb_ba) / ha_hb

    benefit = max(benefit_ab, benefit_ba)

    social_score = calc_social_score(trip_a, trip_b)[0];

    if(benefit !=0.0):
        G.add_edge(trip_a[0], trip_b[0], weight=10000*(benefit*2*.8) + social_score)
        benefit_G.add_edge(trip_a[0], trip_b[0], weight=(benefit*ha_hb))


def calc_social_score(trip_a, trip_b):
    """
    Calculate the social score for trips a and b
    """
    social_score = 0.0
    matched_a = 0
    matched_b = 0

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

    social_score = 0.1 * (matched_a / 5.0) + 0.1 * (matched_b / 5.0)
    return [social_score, matched_a, matched_b]

def calculate_savings(trip_a, trip_b, benefit_G):
    return float(benefit_G[str(trip_a[0])][str(trip_b[0])]['weight'])


def main():
    """
    Main function
    """
    conn = make_connection()

    social_pref_count = [0, 0, 0, 0, 0, 0]

    delay = 0.2

    all_trips = get_trips(conn)
    total_trips = len(all_trips)
    pools = get_pools(all_trips, total_trips, 5)

    distance_saved = 0.0
    trips_saved = 0
    start_run_time = time.time()

    for pool in range(250):
        G = nx.Graph()
        benefit_G = nx.Graph()
        for i in range(len(pools[pool])):
            for j in range(i + 1, len(pools[pool])):
                # print pool
                a = int(pools[pool][i]) - int(all_trips[0][0])
                b = int(pools[pool][j]) - int(all_trips[0][0])

                check(conn, all_trips[a], all_trips[b], G, benefit_G, delay)

        maximum_matching = list(nx.max_weight_matching(G, maxcardinality=True, weight='weight'))

        # calculate distance and trips saved
        total_combined_trips = len(maximum_matching)
        print "combined: "
        print total_combined_trips
        trips_saved += (total_combined_trips * 2)
        print "Trips Saved so far: %s" % trips_saved

        for k in range(total_combined_trips):
            trip_a_id = int(maximum_matching[k][0]) - int(all_trips[0][0])
            trip_b_id = int(maximum_matching[k][1]) - int(all_trips[0][0])

            trip_a = all_trips[trip_a_id]
            trip_b = all_trips[trip_b_id]
            distance_saved += calculate_savings(trip_a, trip_b, benefit_G)

            ret = calc_social_score(trip_a, trip_b)
            if ret[1] == 0:
                social_pref_count[0] += 1
            elif ret[1] == 1:
                social_pref_count[1] += 1
            elif ret[1] == 2:
                social_pref_count[2] += 1
            elif ret[1] == 3:
                social_pref_count[3] += 1
            elif ret[1] == 4:
                social_pref_count[4] += 1
            elif ret[1] == 5:
                social_pref_count[5] += 1

            if ret[2] == 0:
                social_pref_count[0] += 1
            elif ret[2] == 1:
                social_pref_count[1] += 1
            elif ret[2] == 2:
                social_pref_count[2] += 1
            elif ret[2] == 3:
                social_pref_count[3] += 1
            elif ret[2] == 4:
                social_pref_count[4] += 1
            elif ret[2] == 5:
                social_pref_count[5] += 1

    print "Pool #", pool
    print "Total Trips: ", len(all_trips)
    print "trips saved: ", trips_saved

    print "Percentage trips saved: %s" % ((trips_saved / float(len(all_trips))) * 100)

    print "Total Savings", distance_saved

    print "Social Preferences: ", social_pref_count
    print "Running time of pooling: %s" % (time.time() - start_run_time)

    conn.close()

if __name__ == "__main__":
    main()
