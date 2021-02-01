![version](https://img.shields.io/github/manifest-json/v/linto-ai/hmg)

# Hotword Model Generator
HMG is a GUI tool designed to generate keyword spotting models.

**DISCLAIMER: This is an rough version of a tool that haven't beed thoroughly tested, bug may (and probably will) occur. Please use the issue tracker to report them.**

## Introduction
HMG allows you to:
* Manage datasets
* Tune audio features
* Tune model architecture and training parameters
* Train your model
* Evaluate your model
* Test your model
* Export your model
__________________

## Getting Started

### Release
Not available for now

### From Source
You can use the software from the repository.

**Prerequisites**

System dependencies:

* You need ```python3.x``` and ```python3-pip``` installed.
* you need ```portaudio19-dev``` package installed

There is a number of dependencies needed to run the software.
They can be found in the ```requirements.txt``` file at the repository root.

We recommend that you use a virtual environement.
```bash
source /my/virtual/env/bin/activate #Optionnal but advised
cd $(REPO_ROOT)
pip install -r requirements.txt
```

You can launch the program by running either:
```bash
python $(REPO_ROOT)/model_generator/main.py
# or
./$(REPO_ROOT)/model_generator/main.py
```
__________________

## Usage

1. Create a project and specify your keyword(s).
2. Create a dataset
3. Create a feature profile
4. Create a model architecture
5. Create a trained model and train it
6. Evaluate your model
7. Export your model

__________________
## Built using

* [Qt](https://www.qt.io/) - Cross-platform software development for embedded GUI
* [PyQt](https://riverbankcomputing.com/software/pyqt/intro) - Python binding for Qt
* [Tensorflow](https://www.tensorflow.org) - An open source machine learning library for research and production

__________________
## License
This project is licensed under the GNU AFFERO License - see the [LICENSE.md](LICENSE.md) file for details.
