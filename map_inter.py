#!usr/bin/python

import csv
import json
import requests

coordinates = []

def main():
	outfile = open("trip_inter.csv", "w")

	with open("ftrips.csv") as File:
		reader = csv.reader(File)
		for row in reader:
			coordinates.append([row[10], row[9]])

	for i in range(1, 35000):
		url = "http://api.geonames.org/findNearestIntersectionOSMJSON?"
		url += "lat=" + coordinates[i][0] + "&lng=" + coordinates[i][1] + "&username=administrator"
		response = requests.get(url).text
		json_response = json.loads(response)

		lat = json_response['intersection']['lat']
		lng = json_response['intersection']['lng']
		line  = str(i) + "," + lat + "," + lng + "\n"

		print line

		outfile.write(line)

if __name__ == "__main__":
	main()
