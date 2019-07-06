#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import errno
import os
import shutil
import stat
import time

"""
Delete a directory and all its content
"""
def rmtree(path, ignoreError=False):
	# This is needed for Windows
	def handleRemoveReadonly(func, path, exc):
		excvalue = exc[1]
		if excvalue.errno == errno.EACCES:
			os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO) # 0777
			func(path)
		else:
			raise
	retryCounter = 3
	while retryCounter:
		shutil.rmtree(path, ignore_errors=True, onerror=handleRemoveReadonly)
		if not os.path.exists(path) or ignoreError:
			break
		retryCounter -= 1
		# Wait for 1s, this is needed for Windows (probably for some cache to be flushed)
		time.sleep(1)
	if retryCounter == 0:
		raise Exception("Unable to delete directory '%s'" % (str(path)))
