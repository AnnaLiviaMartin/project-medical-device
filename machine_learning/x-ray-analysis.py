# convolutional neural network
# nih chest x-ray

from nih_train import train, evaluate_on_test
from nih_visualize import visualise_all
from constants import CONFIG

if __name__ == "__main__":
    # Training starten
    model = train(CONFIG)

    # Finale Evaluation auf dem Test-Set
    evaluate_on_test(CONFIG)

    # Ergebnisse visualisieren
    visualise_all()