# coding="utf-8"
# -*- coding: utf-8 -*-
import socket
import select
import sys
import struct
import os
import datetime
reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append("../")
from definations import *

class ChatServer(object):

	def __init__(self, host=None, port=None):
		self.port = port;
		self.srvsock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		self.srvsock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
		self.srvsock.bind( (host, port) )
		self.srvsock.listen( 5 )
		self.descriptors = [self.srvsock]
		self.manage_room = {}
		self.client_room = {}
		self.client_ip = {}
		self.room_sock = {}
		self.log = {}
		self.log['ROOM 1'] = []
		self.log['ROOM 2'] = []
		self.log['ROOM 3'] = []
		self.log['ROOM 4'] = []
		self.log['ROOM 5'] = []
		self.log['ROOM 6'] = []
		self.file = {}
		self.file['ROOM 1'] = []
		self.file['ROOM 2'] = []
		self.file['ROOM 3'] = []
		self.file['ROOM 4'] = []
		self.file['ROOM 5'] = []
		self.file['ROOM 6'] = []
		print 'ChatServer started on port %s' % port

	def run( self ):

		while 1:
			(sread, swrite, sexc) = select.select( self.descriptors, [], [] )
			for sock in sread:

				if sock == self.srvsock:
					self.accept_new_connection()

				else:
					mess = sock.recv(4);

					if mess == '':

						host,port = sock.getpeername()
						if self.client_ip.has_key(str(host) + ':' + str(port)):
							name = self.client_ip[str(host) + ':' + str(port)]
							room = self.client_room[name]

							self.descriptors.remove(sock)
							del self.client_ip[str(host) + ':' + str(port)]
							del self.client_room[name]
							self.manage_room[room].remove(name)
							self.room_sock[room].remove(sock)
							self.refresh_member(sock, room, name)
						else:
							self.descriptors.remove(sock)
						sock.close()

					else:

						i = 0
						while i<len(mess) - 1:
							length = int(mess[i:i+4])
							if length == 0:
								FILEINFO_SIZE = struct.calcsize('128sI')
								fhead = sock.recv(FILEINFO_SIZE)
								i = i + FILEINFO_SIZE
								filename, filesize = struct.unpack('128sI', fhead)
								newname = '/Users/mac/Desktop/计算机网络/chat/file/server/' + filename.strip('\0').split('/')[-1]
								#print newname
								fp = open(newname,'wb')
								restsize = filesize
								print "recving..."
								while 1:
									if restsize > 1024:
										filedata = sock.recv(1024)
									else:
										filedata = sock.recv(restsize)
										fp.write(filedata)
										break
									if not filedata:
										break
									fp.write(filedata)
									restsize = restsize - len(filedata)
									if restsize <= 0:
										break
								fp.close()
								print "recv succeeded: File named:",filename
								host,port = sock.getpeername()
								name = self.client_ip[str(host) + ':' + str(port)]
								room = self.client_room[name]

								prepare_mess = {}
								prepare_mess['room'] = room
								prepare_mess['name'] = name
								prepare_mess['type'] = str(MESSAGE)
								prepare_mess['message'] = 'Upload file: ' + filename.strip('\0').split('/')[-1] + ' by <' + name + '> !' + '(' + datetime.datetime.now().strftime("%H:%M:%S") + ')' + '\n'
								prepare_mess['check'] = hash(str(prepare_mess['message'])) & 0xffff
								length = str(len(str(prepare_mess))).rjust(4,'0')
								self.broadcast_string(sock, length + str(prepare_mess), name, room)

								self.file[room].append(filename.strip('\0').split('/')[-1])
								prepare_mess = {}
								prepare_mess['room'] = room
								prepare_mess['name'] = name
								prepare_mess['type'] = str(ADD_FILE)
								prepare_mess['file'] = filename.strip('\0').split('/')[-1]
								prepare_mess['check'] = hash(str(prepare_mess['file'])) & 0xffff
								length = str(len(str(prepare_mess))).rjust(4,'0')
								self.broadcast_string(sock, length + str(prepare_mess), name, room)

							else:
								i = i + 4
								mess = sock.recv(length)
								message = eval(mess[0:length])
								i = i + length
								if message['type'] == str(INFO):

									if message['check'] != hash(str(message['room'] + message['name'])) & 0xffff:
										print 'ERROR' + mess
										break
									else:
										self.client_room[message['name']] = message['room']

										if message['room'] in self.manage_room:
											self.manage_room[message['room']].append(message['name'])
										else:
											self.manage_room[message['room']] = []
											self.manage_room[message['room']].append(message['name'])

										if message['room'] in self.room_sock:
											self.room_sock[message['room']].append(sock)
										else:
											self.room_sock[message['room']] = []
											self.room_sock[message['room']].append(sock)

										host,port = sock.getpeername()
										self.client_ip[str(host) + ':' + str(port)] = message['name']
										prepare_mess = {}
										prepare_mess['room'] = message['room']
										prepare_mess['name'] = message['name']
										prepare_mess['type'] = str(JOIN)
										prepare_mess['check'] = hash(str(message['room'] + message['name'])) & 0xffff
										length = str(len(str(prepare_mess))).rjust(4,'0')
										self.broadcast_string(sock, length + str(prepare_mess), message['name'], message['room'])

										prepare_mess = {}
										prepare_mess['type'] = str(GET_MEMBER)
										all_member = self.manage_room[message['room']]
										send_member = '\n'.join(all_member)
										prepare_mess['member'] = send_member
										prepare_mess['check'] = hash(str(prepare_mess['member'])) & 0xffff
										length = str(len(str(prepare_mess))).rjust(4,'0')
										self.get_member(sock, length + str(prepare_mess))

								elif message['type'] == str(MESSAGE):

									if message['check'] != hash(str(message['message'])) & 0xffff:
										print 'ERROR' + mess
										break
									else:
										host,port = sock.getpeername()
										name = self.client_ip[str(host) + ':' + str(port)]
										room = self.client_room[name]
										length = str(len(str(message))).rjust(4,'0')
										self.broadcast_string(sock, length + str(message), name, room)

								elif message['type'] == str(LEAVE_ROOM):

									if message['check'] != hash(str(message['type'])) & 0xffff:
										print 'ERROR' + mess
										break

									host,port = sock.getpeername()
									name = self.client_ip[str(host) + ':' + str(port)]
									room = self.client_room[name]

									del self.client_room[name]
									self.manage_room[room].remove(name)
									self.room_sock[room].remove(sock)
									self.refresh_member(sock, room, name)

								elif message['type'] == str(GET_LOG):

									if message['check'] != hash(str(message['type'])) & 0xffff:
										print 'ERROR' + mess
										break

									self.send_log(sock, message)

								elif message['type'] == str(SAVE_LOG):

									if message['check'] != hash(str(message['type'])) & 0xffff:
										print 'ERROR' + mess
										break

									self.send_log(sock, message)

								elif message['type'] == str(GET_FILE):

									if message['check'] != hash(str(message['type'])) & 0xffff:
										print 'ERROR' + mess
										break

									self.file_list(sock, message)

								elif message['type'] == str(DOWNLOAD):

									if message['check'] != hash(str(message['type'])) & 0xffff:
										print 'ERROR' + mess
										break

									self.download_file(sock, message)

	def broadcast_string( self, omit_sock, mess, name, room ):

		all_sock = self.room_sock[room]

		i = 0
		while i<len(mess) - 1:
			length = int(mess[i:i+4])
			i = i + 4
			message = eval(mess[i:i+length])
			i = i + length

			if message['type'] == str(JOIN):

				if message['check'] != hash(str(message['room'] + message['name'])) & 0xffff:
					print 'ERROR' + mess
					break

				for sock in self.descriptors:
					if sock in all_sock:
						if sock != omit_sock:
							prepare_mess = message
							prepare_mess['type'] = str(MEMBER)
							prepare_mess['check'] = hash(str(message['room'] + message['name'])) & 0xffff
							length = str(len(str(prepare_mess))).rjust(4,'0')
							sock.sendall(length + str(prepare_mess))

			elif message['type'] == str(MESSAGE):
				if message['check'] != hash(str(message['message'])) & 0xffff:
					print 'ERROR' + mess
					break

				self.log[self.client_room[message['name']]].append(message['message'])
				for sock in self.descriptors:
					if sock in all_sock:
						length = str(len(str(message))).rjust(4,'0')
						sock.sendall(length + str(message))
				print name + '@' + room +': ' + mess

			elif message['type'] == str(ADD_FILE):
				if message['check'] != hash(str(message['file'])) & 0xffff:
					print 'ERROR' + mess
					break

				for sock in self.descriptors:
					if sock in all_sock:
						length = str(len(str(message))).rjust(4,'0')
						sock.sendall(length + str(message))

	def accept_new_connection( self ):
		newsock, (remhost, remport) = self.srvsock.accept()
		self.descriptors.append( newsock )

	def refresh_member(self, omit_sock, room, name):
		all_sock = self.room_sock[room]
		all_member = self.manage_room[room]
		send_member = '\n'.join(all_member)
		print all_member
		for sock in all_sock:
			if sock != omit_sock:
				prepare_mess = {}
				prepare_mess['type'] = str(REFRESH_MEMBER)
				prepare_mess['message'] = 'Client %s left \n' % (name)
				prepare_mess['member'] = send_member
				prepare_mess['check'] = hash(str(prepare_mess['message'] + prepare_mess['member'])) & 0xffff
				length = str(len(str(prepare_mess))).rjust(4,'0')
				sock.sendall(length + str(prepare_mess))

	def get_member(self, sock, mess):
		sock.sendall(mess)

	def send_log(self, sock, message):

		host,port = sock.getpeername()
		name = self.client_ip[str(host) + ':' + str(port)]
		room = self.client_room[name]
		prepare_mess = {}
		prepare_mess['type'] = message['type']
		prepare_mess['message'] = self.log[room]
		prepare_mess['room'] = room
		prepare_mess['check'] = hash(str(prepare_mess['message'])) & 0xffff
		length = str(len(str(prepare_mess))).rjust(4,'0')
		sock.sendall(length + str(prepare_mess))
		#print length + str(prepare_mess)

	def file_list(self, sock, message):

		host,port = sock.getpeername()
		name = self.client_ip[str(host) + ':' + str(port)]
		room = self.client_room[name]
		prepare_mess = {}
		prepare_mess['type'] = message['type']
		prepare_mess['message'] = self.file[room]
		prepare_mess['room'] = room
		prepare_mess['check'] = hash(str(prepare_mess['message'])) & 0xffff
		length = str(len(str(prepare_mess))).rjust(4,'0')
		print prepare_mess
		sock.sendall(length + str(prepare_mess))

	def download_file(self, sock, message):

		host,port = sock.getpeername()
		path = '/Users/mac/Desktop/计算机网络/chat/file/server/' + message['file_name']
		FILEINFO_SIZE = struct.calcsize('128sI')
		fhead = struct.pack('128sI', str(path), os.stat(path).st_size)
		fp = open(path,'rb')
		sock.sendall('0000' + fhead)
		print "sending over..."
		while 1:
			filedata = fp.read(1024)
			if not filedata:
				break
			else:
				sock.sendall(filedata)
		fp.close()
