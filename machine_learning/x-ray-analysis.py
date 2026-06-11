# convolutional neural network
# nih chest x-ray

import torch
import os
from nih_train import train, evaluate_on_test
from constants import CONFIG

if __name__ == "__main__":
    # Training starten
    #model = train(CONFIG)

    # Finale Evaluation auf dem Test-Set
    evaluate_on_test(CONFIG)

def save_model(net, path="./cnn.pt"):
    torch.save(net, path)

def load_model(path="./cnn.pt"):
    if os.path.isfile(path):
        net = torch.load(path)
    return net
