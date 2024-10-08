# -*- coding: utf-8 -*-
"""transfer_learning_on_ECoG.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/15aSagee6VxDslD9JukcZ6alFXmNXRrKt
"""

#Import functions
import torch
import torchvision
import cv2
import torch.optim as optim
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt
import pdb
import torchvision.transforms as transforms
from scipy.signal import convolve2d
import os
import pandas as pd
from torch.utils.data import DataLoader, Subset
from torchvision.datasets import ImageFolder
from sklearn.model_selection import train_test_split

from google.colab import drive
drive.mount('/content/drive')

transform=transforms.Compose([transforms.ToTensor(),transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))])

# Path to the directory containing your dataset
data_dir = '/content/drive/MyDrive/Herron_lab/Neural_data/MPC_MSC_data'

# Create a PyTorch dataset using ImageFolder
dataset = ImageFolder(root=data_dir, transform=transform)
train_indices, test_indices = train_test_split(list(range(len(dataset))), test_size=0.2, random_state=42)

# Create train and test subsets using DataLoader
train_loader = DataLoader(Subset(dataset, train_indices), batch_size=4, shuffle=True)
test_loader = DataLoader(Subset(dataset, test_indices), batch_size=4, shuffle=False)

model = torchvision.models.resnet50(pretrained=True)


model.avgpool =nn.Sequential(nn.Conv2d(2048,1024, kernel_size = (1,1), stride = (1,1), padding ='same'),
                              nn.ReLU(),
                              nn.Dropout(0.5),
                              nn.Conv2d(1024,256,kernel_size=(1,1), stride = (1,1), padding ='same'),
                              nn.ReLU(),
                              nn.Dropout(0.5),
)
                              # nn.Linear(4 * 4 * 32, 1024),
                              # nn.ReLU(inplace = True),
                              # nn.Dropout(),
                              # nn.Dropout(0.5),
                              # nn.Flatten()

                              # )
# model.fc = nn.Identity()
model.fc = nn.Sequential(nn.Linear(in_features = 1024, out_features=3),
                         nn.Sigmoid()
                         )


model.load_state_dict(torch.load('/content/drive/MyDrive/Herron_lab/Neural_data/weights_EEG/Resnet_eegepoch.pth'))

model.fc = nn.Sequential(nn.Linear(in_features=12544, out_features = 2, bias = True),
                         nn.Sigmoid())

for param in model.parameters():
    param.requires_grad=True
for param in model.avgpool.parameters():
  param.requires_grad=True
for param in model.fc.parameters():
    param.requires_grad=True

transform=transforms.Compose([transforms.ToTensor(),transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))])
epochs=10
lr=0.001
momentum=0.9
batch_size=4
optimizer=optim.SGD(model.parameters(),lr=lr,momentum=momentum)
criterion = nn.CrossEntropyLoss()

correct = 0
total = 0
for epoch in range(epochs):  # loop over the dataset for 2 iteration
        running_loss = 0.0
        for i, data in enumerate(train_loader, 0):
            # get the inputs; data is a list of [inputs, labels]
            inputs, labels = data
            inputs, labels = inputs, labels
            # zero the parameter gradients
            optimizer.zero_grad()

            # forward + backward + optimize
            inputs = inputs
            outputs = model(inputs)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            # print statistics
            running_loss += loss.item()
            # if i % 2000 == 1999:    # print every 2000 mini-batches
            #     print(f'[{epoch + 1}, {i + 1:5d}] loss: {running_loss / 2000:.3f}')
            #     running_loss = 0.0
        print(f'epoch : {epoch + 1}, loss:{running_loss/len(train_loader)} ')
        print(f'Accuracy of the epoch {epoch + 1}: {100 * correct // total} %')
        print('-'*200)



print('Finished Training')

correct = 0
total = 0
# since we're not training, we don't need to calculate the gradients for our outputs
with torch.no_grad():
    for data in test_loader:
        images, labels = data
        inputs, labels = inputs, labels
        # calculate outputs by running images through the network
        outputs = model(images)
        # the class with the highest energy is what we choose as prediction
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

print(f'Accuracy of the network on the test images: {100 * correct // total} %')
