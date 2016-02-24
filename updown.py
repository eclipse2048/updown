#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import web
import os
import platform
import cgi

# set some vars for web.py
MAX_FILE_SIZE_GB = 2
RELATIVE_URL = "/"
cgi.maxlen = MAX_FILE_SIZE_GB * 1024 * 1024 * 1024
urls = (RELATIVE_URL, "UpDown")
render = web.template.render(".")
app = web.application(urls, globals())

class UpDown:
	def getFilesAndSizes(self):
		files = sorted(os.listdir("static/"))
		sizes = [os.path.getsize("static/" + f) for f in files]
		files.append("Total: " + str(len(files)) + " files")
		sizes.append(sum(sizes))
		
		# make sizes readable
		for i in range(len(sizes)):
			if sizes[i]/1024 < 1:
				sizes[i] = str(sizes[i]) + " B"
			elif sizes[i]/1024/1024 < 1:
				sizes[i] = str(format(sizes[i]/1024, ".1f")) + " KB"
			elif sizes[i]/1024/1024/1024 < 1:
				sizes[i] = str(format(sizes[i]/1024/1024, ".1f")) + " MB"
			else:
				sizes[i] = str(format(sizes[i]/1024/1024/1024, ".1f")) + " GB"
		return zip(files, sizes)

	def GET(self):
		input = web.input()
		note = ""
		if "note" in input:
			note = input["note"]
		return render.updown(self.getFilesAndSizes(), note)

	def POST(self):
		note = ""

		try:
			input = web.input(upfile={})
		except ValueError:
			return render.updown(self.getFilesAndSizes(), "Upload failed. File must be smaller than " + MAX_FILE_SIZE_GB + "GB.") 
		
		for item in input.items():
			if item[0][:3] == "del":	# delete file
				f = "static/" + item[1]
				print "deleting file", f
				if os.path.isfile(f):
					try:
						os.remove(f)
						note = "File(s) deleted."
					except Error:
						pass

			elif item[0] == "upfile":	# upload new file
				if item[1] == {} or item[1].filename == "":	# no upload file given? do nothing
					continue
				filepath = item[1].filename.replace('\\','/')	# remove Windows slashes
				filename = "static/" + os.path.basename(filepath)

				# overwrite check
				if os.path.exists(filename):
					if "overwrite" not in input.keys() or input["overwrite"] != "yes":
						note = "Upload cancelled, not authorized to overwrite file."
						continue
				
				print "Uploading", filename

				# use different file write mode depending on OS
				if platform.system() == "Windows":
					fout_mode = "wb"
				else:	
					foutmode = "w"
				fout = open(filename, foutmode)
				fout.write(item[1].file.read())
				fout.close()
				note = "Uploaded file " + os.path.basename(filepath) + "."

		return render.updown(self.getFilesAndSizes(), note)

if __name__ == "__main__":
	# next line is necessary for deployment on nginx + fastcgi (see http://webpy.org/cookbook/fastcgi-nginx)
#	web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)	
	app.run()
