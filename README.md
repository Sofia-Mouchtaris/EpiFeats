To run full pipeline:
```
bash run_full_pipeline.sh \
    -i /path/to/freesurfer/ \ # required
    -o /path/to/desired/output/folder/ \ # optional; if not given, will write to current directory
    -r /path/to/results/doc.csv # optional
```

To start from computing features (if pipeline failed on compilation of features):
```
bash direct_compute_features.sh \
    -o /path/to/desired/output/folder/ \ # required; same as -o from original run
    -r /path/to/results/doc.csv # optional
```
