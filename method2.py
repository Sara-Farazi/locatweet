import pdb
import json
import re
import sys
import math

from pymongo import MongoClient
from scipy.optimize import minimize_scalar


DATA_FOLDER = "data/"


def get_file_path(filename):
    return DATA_FOLDER + filename


#this function reads the "filename" file from the data folder
#returns a list object containing all the tweets or users in the file
def parse_file(filename):
    import json
    f = open(get_file_path(filename))
    res = json.load(f)
    f.close()
    return res

names = ["Edmonton, Alberta-tweet.json", "Calgary, Alberta-tweet.json", "Montral, Qubec-tweet.json", "Ottawa, Ontario-tweet.json", "Toronto, Ontario-tweet.json"]

lats = [0, 53.55014, 51.05011, 45.50008, 45.4168, 46.45012]
longs = [0, -113.46871, -114.08529, -73.66588, -75.69934, -63.382]

#connect to mogno server and get a db object
client = MongoClient('localhost', 27017)
db = client.locatweet

#get the collection object for venue names and info
words = db.words

#for inserting into collection: venues.insert_one(obj)
#for querying a collection: for result in venus.find(obj)



for i in range(len(names)):
	res = parse_file(names[i])

	for t in range(0,len(res)):
		city_name = res[t][len(res[0]) - 1]
		# print(res[t])
		# print (city_name)
		for j in range(len(res[t][0])):
			word = words.find({"word": res[t][0][j]})
			
			if word.count() > 0:
				# print(word.count())
				obj = word.next()
				cities = obj["cities"]
				updated = False
				for city in cities:
					if city_name == city["name"]:
						city["number"] = city["number"] + 1
						updated = True
						break
				if not updated:
					cities.append({
							"name": city_name,
							"number": 1,
						})

				words.update({
						"word": res[t][0][j],
					}, {
						"$set": {
							"cities": cities,
						}
					})

			else:
				words.insert_one({
				"word": res[t][0][j],
				"cities": [{
						"name": city_name,
						"number": 1, 
						"prob": 0
					}, ],
				"center": {"city": "None",
				"max_count": 0}

				})


all_words = words.find({})
num_of_words = all_words.count()

while (num_of_words > 0):
	obj = all_words.next()
	cities = obj["cities"]
	max_count = 0
	center = "None"
	for city in cities:
		if city["number"] > max_count:
			max_count = city["number"]
			center = city["name"]

	words.update({
				"word": obj["word"],
				}, {
					"$set": {
						"center": {"city": center, "max_count": max_count},
					}
				})
	num_of_words = num_of_words - 1

def get_dist(x1, x2, y1, y2):
	#print(x1.__str__() + ", " + y1.__str__() + " to " + x2.__str__() + ", " + y2.__str__())
	#print(math.sqrt(math.pow((x1 - x2), 2) + math.pow((y1 - y2), 2 )))
	return math.sqrt(math.pow((x1 - x2), 2) + math.pow((y1 - y2), 2 ))




def find_index(name):

	for i in range(len(names)):
		
		if names[i].split("-")[0] == name:
			return i




all_words = words.find({})
num_of_words = all_words.count()

while (num_of_words > 0):
	obj = all_words.next()
	
	def f(x):

		# print("THIS IS X %%%%%%%%%%%%%%%%%%%")
		# print(x)
		value = 0
		cind = find_index(obj["center"]["city"])
		
		for city in obj["cities"]:
			ind = find_index(city["name"])
			
			dist = get_dist(lats[cind], lats[ind], longs[cind], longs[ind])
			if dist == 0:
				continue

			#print(math.log(obj["center"]["max_count"] * (dist**(-x))))
			# print(math.log(obj["center"]["max_count"] * ( dist **(-x))))
			# print("&&&&&&&&&&&&&&&&&&&&&&")

			value = value + math.log(obj["center"]["max_count"] * ( dist **(-x))) * 100000
			# print(value)

		not_twitted = ["Edmonton, Alberta", "Calgary, Alberta", "Montral, Qubec", "Ottawa, Ontario", "Toronto, Ontario"]
		
		for city in obj["cities"]:
			for item in names:
				if item.split("-")[0] == city["name"]:
					not_twitted.remove(city["name"])

		for item in not_twitted:
			ind = find_index(item)
			dist = get_dist(lats[cind], lats[ind], longs[cind], longs[ind])
			if dist == 0:
				continue


			#print(obj["center"]["max_count"] * (dist**(-x)))
			
			value = value + math.log(1 - (obj["center"]["max_count"] * (dist**(-x)))) * 100000
			# print(value)
			#print(math.log(1 - (obj["center"]["max_count"] * (get_dist(lats[cind], lats[ind], longs[cind], longs[ind])**(-x))) ))
		# print(value)

		return (-1) * value


	# import pdb
	# pdb.set_trace()


	# print("Here we go...")
	res = minimize_scalar(f, bounds = (1, 8), method = "bounded")
	# print("Done optimization")
	
	alpha = res.x
	# print(alpha)

	cind = find_index(obj["center"]["city"])
	for city in obj["cities"]:
			ind = find_index(city["name"])
			if ind == cind:
				prob = 1
			else:
				prob = obj["center"]["max_count"] * (get_dist(lats[cind], lats[ind], longs[cind], longs[ind])**(-alpha))
			city["prob"] = prob


	words.update({
				"word": obj["word"],
			}, {
				"$set": {
					"cities": obj["cities"],
				}
			})
	num_of_words = num_of_words - 1



		




	








