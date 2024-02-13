import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import accuracy_score
import os
from sklearn.model_selection import KFold
import nibabel as nib
from nibabel import freesurfer as nfs
import numpy as np
from sklearn.metrics import confusion_matrix

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score

from sklearn.model_selection import GridSearchCV, KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

import matplotlib.pyplot as plt
from tqdm import tqdm

from sklearn.decomposition import PCA
from sklearn.metrics import classification_report

# myscript.py
import sys

# Get input list from command line
if len(sys.argv) > 1:
    freesurfer_dir = sys.argv[1]
    subjects = sys.argv[2:]
    # print(f"Received input list: {subjects}")
    # print(f"Received input list: {freesurfer_dir}")
else:
    print("No input list provided.")

# change this directory to the aseg_and_stats from PIER or CAPES
# freesurfer_dir = '/mnt/leif/littlab/users/allucas/CNT_borel/Q16_ML_epilepsy/source_data/aseg_and_stats'
# freesurfer_dir = '/mnt/leif/littlab/users/allucas/CNT_borel/Q16_ML_epilepsy/source_data/aseg_and_stats_pier'
# subjects = os.listdir(freesurfer_dir)
# subjects = list(set(subjects)-{'sub-EMOC0004'})
# subjects = [x for x in subjects if x[0]!='.']

print('Subjects to analyze: ', len(subjects))

def compute_cortical_intensity_features(subject, freesurfer_dir):
    # Load the T1w image and aparc+aseg segmentation
    t1w_img = nib.load(f"{freesurfer_dir}/{subject}/{subject}_T1_processed_freesurfer-space.nii.gz")
    aparc_aseg_img = nib.load(f"{freesurfer_dir}/{subject}/{subject}_aparc.DKTatlas+aseg_freesurfer-space.nii.gz")
    
    t1w_data = t1w_img.get_fdata()
    aparc_aseg_data = aparc_aseg_img.get_fdata()
    
    # Find unique labels in the desired range
    unique_labels = np.unique(aparc_aseg_data[(aparc_aseg_data > 1000) & (aparc_aseg_data < 3000) & (aparc_aseg_data != 2000)])

    true_label_pth = 'dtk_atlas_labels.txt'
    with open(true_label_pth) as f:
        lines = [line.rstrip('\n') for line in f]
    lines = [x.split(', ') for x in lines]
    true_labels = {int(lines[i][0]): "_".join(lines[i][1].split(" ")) for i in range(len(lines))}

    cortical_intensity_features = {}

    # Compute mean intensity for each label
    for label in unique_labels:
        mask = aparc_aseg_data == label
        mean_intensity = np.mean(t1w_data[mask])
        
        cortical_intensity_features[f"{true_labels[label]}_mean_intensity"] = mean_intensity

    # Compute asymmetry
    for label in unique_labels:
        if label > 1000 and label < 2000:
            left_key = f"{true_labels[label]}_mean_intensity"
            right_key = f"{true_labels[label+1000]}_mean_intensity"
            asym_key = true_labels[label].split("left_")[1]
            
            if left_key in cortical_intensity_features and right_key in cortical_intensity_features:
                asymmetry = (cortical_intensity_features[left_key] - cortical_intensity_features[right_key]) / (cortical_intensity_features[left_key] + cortical_intensity_features[right_key])
                cortical_intensity_features[f"{asym_key}_intensity_asymmetry"] = asymmetry

    return cortical_intensity_features


def compute_intensity_features(subject, freesurfer_dir):
    # Load the T1w image and aparc+aseg segmentation
    t1w_img = nib.load(f"{freesurfer_dir}/{subject}/{subject}_T1_processed_freesurfer-space.nii.gz")
    aparc_aseg_img = nib.load(f"{freesurfer_dir}/{subject}/{subject}_aparc.DKTatlas+aseg_freesurfer-space.nii.gz")
    
    t1w_data = t1w_img.get_fdata()
    aparc_aseg_data = aparc_aseg_img.get_fdata()
    
    # Define the labels of interest (from the aparc+aseg) - adjust these as needed
    labels_of_interest = extract_labels_from_files(freesurfer_dir, subject)
    
    intensity_features = {}

    # Compute mean and std for each label
    for label, name in labels_of_interest.items():
        mask = aparc_aseg_data == label
        masked_intensity = t1w_data[mask]
        
        mean_intensity = np.mean(masked_intensity)
        std_intensity = np.std(masked_intensity)
        
        intensity_features[f"{name}_mean_intensity"] = mean_intensity
        intensity_features[f"{name}_std_intensity"] = std_intensity

    # Calculate asymmetry
    paired_structures = [("Left-Caudate", "Right-Caudate"),
        ("Left-Putamen", "Right-Putamen"),
        ("Left-Thalamus-Proper", "Right-Thalamus-Proper"),
        ("Left-Pallidum", "Right-Pallidum"),
        ("Left-Hippocampus", "Right-Hippocampus"),
        ("Left-Amygdala", "Right-Amygdala")]
    
    for left_structure, right_structure in paired_structures:
        left_mean_key = f"{left_structure}_mean_intensity"
        right_mean_key = f"{right_structure}_mean_intensity"
        
        left_std_key = f"{left_structure}_std_intensity"
        right_std_key = f"{right_structure}_std_intensity"
        
        if left_mean_key in intensity_features and right_mean_key in intensity_features:
            mean_asymmetry = (intensity_features[left_mean_key] - intensity_features[right_mean_key]) / \
                             (intensity_features[left_mean_key] + intensity_features[right_mean_key])
            intensity_features[f"{left_structure.split('-')[1]}_mean_intensity_asymmetry"] = mean_asymmetry
            
        if left_std_key in intensity_features and right_std_key in intensity_features:
            std_asymmetry = (intensity_features[left_std_key] - intensity_features[right_std_key]) / \
                            (intensity_features[left_std_key] + intensity_features[right_std_key])
            intensity_features[f"{left_structure.split('-')[1]}_std_intensity_asymmetry"] = std_asymmetry

    return intensity_features



