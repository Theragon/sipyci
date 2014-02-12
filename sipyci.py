#!/usr/bin/env python 

""" 
A simple python CI server

run example: ./sipyci port=90 path=/home/user/repo/
run example: ./sipyci path=/full/path/to/repo
port is optional, default port is 5000
sudo to make sure you can open a port
run as administrator on windows


"""

import os
import signal
import socket
import sys
import subprocess
from subprocess import check_output
import json
import urllib2
from pprint import pprint

repopath='/home/ru/NetCrawler'		#This is for ru.dev.lab
worktree='/home/logan/tmp/CIserver'
gitdir='/home/logan/gitrepos/NetCrawler/.git'

#git --work-tree=/repo/path --git-dir=/repo/path/.git pull origin master
#pullString = 'git --work-tree='+repopath+' --git-dir='+repopath+'/.git pull origin master'	#This is for ru.dev.lab
#pullString = 'git --work-tree='+worktree+' --git-dir='+gitdir+' pull origin master'

######################
"""GLOBAL VARIABLES"""
######################
s = None
path = ''
host = ''		# '' means ANY address the machine happens to have
size = 1024
port = 5000
backlog = 5
client = None
address = None
pullString = ''
######################
"""GLOBAL VARIABLES"""
######################

def main():
	"""
	Main function
	parses arguments
	opens socket
	binds to address
	waits for connection
	receives data
	"""

	global path
	global pullString
	global port

	if(len(sys.argv) > 1):
		port, path = parseInput(sys.argv)
	else:
		exit('A path to repository must at least be provided')

	#pullString = 'git --work-tree='+path+' --git-dir='+path+'.git pull origin master'

	openSocket()
	bindToAddress()

	createPullString()

	print('Server is ready and listening on port ' + str(port))

	while 1:
		waitForConnection()
		receiveData()


def parseInput(args):
	foundpath = False
	foundport = False

	for arg in sys.argv:
		if(arg == sys.argv[0]):
			continue
		if(arg[0:5] == 'port='):
			foundport = True
			port = int(arg[5:])
		if(arg[0:5] == 'path='):
			foundpath = True
			path = str(arg[5:])

	if(foundpath == False):
		exit('A path to repository must at least be provided')
	if(foundport == False):
		port = 5000
		print('no port argument found, using default port 5000')

	checkPath(path)

	return port, path


def checkPath(path):
	if os.path.exists(path):
		if sys.platform == 'linux' or sys.platform == 'linux2':		#linux
			if(path[-1:] != '/'):
				exit('path must end with a /')
		elif sys.platform == 'win32' or sys.platform == 'cygwin':	#windows
			if(path[-1:] != '\\'):
				exit('path must end with a \\')
		elif sys.platform == 'darwin':								#OS X
			if(path[-1:] != '/'):
				exit('path must end with a /')
			
	elif not os.path.exists(path):
		exit('invalid path to repository')


def exit(why):
	print(why)
	if s:
		s.close()
	sys.exit(1)


def openSocket():
	global s
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	except socket.error, (value, message):
		if s:
			s.close()
		else:
			exit('failed to open socket: ' + message)


def bindToAddress():
	global s
	try:
		s.bind((host, port))	# s.bind(('', 80)) specifies that the socket is reachable by any address the machine happens to have on port 80
		s.listen(backlog)
	except socket.error, (value, message):
		if s:
			s.close()
		else:
			exit('failed to bind to address: ' + message)


def createPullString():
	global pullString
	pullString = 'git --work-tree='+path+' --git-dir='+path+'.git pull origin master'


def waitForConnection():
	global client
	global address
	print('waiting for connection...')
	client, address = s.accept()
	print address, ' connected'


def receiveData():
	buff = ''
	while True:
		data = client.recv(size)
		buff += data

		if data:
#			print(data + 'end of data')
			print('length of data: ' + str(len(data)))
			#if (data[0:4] == 'pull'):			# This should change later when git hooks are used
				#print('Pulling from git...')
				#subprocess.call(pullString, shell=True)

		elif not data:
			break

	client.close()

	print('client disconnected')
	print('length of buff: ' + str(len(buff)))
	print('data received:')
	#print(buff)
	parseBuffer(buff)


def parseBuffer(buff):
	#global path
	payloadPos = buff.find('payload=')

	if(payloadPos != -1):
		print('found payload at position: ' + str(payloadPos+8))
		payload = buff[payloadPos+8:]
		#payload = urllib.unquote_plus(payload)	# parse from url-encoded
		payload = urllib2.unquote(payload)
		payload2 = json.loads(payload)
		#print json.dumps(payload)
		#pprint(payload2)

		#print('payload keys:')
		#print(payload2.keys())

		#print('payload values:')
		#print(payload2.values())

		'''
		print('loop through dictionary:')
		for item in payload2:
			print payload2[item]
		'''

		global pullString
		#print('pullString: ' + pullString)
		print('Pulling from git...')
		#p = subprocess.call(pullString, shell=True)
		out = check_output(['git', '--work-tree='+path, '--git-dir='+path+'.git', 'pull', 'origin', 'master'])
		#out, err = p.communicate()

		print('output from shell: \n' + out)
	#	for k,v in payload2.items():
	#		print k,v


def handler(signum, frame):
	print '\nSignal handler called with signal', signum
	print 'Shutting down server'
	if s:
		s.close()
	sys.exit('sipyci successfully closed')

signal.signal(signal.SIGINT, handler)


if __name__ == '__main__':
	main()
#p1 = Popen(['echo', 'Hello', 'world'], stdout=PIPE)
#p2 = Popen(['cut', "-d' '", '-f1'], stdin=p1.stdout, stdout=PIPE)
#p1.stdout.close()
#test = p2.communicate()[0]

#process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
#output = process.communicate()[0]