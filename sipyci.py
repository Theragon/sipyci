#!/usr/bin/env python 

""" 
A simple python CI server

run example: ./sipyci port=90 path=/home/user/repo/
run example: ./sipyci path=/full/path/to/repo
"""

import signal
import socket
import sys
import subprocess
import json
import urllib2
from pprint import pprint

repopath='/home/ru/NetCrawler'	#This is for ru.dev.lab
worktree='/home/logan/tmp/CIserver'
gitdir='/home/logan/gitrepos/NetCrawler/.git'

#git --work-tree=/repo/path --git-dir=/repo/path/.git pull origin master
#gitPull = 'git --work-tree='+repopath+' --git-dir='+repopath+'/.git pull origin master'	#This is for ru.dev.lab
gitPull = 'git --work-tree='+worktree+' --git-dir='+gitdir+' pull origin master'

#path = ''
host = ''		# '' means any address the machine happens to have
#port = 5000
backlog = 5
size = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

def main():
	"""
	Main function
	parses input and enters a while true loop
	"""
	path = ''
	port = 5000

	if(len(sys.argv) > 1):
		port, path = parseInput(sys.argv)
		print('path to repo is: ' + path)
	else:
		print('you must provide a path to repo')
#		sys.exit(1)


	s.bind((host,port))	# s.bind(('', 80)) specifies that the socket is reachable by any address the machine happens to have on port 80
	s.listen(backlog)

	print('Server is ready and listening on port ' + str(port))

	waitForConnection()


def parseInput(args):
	foundpath = False
	foundport = False

	for arg in sys.argv:
		print(arg)
		if(arg == sys.argv[0]):
			continue
		if(arg[0:5] == 'port='):
			foundport = True
			port = int(arg[5:])
		if(arg[0:5] == 'path='):
			foundpath = True
			path = str(arg[5:])

	if(foundpath == False):
		print('you must provide a path to the repo')
	if(foundport == False):
		port = 5000

	return port, path


def waitForConnection():
	print('waiting for connection...')
	client, address = s.accept()
	print address, ' connected'
	receiveData(client, address)


def receiveData(client, address):
	buff = ''
	while True:
		data = client.recv(size)
		buff += data

		if not data: break

		if data:
#			print(data + 'end of data')
			print('length of data: ' + str(len(data)))
			if (data[0:4] == 'pull'):			# This should change later when git hooks are used
				print('Pulling from git...')
				subprocess.call(gitPull, shell=True)

	client.close()

	print('client disconnected')
	print('length of buff: ' + str(len(buff)))
	print('data received:')
	print(buff)
	parseBuffer(buff)
	waitForConnection()


def parseBuffer(buff):
	payloadPos = buff.find('payload=')
	print('found payload at position: ' + str(payloadPos+8))

	#print('payload: ' + str(buff[payloadPos+8:]))
	payload = buff[payloadPos+8:]
	#payload = urllib.unquote_plus(payload)	# parse from url-encoded
	payload = urllib2.unquote(payload)
	json.loads(payload)
	print('payload:')
	#print json.dumps(payload)
	pprint(payload)

	for key, value in d.iteritems():
		print key, value


def handler(signum, frame):
	print '\nSignal handler called with signal', signum
	print 'Shutting down server'
	s.close()
	sys.exit()

signal.signal(signal.SIGINT, handler)


if __name__ == '__main__':
	main()
#p1 = Popen(['echo', 'Hello', 'world'], stdout=PIPE)
#p2 = Popen(['cut', "-d' '", '-f1'], stdin=p1.stdout, stdout=PIPE)
#p1.stdout.close()
#test = p2.communicate()[0]

#process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
#output = process.communicate()[0]