#!/usr/bin/python
#Author: Jeff Norris
#Script when execute will prompt for the NFL photo gallery url and then downloads the high
#resolution images in a unique directory in the current working directory where script resides in
import urllib2
import os
import sys
import threading
import Queue

#Creation of class to allow multithreading for the image downloading and saving image to disk
class NFLThread(threading.Thread):
	def __init__(self,plist,idlist,imgpth):
		super(NFLThread,self).__init__()
		self.plist = plist
		self.idlist = idlist
		self.imgpth = imgpth
		
	def run(self):
		while not self.plist.empty() and not self.idlist.empty():
			link = ""
			id = ""
			fpth = self.imgpth
			link = self.plist.get()
			id = self.idlist.get()
			try:
				fpth += id + ".jpg"
				req = urllib2.Request(link)
				urlimage = urllib2.urlopen(req).read()
				outpt = open(fpth,'wb')
				outpt.write(urlimage)
				outpt.close()
			except:
				print "Invalid link"
				pass


q = Queue.Queue()
userurl = raw_input("Please enter the NFL photo gallery url: ")
title = "\"storyHeadline\":\""
idq = Queue.Queue()

#retrieves page to extract urls for largest sized images in gallery
try :
	url = urllib2.Request(userurl)
	resp = urllib2.urlopen(url)
	page = resp.read().split("<script type=\"text/javascript\">")
	
except:
	sys.exit()

#identifies javascript variable containing url for each image in specified 	
tag = "pgJSON"
idtag = "\"id\":\""
endtag = "};"
tag1 = "\"photoUrl\":\""
endtag1 = ".jpg"
fid = 0
titl = ""
type = ""


for item in page:
	if tag in item:
		vind = item.index(tag)
		vend = item.index(endtag)
		item = item[vind:vend]
		list = item.split(",")

for picture in list:
	if titl == "" and title in picture:
		titl = picture.replace(title,"").rstrip("\"")
	elif idtag in picture:
		if fid == 0:
			fid = fid + 1
		else:
			sind = picture.index(idtag)
			picture = picture[sind+len(idtag):]
			send = picture.index("\"")
			picture = picture[:send]
			idq.put(picture.rstrip("\""))
	elif tag1 and "_gallery_600.jpg" in picture: #logic to find and delete old text in image path to be able to download high resolution image
		link = ""
		try:
			ind = picture.index(tag1)
			picture = picture[ind+len(tag1):]
			end = picture.index(endtag1)
			link = picture[:end+len(endtag1)]
			link = link.replace("_gallery_600","")
			q.put(link)
		except:
			pass
	elif tag1 and "pg_600" in picture:#logic to find and delete current text in image path to be able to download high resolution image
		link = ""
		try:
			ind = picture.index(tag1)
			picture = picture[ind+len(tag1):]
			end = picture.index(endtag1)
			link = picture[:end+len(endtag1)]
			link = link.replace("_pg_600","")
			q.put(link)
		except:
			pass
#Allows the creation of directories for images to save to on Mac, Windows, and Linux operating systems
home = ""
pth = sys.path[0]
pth = pth.replace("\\","/")
home = titl.rstrip("\"")
home = home.replace(":","")
pth += "/" + home + "/"

#creation of directory on local host in directory where script is present
try:
	if not (os.path.exists(pth)):
		os.mkdir(home) #creates directory for each gallery set
except OSError:
	print
	print "Can not make directory"
	sys.exit()

# retrieves and saves each image individually to disk using 3 threads
thread1 = NFLThread(q,idq,pth)
thread2 = NFLThread(q,idq,pth)
thread3 = NFLThread(q,idq,pth)
thread1.start()
thread2.start()
thread3.start()
thread1.join()
thread2.join()
thread3.join()
