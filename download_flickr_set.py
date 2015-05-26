#!/usr/bin/env python

import flickrapi
import requests
import xml
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ElementTree
import requests
import os
import re
import time

#User credentials/set specifiers
FLICKR_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" #Your Flickr Key here
FLICKR_SECRET = "xxxxxxxxxxxxxxxx" #Your Flickr Secret here
USER_ID = "xxxxxxxxxxxxx" #Your USER ID
SET_ID = "xxxxxxxxxxxxxxxxx" #Your Set ID

#method gets urls to photos in the photoset, compares them to existing files
#then updates the folder containing files and restarts the slideshow if updates
#were made
def main(key, setID, userID):
	#Authenticating with Flickr
	flickr = flickrapi.FlickrAPI(FLICKR_KEY, FLICKR_SECRET)
	url = 'url_o'
	urlList = []
	update = False
	count = 0
	
	#photoList is a "Root Element" type in an element tree. Whatever that means.
	photoList = flickr.photosets.getPhotos(api_key=key, photoset_id=setID, user_id=userID, extras=url)
	
	#going through photosets in photoList. Should only be one.
	for photoSet in photoList:
		#This thing over here with dump raw photoSet xml type thing ----> xml.etree.ElementTree.dump(photoSet)
		#Going through photo objects in photoSet, adding them to urlList.
		for photo in photoSet:
			urlString = str(photo.get('url_o'))
			urlList.append(urlString)
			count += 1
	
	#Final list of urls for all photos
	print urlList
	
	#Download the pictures
	for photo in urlList:
		jpgName = photo[-29:]
		path = '/home/pi/photoframe/flickr/%s' % jpgName
		try:
			image_file = open(path)
			print "-----Already have %s" % jpgName
		except IOError:
			print "-----Downloading %s" % jpgName
			r = requests.get(photo)
			image_file = open(path, 'w')
			image_file.write(r.content)
			image_file.close()
			update = True
	
	#Comparing file list grabbed from Flickr to file list grabbed from file.
	filelist = os.listdir('/home/pi/photoframe/flickr')
	if count < len(filelist):
		print "-----Removing photos"
		
		#Removing photos deleted on Flickr from directory
		for f in filelist:
			pics = urlList
			for pic in pics:
				jpgName = pic[-29:]
				matchObj = re.match(f, jpgName)
				if matchObj:
					print "-----Found %s, matched %s" % (f, jpgName)
					break
				else:
					print "-----Deleting %s" % (f)
					try:
						os.remove("/home/pi/photoframe/flickr/"+f)
						update = True
						break
					except:
						print "-----"

	#Restarting slideshow if photos have been updated
	if update == True:
		print "-----Restarting slideshow"
		os.system("sudo reboot")

if __name__ == '__main__':
	main(FLICKR_KEY, SET_ID, USER_ID)
