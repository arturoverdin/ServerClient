Arturo Verdin
6590836368
CSCI353
Programming Assignment 1
Multithreaded UDP/TCP server and client.


Server: 
	Handling UDP:

	The server handled any incoming UDP traffic and automatically creates a thread for 
	the data coming in. It registered users by using a vector that keeps track of client 
	IP's and ports.


	Handling TCP:
	Servers can only connect to other servers using TCP. This was achieved by forking a new thread 
	so that the server can continuously listen for incoming connections on one port. They then would
	accept any incoming connections and create a new thread that takes care of the message content. 
	I would keep the socket connection in a vector. Similarly, if instead the server is actively
	trying to connect to another server then it will attempt to connect (we assume a server is
	already listening and waiting for a connection). In that case, the server adds the socket
	connection to the vector and forks a new thread that is ready to recieve a message. 
	
Client: 

	The client is straightfoward. Wait for user input. Fork off a thread to recieve and 
	print any data from the server. If it receives user input then it sends data. Rinse 
	and repeat. 
