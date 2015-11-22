from pymongo import MongoClient

client = MongoClient()
db = client.twitter

import re
#if empty look up all - lookup = 'quantwiz'
lookup = ''
regex = re.compile(lookup)
rstats = db.twitter.find({"text":regex})

#for document in rstats:
#	print(document)

print db.twitter.find({"text":regex}).count()
