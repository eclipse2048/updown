#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import web
import os
import platform
import cgi
from operator import itemgetter

# set some vars for web.py
RELATIVE_URL = "/"
urls = (RELATIVE_URL, "UpDown")
render = web.template.render(".")
app = web.application(urls, globals())

# set some more vars
MAX_FILE_SIZE_GB = 2
cgi.maxlen = MAX_FILE_SIZE_GB * 1024 * 1024 * 1024

class UpDown:
	
	sortBy = 0	# 0=name, 1=size
	sortReverse = False	# False=ascending, True=descending

	def getFilesAndSizes(self):
		files = []
		if os.path.isdir("static/"):
			files = os.listdir("static/")
		sizes = [os.path.getsize("static/" + f) for f in files]
		fs = zip(files, sizes)
		fs.sort(key=itemgetter(UpDown.sortBy), reverse=UpDown.sortReverse)
		fs.append(("Total: " + str(len(fs)) + " files", sum(sizes)))

		# make sizes readable
		f, s = zip(*fs)	# zip() creates a list of immutable tuples, so to prettify the file sizes we have to unzip again
		sl = list(s)
		for i in range(len(sl)):
			if sl[i]/1024 < 1:
				sl[i] = str(sl[i]) + " B"
			elif sl[i]/1024/1024 < 1:
				sl[i] = str(format(sl[i]/1024, ".1f")) + " KB"
			elif sl[i]/1024/1024/1024 < 1:
				sl[i] = str(format(sl[i]/1024/1024, ".1f")) + " MB"
			else:
				sl[i] = str(format(sl[i]/1024/1024/1024, ".1f")) + " GB"
		return zip(f, sl)

	def GET(self):
		input = web.input()

		note = ""
		if "note" in input:
			note = input["note"]

		# evaluate sorting parameter
		if "sort" in input:
			if input["sort"] == "name":
				if UpDown.sortBy == 0:
					UpDown.sortReverse = not UpDown.sortReverse
				else:
					UpDown.sortBy = 0
					UpDown.sortReverse = False
			elif input["sort"] == "size":
				if UpDown.sortBy == 1:
					UpDown.sortReverse = not UpDown.sortReverse
				else:
					UpDown.sortBy = 1
					UpDown.sortReverse = False

		return render.updown(self.getFilesAndSizes(), note)

	def POST(self):

		try:
			input = web.input(upfile={})
		except ValueError:	# file is too big
			return render.updown(self.getFilesAndSizes(), "Upload failed. File must be smaller than " + MAX_FILE_SIZE_GB + "GB.") 
		
		note = ""
		for item in input.items():

			# delete file
			if item[0][:3] == "del":
				f = "static/" + item[1]
				if os.path.isfile(f):
					try:
						os.remove(f)
						print "Deleted file", f
						note = "File(s) deleted."
					except Error:
						print "Error while trying to delete file", f 

			# upload new file
			elif item[0] == "upfile":
				# no upload file given? do nothing
				if item[1] == {} or item[1].filename == "":	
					return render.updown(self.getFilesAndSizes(), "")

				# remove Windows slashes
				filepath = item[1].filename.replace('\\','/')
				filename = "static/" + os.path.basename(filepath)

				# overwrite check
				if os.path.exists(filename):
					if "overwrite" not in input.keys() or input["overwrite"] != "yes":
						return render.updown(self.getFilesAndSizes(), "File already exists. Check box to overwrite.")
				print "Uploading", filename

				# use different file write mode depending on OS
				if platform.system() == "Windows":
					fout_mode = "wb"
				else:	
					foutmode = "w"
				fout = open(filename, foutmode)
				fout.write(item[1].file.read())
				fout.close()
				return render.updown(self.getFilesAndSizes(), "Uploaded file " + os.path.basename(filepath) + ".")

		return render.updown(self.getFilesAndSizes(), note)

if __name__ == "__main__":
	# next line is necessary for deployment on nginx + fastcgi (see http://webpy.org/cookbook/fastcgi-nginx)
#	web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)	
	app.run()
