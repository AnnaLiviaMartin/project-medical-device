# convolutional neural network
# nih chest x-ray

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import transforms
import glob
import os
import random
from PIL import Image
from sklearn.metrics import classification_report, roc_auc_score
import numpy as np

csv_path = "./data/Data_Entry_2017_backup.csv"
image_path = "./data/images"

class PatientDataEntry:
      def __init__(self, line):
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
                  "Hernia",
                  "No Finding"
            ] # 15 Klassen
            data_points = line.split(",")

            self.image_index = data_points[0]
            self.targets = multi_hot_encoding(data_points[1], self.classes)
            self.follow_up = data_points[2]
            self.patient_id = data_points[3]
            self.patient_age = data_points[4]
            self.patient_gender = data_points[5]
            self.view_position = data_points[6]
            self.original_image_width = data_points[7]
            self.original_image_height = data_points[8]
            self.original_image_pixel_spacing_x = data_points[9]
            self.original_image_pixel_spacing_y = data_points[10]

      def add_img_tensor(self, img_tensor):
            self.img_tensor = img_tensor

      def __str__(self):
            return (f"PatientDataEntry(image_index={self.image_index!r}, "
                f"patient_id={self.patient_id!r}, patient_age={self.patient_age!r}, "
                f"patient_gender={self.patient_gender!r}, view_position={self.view_position!r}, "
                f"original_image_width={self.original_image_width!r}, "
                f"original_image_height={self.original_image_height!r}, "
                f"original_image_pixel_spacing_x={self.original_image_pixel_spacing_x!r}, "
                f"original_image_pixel_spacing_y={self.original_image_pixel_spacing_y!r}, "
                f"target={self.targets!r}, img_tensor={self.img_tensor!r})")

def multi_hot_encoding(labels, classes):
      target = torch.zeros(len(classes))

      for label in labels.split("|"):
            if 'Finding Labels' in label:
                  continue
            if label in classes:
                  idx = classes.index(label)
                  target[idx] = 1.0
            else:
                  print(f"ERROR: Desease not recognized: {label}.")
                  exit()

      return target

def create_patient_data_entries():
      """Creates dictionary with key=image name && values=PatienDataEntry"""
      patient_data_entry_list = dict()

      with open(csv_path, encoding='utf-8') as f:
            lines = f.read().split('\n')
            for line in lines:
                  if line.startswith("#"):
                        continue
                  entry = PatientDataEntry(line)
                  patient_data_entry_list[entry.image_index] = entry

      return patient_data_entry_list


# Bilder auf gleich groesse setzen, gleiche breite/hoehe, belichtung normalisieren
normalize = transforms.Normalize(
      mean=[0.5],
      std=[0.5]
)
transform = transforms.Compose([
      transforms.Resize(224),
      transforms.CenterCrop(224),
      transforms.ToTensor(),
      normalize
])

def pre_process(image_path):
      data = create_patient_data_entries()

      all_image_paths = glob.glob(
            os.path.join(image_path, "**", "*.png"),
            recursive=True
      )

      for idx, image_path in enumerate(all_image_paths, start=1):
            image = Image.open(image_path).convert("L") # laden als Graustufenbild

            #image_name = image_path.split("\\")[-1]#windows
            image_name = image_path.split("/")[-1]#mac
            img_tensor = transform(image)

            entry = data[image_name]
            entry.add_img_tensor(img_tensor)

            entry.target_tensor = entry.targets

            print(f"Loaded {idx} / {len(all_image_paths)} images")
            print(f"Percentage done: {(idx / len(all_image_paths) * 100):.2f}%\n")

      return data

# training_batches => [ train1, train2, ... ] => train1 mit 64 items => [batch_images, batch_targets]
def create_batches(data, batch_size=64):
      training_batches = []
      batch_images = []
      batch_targets = []
      total_batches = (len(data) + batch_size - 1) // batch_size


      for entry in data.values():
            batch_targets.append(entry.targets)
            batch_images.append(entry.img_tensor)

            if len(batch_images) >= batch_size:
                  training_batches.append((torch.stack(batch_images) , torch.stack(batch_targets)))

                  batch_images = []
                  batch_targets = []

                  print(f"Loaded batch {len(training_batches)} of {total_batches}")
                  print(f"Percentage done: {(len(training_batches) / total_batches * 100):.2f}%\n")

      # Reste-Batch (optional, falls noch Bilder übrig)
      if len(batch_images) > 0:
            training_batches.append((torch.stack(batch_images), torch.stack(batch_targets)))
            
            print(f"Loaded batch {len(training_batches)} of {total_batches}")
            print(f"Percentage done: {(len(training_batches) / total_batches * 100):.2f}%\n")

      return training_batches


