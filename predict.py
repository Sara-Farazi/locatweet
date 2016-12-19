import pdb
import json
import re
import sys
import math
from pymongo import MongoClient



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

client = MongoClient('localhost', 27017)
db = client.locatweet

#get the collection object for venue names and info
corrects = 0
words = db.words

for i in range(len(names)):
	res = parse_file(names[i])
	size = len(res)
	for t in range(size - 100, size):
		real_city = res[t][len(res[0]) - 1]
		# for c in range(0,5):
		for j in range(len(res[t][0])):
			probability = 0;
			word = words.find({"word": res[t][0][j]})
			obj = word.next()
			probability = probability + obj["prob"]