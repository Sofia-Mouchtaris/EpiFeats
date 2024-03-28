<h1>EpiFeats</h1>

EpiFeats is a simple toolbox that automatically extracts features (included cortical thickness, cortical and subcortical volumetry, T1w intensity, and left-right asymmetries of these) from FreeSurfer outputs, allowing researchers to have a baseline set of standardized features that they can test their own biomarkers and models against.

<h2>Running the pipeline</h2>
<h3>Installing the conda environment</h3>

Please make sure you have Anaconda installed. First clone the directory then import the conda environment. After cloning, open the repository folder in a terminal window and type:

```
git clone https://github.com/penn-cnt/EpiFeats.git
cd EpiFeats
conda env create -f environment.yml
```

This will create a new Python virtual environment with all the required libraries. To activate the environment:

```
conda activate epifeats
```

<h3>To run the full EpiFeats pipeline:</h3>

```
bash run_full_pipeline.sh \
    -i /path/to/freesurfer/ \ # required
    -o /path/to/desired/output/folder/ \ # optional; if not given, will write to current directory
    -r /path/to/results/doc.csv # optional
```

To start from computing features (if pipeline failed on compilation of features):
```
bash direct_compute_features.sh \
    -o /path/to/compiled/freesurfer/data/ \ # required; same as -o from original run
    -r /path/to/results/doc.csv # optional
```
