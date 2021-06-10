import socket
import argparse
import signal
import sys
from threading import Thread

clients = []
servers = []


def signal_handler(signal, frame):

	print("terminating server...", flush=True)
	sys.exit()

class Client:

	def __init__(self, ip, port, name):
		self.ip = ip
		self.name = name
		self.port = port


class TCPReceive(Thread):
	def __init__(self, conn):
		Thread.__init__(self)
		self.conn = conn

	def run(self):

		while True:

			data = self.conn.recv(1024)

			if not data: break

			DATA_NEW = data.decode('utf-8').split()
			ORIGINAL = data.decode('utf-8')
			CLIENT_SENDER = DATA_NEW[0]
			CLIENT_RECEIVE = DATA_NEW[2]
			CLIENT_RECEIVE = CLIENT_RECEIVE[:-1]
			del DATA_NEW[0]
			del DATA_NEW[0]
			del DATA_NEW[0]

			MESSAGE = ''
			for x in DATA_NEW:
				MESSAGE = x + " " + MESSAGE

			print("Received from overlay server: " + ORIGINAL, flush=True)

			for x in clients:

				if x.name == CLIENT_RECEIVE:

					#print(CLIENT_SENDER + " to " + CLIENT_RECEIVE + ":" + MESSAGE, flush=True)
					MESSAGE = "recvfrom" + " " + CLIENT_SENDER + " " + MESSAGE
					MESSAGE = MESSAGE.encode('utf-8')

					sock.sendto(MESSAGE, (x.ip, x.port))
				else:

					for s in servers:
						s.send(data)


class TCPListen(Thread):

	def __init__(self, tcpsock, address):
		Thread.__init__(self)
		self.tcpsock = tcpsock
		self.address = address

	def run(self):
		print('server overlay started at port %s' % self.address[1], flush=True)

		self.tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.tcpsock.bind(self.address)
		self.tcpsock.listen(1)

		while True:
			connection, client_address = tcpsock.accept()
			servers.append(connection)

			print("server overlay connection from host " + client_address[0] + " port " + str(client_address[1]), flush=True)

			tcpThread = TCPReceive(connection)
			tcpThread.daemon = True
			tcpThread.start()


class ClientThread(Thread):

	def __init__(self, data, addr, sock):
		Thread.__init__(self)
		self.data = data
		self.addr = addr
		self.sock = sock

	def run(self):

		DATA_NEW = self.data.decode('utf-8').split()

		# registration process
		if DATA_NEW[0] == 'register':

			CLIENT_IP = str(self.addr[0])
			CLIENT_PORT = int(self.addr[1])
			CLIENT_NAME = DATA_NEW[1]

			print(CLIENT_NAME + " registered from host " + CLIENT_IP + " port " + str(CLIENT_PORT), flush=True)

			SUCC_REG = "welcome " + CLIENT_NAME
			SUCC_REG = SUCC_REG.encode('utf-8')

			self.sock.sendto(SUCC_REG, (CLIENT_IP, CLIENT_PORT))

			newClient = Client(CLIENT_IP, CLIENT_PORT, CLIENT_NAME)
			clients.append(newClient)

		elif DATA_NEW[0] == 'sendto':

			CLIENT_SEND = ''
			CLIENT_REC = str(DATA_NEW[1])
			CLIENT_REC_IP = ''
			CLIENT_REC_PORT = ''
			MESSAGE = ""
			CLIENT_EXISTS = False

			# figure out if client exists and what their address is
			for x in clients:
				if x.name == CLIENT_REC:
					CLIENT_EXISTS = True
					CLIENT_REC_IP = x.ip
					CLIENT_REC_PORT = x.port

			# figure out the name of the sender through their port
			for x in clients:
				if x.port == addr[1]:
					CLIENT_SEND = x.name

			if CLIENT_EXISTS:

				del DATA_NEW[0]
				del DATA_NEW[0]
				for x in DATA_NEW:
					if x == DATA_NEW[len(DATA_NEW) - 1]:
						MESSAGE = x + MESSAGE
					else:
						MESSAGE = x + MESSAGE + " "

				print(CLIENT_SEND + " to " + CLIENT_REC + ": " + MESSAGE, flush=True)

				MESSAGE = "recvfrom" + " " + CLIENT_SEND + " " + MESSAGE
				MESSAGE = MESSAGE.encode('utf-8')

				self.sock.sendto(MESSAGE, (CLIENT_REC_IP, CLIENT_REC_PORT))

			else:

				del DATA_NEW[0]
				del DATA_NEW[0]
				MESSAGE = ""
				for x in DATA_NEW:
					if x == DATA_NEW[len(DATA_NEW) - 1]:
						MESSAGE = x + MESSAGE
					else:
						MESSAGE =  x + MESSAGE + " "

				MESSAGE = CLIENT_SEND + " to " + CLIENT_REC + ": " + MESSAGE

				print(MESSAGE, flush=True)
				print(CLIENT_REC + " is not registered with server", flush=True)

				if servers:
					print("Sending message to overlay server: " + MESSAGE, flush=True)
					MESSAGE = MESSAGE.encode('utf-8')

				for sock in servers:
					sock.send(MESSAGE)


if __name__ == "__main__":

	# takes care of the SIGINT
	signal.signal(signal.SIGINT, signal_handler)

	# takes care of all the arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("-p", required=True
						, help="Add port number to run server on."
						, type=int)

	parser.add_argument("-s", help="IP address of the overlay server, for which you want to connect to. Optional.")

	parser.add_argument("-t", help="Port number of the overlay server, for which you want to connect to. Optional"
						, type=int)

	parser.add_argument("-o", help="Port number used for TCP connetions from other servers. Optional"
						, type=int)

	args = parser.parse_args()

	IP = "127.0.0.1"
	UDP_PORT = args.p

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((IP, UDP_PORT))

	print("server started on 127.0.0.1 at port %s" % UDP_PORT, flush=True)
	try:
		if args.o:
			# Create a TCP/IP socket
			tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			server_address = (IP, args.o)
			newThread = TCPListen(tcpsock, server_address)
			newThread.daemon = True
			newThread.start()

		if args.t and args.s:
			outsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			outsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			server_address = (str(args.s), args.t)
			outsock.connect(server_address)

			print("connected to overlay server at 127.0.0.1 port " + str(server_address[1]), flush=True)

			servers.append(outsock)

			newThread = TCPReceive(outsock)
			newThread.daemon = True
			newThread.start()

		threads = []
		while True:
			data, addr = sock.recvfrom(1024)
			newThread = ClientThread(data, addr, sock)
			newThread.daemon = True
			newThread.start()
			threads.append(newThread)
	except KeyboardInterrupt:
		for x in servers:
			x.close()