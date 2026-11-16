import os
import pandas as pd
import streamlit as st

import config


def get_dataset_path(file_name):
    candidates = [
        os.path.join(config.DATA_DIR, file_name),
        os.path.join(config.PROJECT_ROOT, "Data", file_name),
        os.path.join(config.PROJECT_ROOT, "data", file_name),
    ]

    for file_path in candidates:
        if os.path.exists(file_path):
            return file_path

    return candidates[0]


# ============================================
# Load Single Dataset
# ==================================

@st.cache_data(show_spinner=False)
def load_dataset(file_name):
    file_path = get_dataset_path(file_name)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset not Found: {file_path}")

    return pd.read_csv(file_path, low_memory=False)


# ===========================================
# Load All Datasets
# ===========================================

def load_all_datasets(file_names):
    datasets = {}

    for key, file_name in config.DATASET_FILES.items():
        try:
            datasets[key] = load_dataset(file_name)
        except FileNotFoundError:
            datasets[key] = None

    return datasets


# ==========================================
# check if all datasets are available
# ==========================================

def get_dataset_status():
    status = {}

    for key, file_name in config.DATASET_FILES.items():
        file_path = get_dataset_path(file_name)
        status[key] = os.path.exists(file_path)

    return status
