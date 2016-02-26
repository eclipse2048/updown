# updown – a simple file uploader/downloader

updown is a simple web script to upload and download files. It is written in Python and runs on web.py. It is available under the GPLv3 License.

The script shows a web page listing all currently uploaded files, sortable by name and size. You can download and delete existing files and upload new ones. That's why it's called updown …

NOTE: There is no security whatsoever. No password, no encryption, nada. The only thing that even remotely counts as a security measure is the (very basic) overwrite guard for your uploads. Other than that, nothing. Everybody who knows the URL to your script can download or delete your files and upload stuff onto your server that you may not want there. Use at your own risk!

Dependencies:

  * Python (v2.6 or so; I used v2.7)
  * web.py (I used v0.37)

You can either run the script from the command line and use web.py's built-in webserver, or you can deploy it on your own webserver (see [here](http://webpy.org/cookbook/) for details). In any case, all uploads are stored in the `static/` subdirectory of the script's own dir (which must therefore be read-/writable).

You may want to take a look at two constants while setting things up:

  * `RELATIVE_URL` is the URL under which the script will be listening, relative to the web root. If you run updown on a real webserver, change this value accordingly. Default is /, which is fine for the built-in webserver.
  * `MAX_FILE_SIZE_GB` limits the upload size for a file. Default is 2 GB.
