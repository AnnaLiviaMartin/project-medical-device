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
    "data_dir": "./data",
    "output_dir": "./checkpoints",
    "plot_dir": "./plots",

    "batch_size": 16,
    "num_workers": 4,

    "num_epochs": 25,
    "learning_rate": 1e-4,
    "weight_decay": 1e-4,

    "patience": 5,
    "unfreeze_epoch": 4,

    "num_classes": 14,
    "random_seed": 42,

    "pos_weight_mode": "sqrt",
    "pos_weight_max": 20.0,

    "dropout": 0.25,
}

PIXEL = 448 #224  # Eingangsaufloesung fuer DenseNet-121 (Vergleich 224 vs. 448 getestet)

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]