def divide_train_validation_test(data,
                                 train_ratio=0.7,
                                 validation_ratio=0.15,
                                 test_ratio=0.15):

      data_list = list(data.values())

      random.shuffle(data_list)

      total_size = len(data_list)

      train_end = int(total_size * train_ratio)
      validation_end = train_end + int(total_size * validation_ratio)

      train_data = data_list[:train_end]
      validation_data = data_list[train_end:validation_end]
      test_data = data_list[validation_end:]

      return train_data, validation_data, test_data

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        # Block 1: 256x256 -> MaxPool -> 126x126
        self.conv1 = nn.Conv2d(1, 16, kernel_size=5, padding=2) 
        
        # Block 2: 126x126 -> MaxPool -> 61x61
        self.conv2 = nn.Conv2d(16, 32, kernel_size=5, padding=2)
        self.conv_dropout = nn.Dropout2d(0.1)
        
        # Block 3: 61x61 -> MaxPool -> 29x29
        self.conv3 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        
        # Block 4: 29x29 -> MaxPool -> 13x13
        self.conv4 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        
        # Der Fully Connected Layer erwartet jetzt 128 Kanäle * 1x1 Pixel = 128 Eingänge
        self.fully_connected1 = nn.Linear(128 * 1 * 1, 64)
        self.fully_connected2 = nn.Linear(64, 15)

    def forward(self, x):
        # Block 1
        x = F.relu(F.max_pool2d(self.conv1(x), 2))
        
        # Block 2
        x = self.conv2(x)
        x = self.conv_dropout(x)
        x = F.relu(F.max_pool2d(x, 2))
        
        # Block 3
        x = F.relu(F.max_pool2d(self.conv3(x), 2))
        
        # Block 4
        x = F.relu(F.max_pool2d(self.conv4(x), 2))

        # KORREKTUR: Global Average Pooling (reduziert jede Feature Map auf 1x1 Pixel)
        x = F.adaptive_avg_pool2d(x, (1, 1))

        # Flattening (x.size(0) ist die Batch-Größe, -1 flacht den Rest zu 128 ab)
        x = x.view(x.size(0), -1)

        x = F.relu(self.fully_connected1(x))
        x = self.fully_connected2(x)
        return x

def calculate_pos_weights(training_data_entries):
    """
    Berechnet die pos_weight Tensoren basierend auf den echten Trainingsdaten.
    training_data_entries: Liste oder Dict deiner PatientDataEntry-Objekte
    """
    num_classes = 15
    pos_counts = torch.zeros(num_classes)
    neg_counts = torch.zeros(num_classes)
    
    for entry in training_data_entries:
        targets = entry.targets  # Das ist dein Multi-Hot-Tensor der Größe 15
        pos_counts += targets
        neg_counts += (1.0 - targets)
        
    # Verhindere Division durch 0, falls eine Krankheit extrem selten ist (wird zu 1.0)
    pos_counts = torch.clamp(pos_counts, min=1.0)
    
    # Berechne das Verhältnis Nullen / Einsen
    pos_weights = neg_counts / pos_counts
    
    return pos_weights

