# first convolutional network

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
from torch.autograd import Variable

class Net(nn.Module):
      def __init__(self):
            super(Net, self).__init__()
            self.conv1 = nn.Conv2d(1, 10, kernel_size=5) # 1 bild reinkommen, 10 bilder output -> bilder werden kleiner/zusammengefasst, kernel size=>25 pixel werden zusammengefasst auf einen output pixel
            self.conv2 = nn.Conv2d(10, 20, kernel_size=5)
            self.conv_dropout = nn.Dropout2d() # vergessen einzelner Pixel aber nicht des ganzen Bildes, damit das Netz nicht zu sehr auf bestimmte Pixel fixiert ist (memorizing)
            self.fully_connected1 = nn.Linear(320, 60) # 320 weil 20 Bilder mit je 4x4 Pixeln
            self.fully_connected2 = nn.Linear(60, 10) # am Ende 10 Klassen, von 0-9 für die jeweiligen Zahlen

      def forward(self, x):
            x = self.conv1(x)
            x = F.max_pool2d(x, 2)
            x = F.relu(x) # ReLU: wenn kleiner 0 dann 0, wenn größer 0 dann x
            x = self.conv2(x)
            x = self.conv_dropout(x)
            x = F.max_pool2d(x, 2)
            x = F.relu(x)
            # jetzt mehr infos benötigt
            #print(x.size())
            #exit()
            x = x.view(-1, 320)
            x = self.fully_connected1(x)
            x = F.relu(x)
            x = self.fully_connected2(x)
            return F.log_softmax(x, dim=1) # dim musste ich ergänzen

def train(epoch, model, optimizer, training_data):
      model.train()
      for batch_idx, (data, target) in enumerate(training_data): # Liste von training_data durchgehen mit batch id und 64x tupel von data und target
            # auf Grafikkarte abspielen
            data = data.cuda() if torch.cuda.is_available() else data
            target = target.cuda() if torch.cuda.is_available() else target
            data = Variable(data)
            target = Variable(target)

            optimizer.zero_grad() # Gradienten auf 0 setzen, d.h. normalisieren

            # daten durch model jagen
            output = model(data)

            # loss berechnen
            criterion = nn.CrossEntropyLoss()
            loss = criterion(output, target)
            loss.backward() # backpropagation
            optimizer.step() # update weights
            print(f"Train Epoch: {epoch} [{batch_idx * len(data)}/{len(training_data.dataset)} ({100. * batch_idx / len(training_data):.0f}%)]\tLoss: {loss.item():.6f}")

def main():
      kwargs = {'num_workers': 1, 'pin_memory': True} if torch.cuda.is_available() else {}
      # unique für diesen Datensatz
      training_data = torch.utils.data.DataLoader(
            datasets.MNIST('./mnist_image_recognition/data', train=True, download=True,
                        transform=transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])),
            batch_size=64, shuffle=True, **kwargs) # shuffles the data so no memorizing, batches of 64 pieces

      test_data = torch.utils.data.DataLoader(
            datasets.MNIST('./mnist_image_recognition/data', train=False,
                        transform=transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])),
            batch_size=64, shuffle=True, **kwargs)
      
      model = Net()
      model.cuda() if torch.cuda.is_available() else model

      # Stochastic Gradient Descent, learning rate 0.01
      optimizer = optim.SGD(model.parameters(), lr=0.1, momentum=0.8)
      
      for epoch in range(1, 5):
            train(epoch, model, optimizer, training_data)

      # Evaluation
      test(model, test_data)

def test(model, test_data):
      model.eval()
      loss = 0
      correct = 0
      for data, target in test_data:
            data = data.cuda() if torch.cuda.is_available() else data
            target = target.cuda() if torch.cuda.is_available() else target
            with torch.no_grad():
                  output = model(data)

            # loss berechnen
            loss += F.nll_loss(output, target, reduction='sum').item()
            prediction = output.data.max(1, keepdim=True)[1]
            correct += prediction.eq(target.data.view_as(prediction)).cpu().sum()

      loss = loss / len(test_data.dataset)
      print(f"\nTest set: Average loss: {loss:.4f}")
      print(f"Test set: Accuracy: {100. * correct / len(test_data.dataset):.0f}%\n")

if __name__ == '__main__':
      main()