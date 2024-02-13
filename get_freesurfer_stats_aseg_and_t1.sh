#!/bin/bash -i


# load the required modules

# loading ANTs
module load ANTs

# preparing freesurfer
module load freesurfer/6.0.0
source /appl/freesurfer-6.0.0/SetUpFreeSurfer.sh

export FS_LICENSE=/project/davis_group/elicorn/images_pmacs/license.txt

export SURFER_FRONTDOOR=1

# specifying the target directories
# freesurfer_dir=/project/davis_group_1/group_projects/structural_cat/outputs/freesurfer/
freesurfer_dir=$1

freesurfer_out_dir=./aseg_and_stats_pier/

# Assuming the subjects are listed in subjects.txt, one subject per line
subject_file="subjects.txt"
subject_list=()

counter=0
max_iterations=2

# Read the subject file line by line
for freesurfer_dir_subject in "$freesurfer_dir"/sub*; do

    if [ -d "$freesurfer_dir_subject" ]; then
        subject=$(basename "$(dirname "$freesurfer_dir_subject/temp")")

        echo "Processing subject: $subject"

        sub_dir_aseg=${freesurfer_out_dir}${subject}

        mkdir -p $sub_dir_aseg

        source_aseg=${freesurfer_dir_subject}/mri/aparc.DKTatlas+aseg.mgz
        
        out_aseg_conform=${sub_dir_aseg}/${subject}_aparc.DKTatlas+aseg_freesurfer-space.nii.gz
        
        out_aseg_native_mgz=${sub_dir_aseg}/${subject}_aparc.DKTatlas+aseg_native.mgz

        out_aseg_native=${sub_dir_aseg}/${subject}_aparc.DKTatlas+aseg_native.nii.gz
        
        source_t1=${freesurfer_dir_subject}/mri/rawavg.mgz

        source_t1_conformed_fully_processed=${freesurfer_dir_subject}/mri/T1.mgz

        source_t1_conformed_fully_processed_skullstripped=${freesurfer_dir_subject}/mri/brainmask.mgz
        
        out_t1_conformed_fully_processed=${sub_dir_aseg}/${subject}_T1_processed_freesurfer-space.nii.gz

        out_t1_conformed_fully_processed_skullstripped=${sub_dir_aseg}/${subject}_brainmask_processed_freesurfer-space.nii.gz

        # convert the aseg file to native space (from freesurfer conformed space)

        mri_label2vol --seg $source_aseg --temp $source_t1 --o $out_aseg_native_mgz --regheader $source_aseg

        # convert the .mgz file to a nifti file
        
        # convert the freesurfer space files
        mri_convert $source_aseg $out_aseg_conform

        # convert the native files
        mri_convert $out_aseg_native_mgz $out_aseg_native
        
        # copy and convert the T1.mgz and brainmask.mgz, both in freesurfer space

        mri_convert $source_t1_conformed_fully_processed $out_t1_conformed_fully_processed

        mri_convert $source_t1_conformed_fully_processed_skullstripped $out_t1_conformed_fully_processed_skullstripped

        # copy the stats directory

        source_stats=${freesurfer_dir_subject}/stats

        cp -r $source_stats $sub_dir_aseg

        # add completed patient to subject list
        subject_list+=("$subject")

    fi

    ((counter++))

    if [ "$counter" -gt "$max_iterations" ]; then
        echo "Breaking out of the loop."
        break
    fi

done

python compute_features.py "$freesurfer_out_dir" "${subject_list[@]}"