import torch
from torchvision import transforms

class Model():
	def __init__(self, model_path):
		self.model = torch.load(model_path)]
		self.model.eval()
	def preprocess(self,im):
		pass
		#returns a tensor which is the model input provided to the forward function
	def forward(self, modelinput):		
		pass
		#returns raw output, also usually a tensor
