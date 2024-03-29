#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import os
import sys
import subprocess

"""
Return the path of the executable if available, None otherwise
"""
def which(executable, cwd="."):
	try:
		"""
		Note, Windows will try first to look for the .exe or .cmd
		whithin the drectory requested, hence this code path should
		happen all the time.
		"""
		if sys.platform == "win32":
			pathList = os.environ["PATH"].split(os.pathsep)
			# If the path is a relative path
			if executable.find(os.path.sep):
				pathList.insert(0, path(cwd, os.path.dirname(executable)))
				executable = os.path.basename(executable)
			for root in pathList:
				for ext in [".exe", ".cmd", ""]:
					executablePath = os.path.join(root, "%s%s" % (executable, ext)).replace("/" if os.sep == "\\" else "\\", os.sep)
					if os.path.isfile(executablePath):
						return executablePath
		else:
			output = subprocess.check_output(["which", executable]).strip()
			return output if len(output) else None
	except:
		pass
	return None
