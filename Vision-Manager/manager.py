import json
from socket import gethostbyname, AF_INET, SOCK_DGRAM, SOCK_STREAM
from socket import socket as socket_function
import numpy as np
import struct
from PIL import Image
import socket

class Manager():
    def __init__(self):
        self.configuration = None
        self.camera_type = None
        self.image_size = None
        self.port = int(input("Enter server port number: "))
        self.msg_size = 1024
        self.cur_sock = None
        self.client_address = None
        host = gethostbyname('0.0.0.0')
        self.s = socket_function(AF_INET, SOCK_STREAM)
        import socket
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        self.s.bind((host, self.port))
        self.s.listen(5)
        while True:
            print("No nodes are detected as of yet") #waiting for node to connect to manager object
            self.cur_sock, self.client_address = self.s.accept()
            if self.cur_sock != None and self.client_address != None:
                print("Connection created")
                break

        
    #communication helper functions
    def deserialize(self,msg):
        msg = json.loads(msg)
        arr = np.frombuffer(msg['data'].encode('ISO-8859-1'), dtype=msg['dtype'])
        arr = np.reshape(arr, msg['shape'])
        return arr
    
    def recv_msg(self, sock):
        # Read message length and unpack it into an integer
        raw_msglen = self.recvall(sock, 4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        # Read the message data
        return self.recvall(sock, msglen)

    def recvall(self, sock, n):
        # Helper function to recv n bytes or return None if EOF is hit
        data = bytearray()
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data
    #get sample image to see if node camera pipeline is working 
    def takeImage(self):
        if self.cur_sock is None:
            raise Exception("No client currently connnected!")
        msg = "take image"
        self.cur_sock.sendall(msg.encode())
        print("Waiting for numpy array")
        data_json= self.recv_msg(self.cur_sock)
        data = json.loads(data_json)



        if data['success'] == 0:
            self.end()
            raise Exception("Node failed to take image")
        else:
            data = self.deserialize(data_json)
            print(data)
            inp = input("Save Image? Type Y for Yes and N for No")
            if (inp == 'Y'):
                data = data.reshape(480,640,3)
                data = data.astype(np.uint8)
                im = Image.fromarray(data)
                im = im.save(r"testImage.jpg")
                print("Image has been saved in your local directory")
    #main inferencing function to run inferencing on the node and recieve outputs from node
    def inference(self):
        #first sends a string to tell the node what is happening
        #then sends json config file containing all instructions
        msg = "inferencing"
        self.cur_sock.sendall(msg.encode())
        reply = self.cur_sock.recv(1024)
        print(reply.decode())
        x = input("Enter the path to the config .json file here: ")
        f = open(x)
        data = json.load(f)
        custom = data['custom']
        model = data['model']
        if custom == False:
            image_height = data['height']
            image_width = data['width']

        data = json.dumps(data)
        msg = struct.pack('>I', len(data)) + bytes(data, encoding='utf-8')
        f.close()
        self.cur_sock.sendall(msg)
        try:
            while True:
                if (custom == False):
                    reply = self.cur_sock.recv(1024)
                    reply = reply.decode()
                    if reply == "Inferencing with model failed":
                        self.end()
                        raise Exception("Inferencing with model has stopped")
                    else:
                        print(reply) #prints model outputs, imagenet.txt labels
                elif(custom == True):
                    data_json = self.recv_msg(self.cur_sock)
                    data = json.loads(data_json)
                    if data['success'] == 0:
                        self.end()
                        raise Exception("Inferencing with custom model has stopped")
                    else:
                        data = self.deserialize(data_json)
                        print(data) #prints model outputs, tensors
        except:
            self.end()
            raise Exception("Inferencing has stopped")

    def end(self): #cleanup function
        msg = "end node"
        self.cur_sock.sendall(msg.encode())
        self.s.close()
        self.cur_sock.close()
