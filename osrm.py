#!/usr/bin/env python

import requests
import urllib
import csv
import sys
import json

def main():
	coordinates  = []

	with open('NYC_Intersetions.csv') as File:
		reader = csv.reader(File)
		for row in reader:
			coordinates.append(row)

	output_file = open("int_dd.csv", "a")

	# coordinates = [[40.645692, -73.783717], [40.7980472, -73.96004], [40.798645, -73.9614743], [40.7992369, -73.962876]]
	jfk = ["40.645692", "-73.783717"]
	for i in range(1, 11490, 5):
		osrm_api_url = "http://router.project-osrm.org/"
		path = "route/v1/driving/"
		url = osrm_api_url + path
		
		for j in range(5):
			url += jfk[1] + "," + jfk[0] + ";" + str(coordinates[i + j][2]) + "," + str(coordinates[i + j][1]) + ";"
		url  = url[:-1]
		url += "?annotations=distance"
		response  = requests.get(url).text
		json_response = json.loads(response)
		distance_matrix = json_response["routes"][0]["legs"]
		print len(json_response["waypoints"])
		for j in range(5):
			line = str(i + j) + "," + str(coordinates[i + j][1]) + "," + str(coordinates[i + j][2]) + "," + str(distance_matrix[j * 2]["distance"]) + "," + str(distance_matrix[j * 2]["duration"]) + "\n"
			print line
			output_file.write(line)

	output_file.close()

if __name__ == "__main__":
	main()