def extract_labels_from_files(freesurfer_dir, subject):
    aseg_file_path = f"{freesurfer_dir}/{subject}/stats/aseg.stats"
    
    labels_of_interest = {}
    
    # Extract labels from aseg.stats
    with open(aseg_file_path, 'r') as file:
        for line in file:
            if not line.startswith("#"):
                data = line.split()
                index = int(data[1])  # This column contains the index
                region_name = data[4]  # This column contains the region name
                labels_of_interest[index] = region_name
    
    return labels_of_interest

def extract_features(subject, freesurfer_dir):
    # File paths for cortical and subcortical stats
    lh_file_path = f"{freesurfer_dir}/{subject}/stats/lh.aparc.DKTatlas.stats"
    rh_file_path = f"{freesurfer_dir}/{subject}/stats/rh.aparc.DKTatlas.stats"
    aseg_file_path = f"{freesurfer_dir}/{subject}/stats/aseg.stats"
    
    features = {}
    
    # Helper function to process each hemisphere file
    def process_cortical_file(file_path, hemisphere_prefix):
        thickness_values = {}
        volume_values = {}

        with open(file_path, 'r') as file:
            lines = file.readlines()

        for line in lines:
            if not line.startswith("#"):
                data = line.split()
                region_name = data[0]
                avg_thickness = float(data[4])
                gray_vol = float(data[2])
                
                # Prefix region name with hemisphere and feature type
                thickness_values[f"{hemisphere_prefix}_{region_name}_thickness"] = avg_thickness
                volume_values[f"{hemisphere_prefix}_{region_name}_vol"] = gray_vol

        # Update main feature dictionary
        features.update(thickness_values)
        features.update(volume_values)

    def process_aseg_file(file_path):
        volumes = {}

        with open(file_path, 'r') as file:
            lines = file.readlines()

        for line in lines:
            if not line.startswith("#"):
                data = line.split()
                structure_name = data[4]
                volume = float(data[3])
                volumes[f"{structure_name}_vol"] = volume

        # Update main feature dictionary
        features.update(volumes)

    # Process cortical measures for both hemispheres and subcortical measures
    process_cortical_file(lh_file_path, "lh")
    process_cortical_file(rh_file_path, "rh")
    process_aseg_file(aseg_file_path)

    # Calculate asymmetry for cortical thickness and volume
    for region in [x.split("_")[1] for x in features.keys() if ('lh' in x) and ('thickness' in x)]:
        lh_thickness_key = f"lh_{region}_thickness"
        rh_thickness_key = f"rh_{region}_thickness"
        lh_vol_key = f"lh_{region}_vol"
        rh_vol_key = f"rh_{region}_vol"

        if lh_thickness_key in features and rh_thickness_key in features:
            thickness_asymmetry = (features[lh_thickness_key] - features[rh_thickness_key]) / \
                                  (features[lh_thickness_key] + features[rh_thickness_key])
            features[f"{region}_thickness_asymmetry"] = thickness_asymmetry

        if lh_vol_key in features and rh_vol_key in features:
            vol_asymmetry = (features[lh_vol_key] - features[rh_vol_key]) / \
                           (features[lh_vol_key] + features[rh_vol_key])
            features[f"{region}_vol_asymmetry"] = vol_asymmetry

    # Calculate asymmetry for subcortical volumes
    subcortical_pairs = [
        ("Left-Caudate", "Right-Caudate"),
        ("Left-Putamen", "Right-Putamen"),
        ("Left-Thalamus-Proper", "Right-Thalamus-Proper"),
        ("Left-Pallidum", "Right-Pallidum"),
        ("Left-Hippocampus", "Right-Hippocampus"),
        ("Left-Amygdala", "Right-Amygdala")
        # Add more pairs as needed
    ]
    
    for left_structure, right_structure in subcortical_pairs:
        left_key = f"{left_structure}_vol"
        right_key = f"{right_structure}_vol"

        if left_key in features and right_key in features:
            asymmetry = (features[left_key] - features[right_key]) / \
                        (features[left_key] + features[right_key])
            asymmetry_key = f"{left_structure.split('-')[1]}_asymmetry"
            features[asymmetry_key] = asymmetry
    
    
    # include subcortical intensity features
    intensity_features = compute_intensity_features(subject, freesurfer_dir)
    
    features.update(intensity_features)

    # include cortical intensity features
    cortical_intensity_features = compute_cortical_intensity_features(subject, freesurfer_dir)
    
    features.update(cortical_intensity_features)
    
    return features

# Extract features (thickness and volume) for all subjects
data_list = []

subjects_succeeded = []
subjects_failed = []

for subject in tqdm(subjects):
    try:
        features = extract_features(subject, freesurfer_dir)
        data_list.append(features)
        subjects_succeeded.append(subject)
    except FileNotFoundError:
        subjects_failed.append(subject)

# Since we're adding a new set of features, we need to extract region names again.
sample_features = extract_features(subjects[0], freesurfer_dir)
all_feature_names = list(sample_features.keys())

df = pd.DataFrame(data_list, columns=all_feature_names)
df['Subject'] = subjects_succeeded

df.to_pickle('freesurfer_features.p')
