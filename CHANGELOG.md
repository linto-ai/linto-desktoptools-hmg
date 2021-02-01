# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
- Add Files to dataset from manifest.
- Add Detected samples to dataset.
- Samples smart trimming.
- Noise and noised sample management.
- CRNN and CNN Model Architectures.
- Models layer additions.
- Models dropout and Gaussian Layers. 
- LMFE Features.
- Inference optimizations.

## [1.0.0] - 2021-02-01
New Software architecture. **Projects created with older version will no longer work**. Please create a new project.

### Changed
- Project now support multiple datasets, features and model architectures.
- Complete code overhaul.
- Dependencies including tensorflow latest version.
- Module are now presented as widgets within in the navigation interface.
- All module redevelopped using a new _Module pattern.
- All module now accept multiple profiles

### Added
- Dataset, features, model and trained_model classes.
- Navigation interface
- Added Datasets Management Module
- Export and import existing datasets
- Sample's sampling rate are now not irrelevant as they are automaticly resampled to the target sampling rate.
- FeatToFile and FileToFeat functions.
- Implemented homebrew MFCC feature extraction.
- Remove and/or delete samples (with manifest) function in the evaluate Module.

### Removed
- Removed large chunk of now unused code.

## [0.10] - 2020-02-20
### Added
- Added unroll option at model creation to unroll the GRU layer in order to export TF Lite format. 
- Added tensorflow lite export for unrolled model.

## [0.9hotfix1] - 2020-02-20
### Added
- Add changelog

### Fixed
- Fix #1. Division by zero
