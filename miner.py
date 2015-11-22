import commands
import sys
output = commands.getoutput('ps -A')
#check if mongod on else exit
if 'mongod' in output:
	print("Mongod On")
else:
	print("Mongod Off")
	sys.exit()

from random import shuffle
#service mongod start, before script starts
from pymongo import MongoClient
client = MongoClient('localhost', 27017)

import os, sys #remove ghostdriver.log

from bs4 import BeautifulSoup
from selenium import webdriver
import random
import time
import datetime


def stalker(link):

	#/usr/local/bin/phantomjs, where phanomjs exe located
	#--ignore-ssl-errors=true, enable, else blank in ssl page
	driver = webdriver.PhantomJS('/usr/local/bin/phantomjs', service_args=['--ignore-ssl-errors=true']) 

	driver.get(link)
	
	lastHeight = driver.execute_script("return document.body.scrollHeight")
	while True:
	    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	    a = random.randrange(3,6)
	    time.sleep(a) #add random delay avoid bot detection	
	    newHeight = driver.execute_script("return document.body.scrollHeight")
	    if newHeight == lastHeight:
		break
	    lastHeight = newHeight

	soup = BeautifulSoup(driver.page_source, 'html.parser')
	
	post = text = soup.findAll("div", { "class" : "tweet original-tweet js-original-tweet js-stream-tweet js-actionable-tweet js-profile-popup-actionable  dismissible-content "})

	for info in post: 
		#Grab Username
		username = info.find("strong", { "class" : "fullname js-action-profile-name show-popup-with-id" }).getText()

		#Grab Hashtag
		hashtag = info.find("span", { "class" : "username js-action-profile-name" }).getText()

		#Grab Date and Time
		date = info.find("a", { "class" : "tweet-timestamp js-permalink js-nav js-tooltip"})['title']

		#Text
		text = info.find("p", { "class" : "TweetTextSize  js-tweet-text tweet-text"}).getText()

		#Store in Twitter database
		db = client.twitter
		
		#Store in Sugar collection
		#change db.twitter to db.whatever - whatever is collection name
		result = db.twitter.insert_one(
		    {
			"username": username,
			"hashtag": hashtag,
			"date": date,
			"text": text       
		}
		)

def normal_link(topic,start,end):
	result = 'https://twitter.com/search?f=tweets&vertical=default&q=%22'+topic+'%22%20since%3A'+start+'%20until%3A'+end+'&src=typd&lang=en'
	return result

def track(topic,num):
	if num == 0:
		num = num + 1
	count = 0
	current = datetime.datetime.now() - datetime.timedelta(days=1)
	try:
		for i in xrange(num):
			minus = current - datetime.timedelta(days=1)
			past = minus
			#print past.strftime('%Y-%m-%d') ,'\t', current.strftime('%Y-%m-%d')
			
			#Start - Main Function 
			stalker(normal_link(topic,str(past.strftime('%Y-%m-%d')),str(current.strftime('%Y-%m-%d'))))
			#End - Can be other link function	
		
			current = past
			count = count + 1
			a = random.randrange(1,3)
	    		time.sleep(a) #add random delay avoid bot detection
			print topic, ' - ',count,' of ', num
	except:
			pass


#Skelton from http://www.bogotobogo.com/python/Multithread/python_multithreading_Synchronization_Semaphore_Objects_Thread_Pool.php
import threading

class ThreadPool(object):
    def __init__(self):
        super(ThreadPool, self).__init__()
        self.active = []
        self.lock = threading.Lock()
    def makeActive(self, name):
        with self.lock:
            self.active.append(name)
    def makeInactive(self, name):
        with self.lock:
            self.active.remove(name)

def grab(i,s, pool):		
	with s:
		name = threading.currentThread().getName()
		pool.makeActive(name)
		#start - add function
		track(str(i),2)
		#print str(i)		
		time.sleep(0.5)
		#end - add function
		pool.makeInactive(name)


pool = ThreadPool()
s = threading.Semaphore(12)

filePath = "input"
wordList = []
wordCount = 0

#Read lines into a list
file = open(filePath, 'rU')
for line in file:
    for word in line.split():
        wordList.append(word)
        wordCount += 1
wordList = dict.fromkeys(wordList).keys()

tweets = []
for words in wordList:
    words_filtered = [e.lower() for e in words.split() if len(e) >= 3] 
    tweets.append(words_filtered)


shuffle(tweets)

print tweets

for i in tweets:
	try:
		t = threading.Thread(target=grab, name=str(i), args=(i,s, pool))
		t.start()
	except:
		pass

try:
	os.remove("ghostdriver.log")
except:
	pass
