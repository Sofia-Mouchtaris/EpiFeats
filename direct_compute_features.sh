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

# parce inputs
while getopts "i:o:r:" option; do
    case $option in
        o) # output directory
            ofl=true
            freesurfer_out_dir="$OPTARG"
        ;;
        r) # results doc
            rfl=true
            outcomes_file="$OPTARG"
        ;;
    esac
done

if [[ $ofl != true ]]; then
    echo "you must specify an directory with -o"
    exit 1
fi

if [[ $rfl != true ]]; then
    outcomes_file=./junk
fi

# freesurfer_dir=$1
# freesurfer_out_dir=./aseg_and_stats_pier/

# Assuming the subjects are listed in subjects.txt, one subject per line
subject_file="subjects.txt"
subject_list=()

# Read the subject file line by line
for freesurfer_dir_subject in "$freesurfer_out_dir"/sub*; do

    if [ -d "$freesurfer_dir_subject" ]; then
        subject=$(basename "$(dirname "$freesurfer_dir_subject/temp")")
        subject_list+=("$subject")

    fi

done

python compute_features.py "$freesurfer_out_dir" "$outcomes_file" "${subject_list[@]}"
python run_xgboost.py "$outcomes_file" 


