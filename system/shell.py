#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import subprocess
import sys
import threading
import time
try:
	from queue import Queue
except:
	from Queue import Queue

"""
To store the instance of process started with the non-blocking option
"""
global runningProcess
runningProcess = []

"""
Execute a shell command in a specific directory.
If it fails, it will throw.
@param blocking Tells if the process should block the execution. If not it will run in parallel and might block the ending of the caller
                process if it ends.
"""
def shell(command, cwd=".", capture=False, ignoreError=False, queue=None, signal=None, hideStdout=False, hideStderr=False, blocking=True):

	def enqueueOutput(out, queue, signal):
		try:
			for line in iter(out.readline, b''):
				queue.put(line.rstrip().decode('utf-8', 'ignore'))
		except:
			pass
		out.close()
		signal.set()

	stdout = open(os.devnull, "w") if hideStdout else (subprocess.PIPE if capture or queue else None)
	stderr = open(os.devnull, "w") if hideStderr else (subprocess.STDOUT if capture or queue else None)

	isReturnStdout = True if capture and not queue else False

	# Workaround on Windows machine, the environment path is not searched to find the executable, hence
	# we need to do this manually.
	if sys.platform == "win32":
		fullPath = which(command[0], cwd=cwd)
		if fullPath:
			command[0] = fullPath

	proc = subprocess.Popen(command, cwd=cwd, shell=False, stdout=stdout, stderr=stderr)

	# If non-blocking returns directly
	if not blocking:
		global runningProcess
		runningProcess.append(proc)
		return

	if not queue:
		queue = Queue()

	if not signal:
		signal = threading.Event()

	# Wait until a signal is raised or until the the process is terminated
	if capture:
		outputThread = threading.Thread(target=enqueueOutput, args=(proc.stdout, queue, signal))
		outputThread.start()
		signal.wait()
	else:
		while proc.poll() is None:
			time.sleep(0.1)
			if signal.is_set():
				break

	errorMsgList = []

	# Kill the process (max 5s)
	stoppedBySignal = True if proc.poll() is None else False
	if stoppedBySignal:
		def processTerminateTimeout():
			proc.kill()
			errorMsgList.append("stalled")
		timer = threading.Timer(5, processTerminateTimeout)
		try:
			timer.start()
			proc.terminate()
			proc.wait()
		finally:
			timer.cancel()

	if proc.returncode != 0:
		errorMsgList.append("return.code=%s" % (str(proc.returncode)))

	if len(errorMsgList):
		if not ignoreError:
			message = "Failed to execute '%s' in '%s': %s" % (" ".join(command), str(cwd), ", ".join(errorMsgList))
			raise Exception(message)

	# Build the output list
	return list(queue.queue) if isReturnStdout else []

"""
Ensure that the processes previously started are destroyed
"""
def destroy():
	isError = False
	# Wait until all non-blocking process previously started are done
	global runningProcess
	for process in runningProcess:
		isError |= (process.wait() != 0)
	return isError
