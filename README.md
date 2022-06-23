# A Distributed Vision-Based Pipeline
## Prerequsites
One or more Jetson Nano boards with the following packages (code may work with other package versions than those listed):
* socket
* sys
* cv2 - 4.5.5
* os
* PIL - 8.4.0
* numpy - 1.19.5
* json
* torch - 1.8.0
* torchvision - 0.9.0

Make sure all Nanos (nodes) are connected to USB camera modules

A PC with the following packages:
* json
* socket
* numpy - 1.19.5
* struct
* PIL - 8.4.0

## User Implementation Guidelines
1. Copy the Vision-Node folder into your Jetson Nano home directory (you will get an error if it is in any directory besides home) and copy the Vision-Manager folder into your PC home directory. Make sure to keep the folder names the same. Make sure to keep all user-generated test scripts within these respective directories. 
2. Run these commands to create an instance of the Manager class:  
`from manager import Manager`  
`manager = Manager()`  
`#prompt to enter desired port number`  
3. Next, connect a node object to the Manager object created earlier (run these commands from the client side):  
`from node import Node`  
`node = Node()`  
`#prompt to enter desired port number, same number as entered for manager`  
`node.connect() #on the manager side, you should see a printout stating that a connection has been created`  
4. Before running inferencing, first test whether the node's camera pipeline is functioning using the takeImage() function. 
`manager.takeImage()`  
`#prompt asking user if they want to save the image`  
5. When running inferencing, you can either run a [standard pretrained classification model](https://pytorch.org/vision/stable/models.html) or run a custom model. You need to create a config .json file before running inferencing and store it inside of the Vision-Manager folder. Example config files are provided (test.json, test2.json). When running a standard model, this should be what your config file looks like:  
`{"custom":false,"model":{name of model, e.g. (resnet18, alexnet, vgg16}, "height":{integer value specifying height of images taken as input by model, "width":{integer value specifying width of images taken as input by model}}`  
Note: When specifying model name, ensure that the name is equal (characterwise) to the torchvision constructors (e.g. "resnet18" not ResNet18)  
6. When running a custom model, your config file looks a bit different:  
`{"custom":true, "model":{name of folder in Vision-Node/Models directory}`  
7. When running custom models, you have to create a folder with the name of your model in the Vision-Node/Models directory. Inside of this folder, you have to put the [.pth file to the entire model, not the state_dict .pth file](https://pytorch.org/tutorials/beginner/saving_loading_models.html) and rename it model.pth. Then, a template is provided for a python file you must create in this folder named model.py. Inside of this file, you should have a class called Model and two functions which you can provide custom definitions to (preprocess, forward). Again, a template and example is provided for what a custom model directory should look like. 
8. In order to actually run inferencing, use this command from the manager terminal:
`manager.inference()`  
`#prompt asking user for the name of the config file (e.g. 'test.json')`  
`#online inferencing should start and outputs are printed in the manager terminal`  
9. Before exiting out of the manager terminal, always make sure to run the `manager.end()` command, since this will close all pipelines. After an inferencing session is over, you will have to create a new manager instance and new node instance for another session. Also, you can use two or more seperate manager and node instances (each node instance will be instantiated on a different Jetson Nano) to run inferencing on multiple nodes at the same time. 
