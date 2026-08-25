PATHOLOGY_LIST = [
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
] # + No Finding

NUM_CLASSES = len(PATHOLOGY_LIST)  # 14

CONFIG = {
    "data_dir":    "./data",
    "output_dir":  "./checkpoints",
    "plot_dir":    "./plots",
    "batch_size":  32,
    "num_workers": 4,
    "num_epochs":  10,
    "learning_rate": 1e-4,
    "weight_decay":  1e-5,
    "patience":      3,      # Early Stopping: Epochen ohne Verbesserung
    "num_classes":   14,
    "random_seed":   42,
}

PIXEL = 320 #224  # Bildgröße für ResNet-Modelle

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]