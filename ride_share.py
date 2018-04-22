#!/usr/bin/env python

from dbconfig import *
import MySQLdb
import json
import sys
import requests
import urllib
import networkx as nx

G = nx.Graph()

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
    cur.execute("SELECT * FROM trips WHERE stdate='1/23/16'")
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
    social_score =0
    print "coo"
    print trip_a, trip_b

    if(str(trip_a[3])==str(trip_b[3]) and str(trip_a[2])==str(trip_b[2])):
        benefit = .5;
        social_score = calc_social_score(trip_a, trip_b)
        G.add_edge(trip_a[0], trip_b[0], weight=10000*(benefit*2*.8 + social_score))
        return


    url_ab = "http://router.project-osrm.org/route/v1/driving/" + str(trip_a[3]) + "," + str(trip_a[2]) + ";" + str(trip_b[3]) + "," + str(trip_b[2]) + "?annotations=distance"
    response  = requests.get(url_ab).text
    json_response = json.loads(response)
    dist_ab = json_response["routes"][0]["distance"] * 0.00062137
    time_ab = json_response["routes"][0]["duration"] / 60.0
    speed_ab = dist_ab / time_ab

    url_ba = "http://router.project-osrm.org/route/v1/driving/" + str(trip_b[3]) + "," + str(trip_b[2]) + ";" + str(trip_a[3]) + "," + str(trip_a[2]) + "?annotations=distance"
    response  = requests.get(url_ab).text
    json_response = json.loads(response)
    dist_ba = json_response["routes"][0]["distance"] * 0.00062137
    time_ba = json_response["routes"][0]["duration"] / 60.0
    speed_ba = dist_ba / time_ba

    ha_hb = float(trip_a[9]) + float(trip_b[9])
    ha_ab = float(trip_a[9]) + dist_ab
    hb_ba = float(trip_b[9]) + dist_ba

    print("ha-hb {}".format(ha_hb))
    print("ha-ab {}".format(ha_ab))
    print("hb-ba {}".format(hb_ba))


    cur = conn.cursor()
    lat = str(trip_a[2])
    lon = str(trip_a[3])
    #print trip_a
    #print trip_b
    q = "SELECT distance, ttime from delayconstraint where lat = " + lat + " and lon = " + lon
    print q
    cur.execute(q)
    result = cur.fetchall()
    dist_ha_osrm = float(result[0][0]) * 0.00062137
    time_ha_osrm = float(result[0][1]) / 60.0
    speed_ha_osrm = dist_ha_osrm / time_ha_osrm
    speed_ha_ds = float(trip_a[26])

    lat = str(trip_b[2])
    lon = str(trip_b[3])
    q = "SELECT distance, ttime from delayconstraint where lat = " + lat + " and lon = " + lon
    print q
    cur.execute(q)
    result = cur.fetchall()
    dist_hb_osrm = float(result[0][0]) * 0.00062137
    time_hb_osrm = float(result[0][1]) / 60.0
    speed_hb_osrm = dist_hb_osrm / time_hb_osrm
    speed_hb_ds = float(trip_b[26])
    print speed_ha_osrm
    print speed_ha_ds

    speed_max_ab = max(speed_ab, speed_ba)
    factor = ((speed_ha_ds / speed_ha_osrm) + (speed_hb_ds / speed_hb_osrm)) / 2.0

    print 'factor'
    print(factor)
    flag_ab = 0
    flag_ba = 0
    benefit_ab = 0
    benefit_ba = 0


    if ha_hb > ha_ab:
        drop_time = float(trip_a[25]) + (dist_ab / (factor * speed_max_ab))
        if drop_time <= float(trip_b[25]) + float(trip_b[14]):
            flag_ab = 1
            benefit_ab = (ha_hb - ha_ab)/ha_hb

    print 'flag_ab'
    print flag_ab
    print 'benefit_ab'
    print benefit_ab

    if ha_hb > hb_ba:
        drop_time = float(trip_b[25]) + (dist_ba / (factor * speed_max_ab))
        if drop_time <= float(trip_a[25]) + float(trip_a[14]):
            flag_ba = 1
            benefit_ba = (ha_hb - hb_ba)/ha_hb
    print 'flag_ba'
    print flag_ba
    print 'benefit_ba'
    print benefit_ba
    #if flag_ab == 1 and flag_ba == 1:
    benefit = max(benefit_ab, benefit_ba)
    print 'final benefit'
    print benefit
    social_score = calc_social_score(trip_a, trip_b);
    #print 'social_score'
    #print social_score
    if(benefit !=0.0):
        G.add_edge(trip_a[0], trip_b[0], weight=10000*(benefit*2*.8) + social_score)
    #print 'graph'
    #print list(G.edges.items())
    #G.add_edge('100', '200', weight=1+benefit*.8)
    #elist = [('a', 'b', 5.0), ('b', 'c', 3.0), ('a', 'c', 1.0), ('c', 'd', 7.3)]
    #G.add_weighted_edges_from(elist)
    #print list(G.edges.items())
    #if flag_ab == 1 and flag_ba == 0:



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