def train(epoch, net, training_data, optimizer, pos_weights):
      # Stochastic Gradient Descent, learning rate 0.01
      net.train()
      pos_weights = pos_weights.cuda() if torch.cuda.is_available() else pos_weights
        
      criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weights)

      for batch_idx, (data, target_list) in enumerate(training_data):
            # auf Grafikkarte abspielen
            data = data.cuda() if torch.cuda.is_available() else data
            target = target_list.float() # multi-hot encoding
            target = target.cuda() if torch.cuda.is_available() else target

            optimizer.zero_grad()  # Gradienten auf 0 setzen, d.h. normalisieren
            output = net(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()

            print(f"Train Epoch: {epoch} [{batch_idx * len(data)}/{len(training_data)} ({100. * batch_idx / len(training_data):.0f}%)]\tLoss: {loss.item():.6f}")

# def test(net, test_data):
#     net.eval()
#     correct_elements = 0
#     total_elements = 0

#     with torch.no_grad():
#         for data, targets in test_data:
#             data = data.cuda() if torch.cuda.is_available() else data
#             targets = targets.float().cuda() if torch.cuda.is_available() else targets.float()
#             print(f"Data targets: {targets}")

#             output = net(data)
#             print(f"Model output: {output}")
#             probabilities = torch.sigmoid(output)
#             predictions = (probabilities > 0.5).float()
            
#             # Das ist die Element-wise Accuracy (Achtung vor dem "Nullen-Bias"!)
#             correct_elements += (predictions == targets).sum().item()
#             total_elements += targets.numel()

#     accuracy = 100 * correct_elements / total_elements
#     print(f"\nTest Element-wise Accuracy: {accuracy:.2f}%\n")

def test(net, test_data):
    net.eval()
    
    all_targets = []
    all_predictions = []
    all_probabilities = []

    with torch.no_grad():
        for data, targets in test_data:
            data = data.cuda() if torch.cuda.is_available() else data
            targets = targets.float().cuda() if torch.cuda.is_available() else targets.float()

            output = net(data)
            probabilities = torch.sigmoid(output)
            predictions = (probabilities > 0.5).float()
            
            # Daten für die Gesamtanalyse sammeln
            all_targets.append(targets.cpu().numpy())
            all_predictions.append(predictions.cpu().numpy())
            all_probabilities.append(probabilities.cpu().numpy())

    # Batches zusammenfügen
    y_true = np.vstack(all_targets)
    y_pred = np.vstack(all_predictions)
    y_prob = np.vstack(all_probabilities)

    # Zeigt dir exakt Precision, Recall und F1-Score für jede der 15 Klassen!
    print("\n--- Detaillierter Klassifikationsbericht ---")
    # zero_division=0 verhindert Warnungen, wenn eine Klasse nie vorhergesagt wird
    print(classification_report(y_true, y_pred, zero_division=0)) 
    
    # Der medizinische Standard: ROC-AUC Score
    try:
        macro_auc = roc_auc_score(y_true, y_prob, average='macro')
        print(f"Macro ROC-AUC Score: {macro_auc:.4f}  (0.5 ist pures Raten, 1.0 ist perfekt)")
    except ValueError:
        # Falls im Testset für eine Klasse keine einzige 1 existiert
        print("ROC-AUC konnte nicht berechnet werden (fehlende Klassenvarianz im Test-Batch).")

def validate(net, validation_data, pos_weights):
    net.eval()
    
    pos_weights = pos_weights.cuda() if torch.cuda.is_available() else pos_weights  
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weights)
    
    validation_loss = 0.0
    total_samples = 0  # Zählt die echten Bilder

    with torch.no_grad():
        for data, targets in validation_data:
            data = data.cuda() if torch.cuda.is_available() else data
            targets = targets.float().cuda() if torch.cuda.is_available() else targets.float()

            output = net(data)
            loss = criterion(output, targets)
            
            validation_loss += loss.item() * data.size(0)
            total_samples += data.size(0)

    average_loss = validation_loss / total_samples
    print(f"\nValidation Loss: {average_loss:.6f}\n")

def save_model(net, path="./rnn.pt"):
      torch.save(net, path)

def load_model(path="./rnn.pt"):
      if os.path.isfile(path):
            net = torch.load(path)
      return net

def main():
      # Daten vorverarbeiten: alles in Dictionary packen, Bilder in Tensoren umwandeln, Bilder auf gleiche Größe bringen, Normalisieren
      data = pre_process(image_path)
      print(data["00000001_001.png"])

      # Trainingsdaten in Batches aufteilen
      train_entries, validation_entries, test_entries = divide_train_validation_test(data)

      pos_weights = calculate_pos_weights(train_entries)
      print(f"Berechnete pos_weights für die 15 Klassen:\n{pos_weights}\n")

      training_data = create_batches({e.image_index: e for e in train_entries})
      validation_data = create_batches({e.image_index: e for e in validation_entries})
      test_data = create_batches({e.image_index: e for e in test_entries})

      print(training_data[0][0].size())

      # Netz erstellen
      net = Net()
      #net = load_model()
      net.cuda() if torch.cuda.is_available() else net
      optimizer = optim.Adam(net.parameters(), lr=0.001)

      for epoch in range(1, 30):
            train(epoch, net, training_data, optimizer, pos_weights)
            validate(net, validation_data, pos_weights)

      test(net, test_data)
      save_model(net)

if __name__ == '__main__':
      main()