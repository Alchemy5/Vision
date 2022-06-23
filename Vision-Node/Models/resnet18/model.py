import torch
from torchvision import transforms
import torch.nn as nn
class Model():
	def __init__(self, model_path): #path to .pth file, define model arch. inside of this function
		
		self.model = torch.load(model_path)
		self.model.eval()	
	def preprocess(self,im):
		image_height = 224
		image_width = 224
		im = im.resize((image_width, image_height))
		preprocess = transforms.Compose([transforms.Resize(image_height), transforms.CenterCrop(224), transforms.ToTensor(), transforms.Normalize(mean = [0.485, 0.456, 0.406], std=[0.229,0.224,0.225])]) 
		im = preprocess(im)
		tensor = torch.unsqueeze(im,0)
		return tensor

	def forward(self, modelinput):
		out = self.model(modelinput)
		return out
	
	