def calculate_savings(trip_a, trip_b):
    savings = 0
    distance_a = float(trip_a[9])
    distance_b = float(trip_b[9])
    savings = abs(distance_a - distance_b)

    return savings


"""
Main function
"""
def main():
    conn = make_connection()

    all_trips = get_trips(conn)
    total_trips = len(all_trips)

    pools = get_pools(all_trips, total_trips, 5)

    print all_trips[0]

    pool =0

    for i in range(len(pools[pool])):
        for j in range(i+1, len(pools[pool])):
            a = int(pools[pool][i]) - int(all_trips[0][0])
            b = int(pools[pool][j]) - int(all_trips[0][0])
            check(conn, all_trips[a], all_trips[b])

    print 'length of pool'
    print pools[pool], len(pools[pool])
    #check(conn, all_trips[0], all_trips[1])
    print 'graph'
    print list(G.edges.items())

    print 'max matching'

    maximum_matching = list(nx.max_weight_matching(G, maxcardinality=True, weight='weight'))
    print maximum_matching, len(maximum_matching)

    distance_saved = 0.0
    total_combined_trips = len(maximum_matching)
    for i in range(total_combined_trips):
        trip_a_id = int(maximum_matching[i][0]) - int(all_trips[0][0])
        trip_b_id = int(maximum_matching[i][1]) - int(all_trips[0][0])
        # print len(all_trips), trip_a_id, trip_b_id

        trip_a = all_trips[trip_a_id]
        trip_b = all_trips[trip_b_id]
        distance_saved += calculate_savings(trip_a, trip_b)

    print "Total Savings"
    print distance_saved

    trips_saved = (total_combined_trips * 2)
    print "trips saved"
    print trips_saved

    # distance_saved = 0.0
    # trips_saved = 0
    # for pool in range(len(pools)):
    #     for i in range(len(pools[pool])):
    #         for j in range(i, len(pools[pool])):
    #             a = int(pools[pool][i]) - int(all_trips[0][0])
    #             b = int(pools[pool][j]) - int(all_trips[0][0])
    #
    #             check(conn, all_trips[a], all_trips[b])
    #             maximum_matching = list(nx.max_weight_matching(G, maxcardinality=True, weight='weight'))
    #
    #             # calculate distance and trips saved
    #             total_combined_trips = len(maximum_matching)
    #             for i in range(total_combined_trips):
    #                 trip_a_id = int(maximum_matching[i][0]) - int(all_trips[0][0])
    #                 trip_b_id = int(maximum_matching[i][1]) - int(all_trips[0][0])
    #                 # print len(all_trips), trip_a_id, trip_b_id
    #
    #                 trip_a = all_trips[trip_a_id]
    #                 trip_b = all_trips[trip_b_id]
    #                 distance_saved += calculate_savings(trip_a, trip_b)
    #
    #             trips_saved += (total_combined_trips * 2)

    conn.close()

if __name__ == "__main__":
    main()
