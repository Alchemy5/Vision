from socket import socket, gethostbyname, AF_INET, SOCK_DGRAM, SOCK_STREAM
import sys
import struct
import cv2
import os
from PIL import Image as PILImage
import numpy as np
import json
class Node():
	#initialization of values required for socket communication
	def __init__(self):
		self.local_port = 5004
		self.size = 1024
		self.server_port = int(input("Enter server port number: "))
		self.local_host = gethostbyname( '0.0.0.0' )
		self.server =  ('10.163.146.153', self.server_port)
		self.s = socket(AF_INET, SOCK_STREAM)
		self.success = 1
	#helper functions for reading messages
	def recv_msg(self,sock):
		raw_msglen = self.recvall(sock, 4)
		msglen = struct.unpack('>I', raw_msglen)[0]
		return self.recvall(sock,msglen)
	def recvall(self,sock,n):
		data = bytearray()
		while len(data) < n:
			packet = sock.recv(n-len(data))
			data.extend(packet)
		return data
	#main function
	def connect(self):
		try:
			self.s.connect(self.server)
			print("Connected")
		except:
			raise Exception("Exception: Connection failed, check whether manager class has been instantiated and try again")
		
		video = cv2.VideoCapture('/dev/video0')
		while True:
			command = self.s.recv(1024) #main command: take image, end node, inferencing
			print(command.decode())
			command = command.decode()
			
			if command == "take image":
				try:
					print("Taking image")
					_,frame=video.read()
					frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
					image = PILImage.fromarray(frame,'RGB')
					r = np.array(image.getdata())
					data = r.tostring().decode('ISO-8859-1')
					shape = r.shape
					dtype = str(r.dtype)
					r = json.dumps({ 'success':self.success,'data':data,'shape':shape,'dtype':dtype})
					msg = r
					msg = struct.pack('>I',len(msg)) + bytes(msg, encoding = 'utf-8')
					self.s.sendall(msg)
				except:
					self.success = 0
					r = json.dumps({'success':self.success})
					msg = r
					msg = struct.pack('>I',len(msg)) + bytes(msg, encoding = 'utf-8')
					self.s.sendall(msg)
					video.release()
					raise Exception("Take image command failed to execute")
					
			elif command == "end node":
				break

			elif command == "inferencing":
				try:
					import torchvision.models as models
					import torch
					from torchvision import transforms
					
					msg = "Send me the .json config file"
					self.s.sendall(msg.encode())
					data = self.recv_msg(self.s)
					config = json.loads(data)
					print(config)
					if config['custom'] == True: #custom model
						try:
							model_str = config['model']
							model_path = 'Models/' + model_str + '/model.pth'
							#model = torch.load(model_path)
							os.chdir('Models')
							os.chdir(model_str)
							from model import Model
							os.chdir(os.path.expanduser("~"))
							os.chdir('Vision-Node')
							model_functions = Model(model_path)
							while True:
								_,frame = video.read()
								frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
								image = PILImage.fromarray(frame,'RGB')
								tensor = model_functions.preprocess(image)
								out = model_functions.forward(tensor)
								r = out.detach().numpy()
								data = r.tostring().decode('ISO-8859-1')
								shape = r.shape
								dtype = str(r.dtype)
								r = json.dumps({ 'success':self.success,'data':data,'shape':shape,'dtype':dtype})
								msg = r
								msg = struct.pack('>I',len(msg)) + bytes(msg, encoding = 'utf-8')
								self.s.sendall(msg) #sends model output to manager (main computer)
						except:
							self.success = 0
							r = json.dumps({'success':self.success})
							msg = r
							msg = struct.pack('>I',len(msg)) + bytes(msg, encoding = 'utf-8')
							self.s.sendall(msg)
							
							video.release()
							raise Exception("Inferencing with custom model failed")
					elif config['custom'] == False: #standard PyTorch model
						try:
							model = config['model'] #resnet18, vgg16, etc.
							image_height = config['height']
							image_width = config['width']
							#standard preprocess function
							preprocess = transforms.Compose([transforms.Resize(image_height), transforms.CenterCrop(224), transforms.ToTensor(), transforms.Normalize(mean = [0.485, 0.456, 0.406], std=[0.229,0.224,0.225])]) 
							
							full_string = 'models.' + model + '(pretrained=True)'
							model = eval(full_string)
							while True:
								_,frame = video.read()
								frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB) #color conversion from cv2 to PIL
								image = PILImage.fromarray(frame,'RGB')
								im = image.resize((image_width,image_height))
								im = preprocess(im)
								tensor = torch.unsqueeze(im,0)
							
								model.eval()
								out = model(tensor)
								with open('imagenet_classes.txt') as f:
									labels=[line.strip() for line in f.readlines()] 
								_, index = torch.max(out,1)
								final = labels[index[0]]
								self.s.sendall(final.encode()) #sends model output to manager (main computer)
						except:
							self.success = 0
							msg = "Inferencing with model failed"
							self.s.sendall(msg.encode())
							video.release()
							raise Exception("Inferencing with model failed")

				except:
					video.release()
					raise Exception("Inferencing failed")




				

