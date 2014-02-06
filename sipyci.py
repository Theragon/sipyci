#!/usr/bin/env python 

""" 
A simple CI server 
""" 

import signal
import socket
import sys
import subprocess

repopath='/home/ru/NetCrawler'	#This is for ru.dev.lab
worktree='/home/logan/tmp/CIserver'
gitdir='/home/logan/gitrepos/NetCrawler/.git'

#git --work-tree=/repo/path --git-dir=/repo/path/.git pull origin master
#gitPull = 'git --work-tree='+repopath+' --git-dir='+repopath+'/.git pull origin master'	#This is for ru.dev.lab
gitPull = 'git --work-tree='+worktree+' --git-dir='+gitdir+' pull origin master'

host = ''
port = 50000
backlog = 5
size = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host,port))
s.listen(backlog)

def main():

	while 1:
		client, address = s.accept()
		data = client.recv(size)

		if data:
			print(data + 'end of data')
			client.send(data)
			if (data == 'pull\r\n'):			#This should change later when git hooks are used
				print('Pulling from git...')
				subprocess.call(gitPull, shell=True)
			break

		client.close()

	s.close()

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