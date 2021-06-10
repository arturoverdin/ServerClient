import socket
import argparse
import signal
import sys

from threading import Thread


def signal_handler(signal, frame):
    print("terminating client...", flush=True)
    sys.exit()


class messageThread(Thread):

    def __init__(self, ip, name):
        Thread.__init__(self)
        self.ip = ip
        self.name = name

    def run(self):

        while True:
            data = sock.recv(1024)
            DATA_NEW = data.decode('utf-8').split()
            MESSAGE = ""
            RECV = DATA_NEW[0]

            if RECV == "recvfrom":

                SENDER_NAME = str(DATA_NEW[1])
                del DATA_NEW[0]
                del DATA_NEW[0]

                for x in DATA_NEW:
                    if x == DATA_NEW[len(DATA_NEW) - 1]:
                        MESSAGE = x + MESSAGE
                    else:
                        MESSAGE = x + MESSAGE + " "
                print(SENDER_NAME + ": " + MESSAGE, flush=True)


if __name__ == "__main__":

    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", required=True
                        , help="Add port number to run server on."
                        , type=int)

    parser.add_argument("-s", required=True
                        , help="Chat server IP address.")

    parser.add_argument("-n", required=True
                        , help="Name of the client")

    args = parser.parse_args()

    UDP_IP = args.s
    UDP_PORT = args.p
    CLIENT_NAME = args.n

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    REGISTER = "register " + CLIENT_NAME
    REGISTER = REGISTER.encode('utf-8')

    sock.sendto(REGISTER, (UDP_IP, UDP_PORT))

    data, addr = sock.recvfrom(1024)
    DATA_NEW = data.decode('utf-8')
    SUCC_REG = "welcome " + CLIENT_NAME

    if DATA_NEW == SUCC_REG:
        print("connected to server and registered " + CLIENT_NAME, flush=True)
        newThread = messageThread(UDP_IP, CLIENT_NAME)
        newThread.daemon = True
        newThread.start()

        while True:
            RAW_MESSAGE = input("")
            PROC_MESSAGE = RAW_MESSAGE.split()

            if RAW_MESSAGE == 'exit':
                print("terminating client...", flush=True)
                break
            elif PROC_MESSAGE[0] == "sendto":
                MESSAGE = RAW_MESSAGE.encode('utf-8')
                sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))