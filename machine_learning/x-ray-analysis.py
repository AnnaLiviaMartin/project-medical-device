# convolutional neural network
# nih chest x-ray

import torch
import os
from nih_train import train, evaluate_on_test
from nih_visualize import visualise_all
from constants import CONFIG

def save_model(model, path="./checkpoints/cnn_state_dict_end.pt"):
    torch.save(model.state_dict(), path)

if __name__ == "__main__":
    # Training starten
    model = train(CONFIG)

    # Finale Evaluation auf dem Test-Set
    evaluate_on_test(CONFIG)

    save_model(model)

    # Ergebnisse visualisieren
    visualise_all()