# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
- Tool for trimming and normalizing audio samples.

## [0.10] - 2020-02-20
### Added
- Added unroll option at model creation to unroll the GRU layer in order to export TF Lite format. 
- Added tensorflow lite export for unrolled model.

## [0.9hotfix1] - 2020-02-20
### Added
- Add changelog

### Fixed
- Fix #1. Division by zero
