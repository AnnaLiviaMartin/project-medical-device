# convolutional neural network
# nih chest x-ray

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
from torch.autograd import Variable
from os import listdir
import glob
import os
import random
from PIL import Image

csv_path = "./data/Data_Entry_2017.csv"
image_path = "./data/images"

# Gegeben: Bild x/input + Was ist es (y/target) => Dict für Targets, Liste für Images
# Frage: Wie viele Krankheiten?

# Targets einlesen
class PatientDataEntry:
      def __init__(self, line):
            data_points = line.split(",")

            self.image_index = data_points[0]
            self.finding_labels = data_points[1].split("|")
            self.follow_up = data_points[2]
            self.patient_id = data_points[3]
            self.patient_age = data_points[4]
            self.patient_gender = data_points[5]
            self.view_position = data_points[6]
            self.original_image_width = data_points[7]
            self.original_image_height = data_points[8]
            self.original_image_pixel_spacing_x = data_points[9]
            self.original_image_pixel_spacing_y = data_points[10]

            self.classes = [
                  "Atelectasis",
                  "Cardiomegaly",
                  "Effusion",
                  "Infiltration",
                  "Mass",
                  "Nodule",
                  "Pneumonia",
                  "Pneumothorax",
                  "Consolidation",
                  "Edema",
                  "Emphysema",
                  "Fibrosis",
                  "Pleural_Thickening",
                  "Hernia"
            ]

      def add_img_tensor(self, img_tensor):
            self.img_tensor = img_tensor

      def __str__(self):
            return (f"PatientDataEntry(image_index={self.image_index!r}, "
                f"finding_labels={self.finding_labels!r}, follow_up={self.follow_up!r}, "
                f"patient_id={self.patient_id!r}, patient_age={self.patient_age!r}, "
                f"patient_gender={self.patient_gender!r}, view_position={self.view_position!r}, "
                f"original_image_width={self.original_image_width!r}, "
                f"original_image_height={self.original_image_height!r}, "
                f"original_image_pixel_spacing_x={self.original_image_pixel_spacing_x!r}, "
                f"original_image_pixel_spacing_y={self.original_image_pixel_spacing_y!r})")

def create_patient_data_entries():
      """Creates dictionary with key=image name && values=PatienDataEntry"""
      patient_data_entry_list = dict()

      with open(csv_path, encoding='utf-8') as f:
            lines = f.read().split('\n')
            for line in lines:
                  entry = PatientDataEntry(line)
                  patient_data_entry_list[entry.image_index] = entry

      return patient_data_entry_list


# Bilder auf gleich groesse setzen, gleiche breite/hoehe, belichtung normalisieren
normalize = transforms.Normalize(
      mean = [0.485, 0.456, 0.406],
      std = [0.229, 0.224, 0.225]
)
transform = transforms.Compose([
      transforms.Resize(256), 
      transforms.CenterCrop(256),
      transforms.ToTensor(),
      normalize
])

# def pre_process():
#       """Creates dictionary including all data (x, y)"""
#       data = create_patient_data_entries() # add data entries y

#       for name in os.listdir(image_path):
#             full_path = os.path.join(image_path, name)

#             if os.path.isdir(full_path):
#                   print("Subfolder gefunden:", full_path)
#                   for sub_name in os.listdir(full_path):
#                         sub_path = os.path.join(full_path, sub_name)
#                         images = listdir(sub_path)
#                         for image_path in images: # add images
#                               full_image_path = os.path.join(sub_path, image_path)
#                               image = Image.open(full_image_path).convert("RGB")
#                               img_tensor = transform(image)
#                               data[image_path].add_img_tensor(img_tensor)

def create_target_tensor(labels, classes):
      target = torch.zeros(len(classes))

      for label in labels:
            if label == "No Finding":
                  continue

            if label in classes:
                  idx = classes.index(label)
                  target[idx] = 1.0

      return target

def pre_process():
      data = create_patient_data_entries()

      all_image_paths = glob.glob(
            os.path.join(image_path, "**", "*.png"),
            recursive=True
      )

      for image_path in all_image_paths:
            image = Image.open(image_path).convert("RGB")

            image_name = image_path.split("/")[-1]
            img_tensor = transform(image)

            entry = data[image_name]
            entry.add_img_tensor(img_tensor)

            entry.target_tensor = create_target_tensor(
                  entry.finding_labels,
                  entry.classes
            )

      return data

      # training_data_list = []
      # training_data = []
      # target_list = []
      # files = listdir(train_path)
      # for i in range(len(listdir(train_path))):
      #       # zufälliges element aus liste mit dateinamen auswählen
      #       f = random.choice(files)
      #       files.remove(f)

      #       # bild laden zu tensor machen und in liste
      #       #img = Image.open(train_path + f)
      #       img_tensor = transform(img)
      #       training_data_list.append(img_tensor)

      #       # add labels for each image
      #       is_cat = 1 if 'cat' in f else 0
      #       is_dog = 1 if 'dog' in f else 0
      #       target = [is_cat, is_dog]
      #       target_list.append(target)

      #       if len(training_data_list) >= 64: # batch size
      #             training_data.append((torch.stack(training_data_list), target_list)) # liste aus batches die wir durch netz jagen wollen mit targets
      #             training_data_list = []
      #             target_list = []

      #             #print(f"Loaded batch {len(training_data)} of {int(len(listdir(train_path)) / 64)}")
      #             #print(f"Percentage done: {(len(training_data) / (len(listdir(train_path)) / 64) * 100):.2f}%\n")
      #             #break
            
      #return training_data

def devide_train_validation_test():
      pass

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

def train():
      pass

def test():
      """Wie sieht das Ergebnis mit anderen Zahlen aus?"""
      pass

def validate():
      pass

def save_model(net, path="./mein_netz.pt"):
      torch.save(net, path)

def load_model(path="./mein_netz.pt"):
      if os.path.isfile(path):
            net = torch.load(path)
      return net

def main():
      pass

if __name__ == '__main__':
      main()