# Human-Robot-Negotiation
Human Robot Negotiation Framework that enables a human negotiator to negotiate with a humanoid robot.

## Preparation

### CUDA & CUDNN

Since we utilize CUDA and related deep learning libraries, you must first ensure that they are installed correctly.

- ### CUDA (11.X)
```
https://developer.nvidia.com/cuda-11-7-0-download-archive
```
- ### CUDNN (8.X)
```
https://developer.nvidia.com/cudnn
```

## Python Environment

Install Python 3.10 and Python 2.7 respectively.

Afterward, you only need to install the requirements for Python 3 for the Core, the robots environments are built automatically.

```
pip3 -r requirements.txt --no-deps
```

Please test that the Tensorflow library can utilize the GPU.

```
import tensorflow as tf
tf.config.list_physical_devices('GPU')
```

## Pynaoqi

- Install the C++ compilers for Python 2.7. Download links are removed from the Microsoft website for 2.7, you can download it from the web archieve. The problem and solution is in the stackoverflow comments.

```
https://stackoverflow.com/questions/35118312/microsoft-compilers-for-python-2-7-cant-download-it-what-higher-version-shoul
```

- Follow the instruction on the Aldebaran Website for Nao.
  - For older Nao versions (Prior to v6) and Pepper:
```
  http://doc.aldebaran.com/2-5/dev/python/install_guide.html
```
  - For Nao V6:
```
  http://doc.aldebaran.com/2-8/dev/python/install_guide.html
```
-

### Test if naoqi works in Python 2.7 shell

```bash
  python
  (in python shell) import naoqi
```

## NLTK

If you are first time installing and trying to get a working version, nltk will ask you several times to download some libraries. You can download them from python shell as follows:

```bash
  python
  (in python shell) import nltk
  (in python shell) nltk.download('punkt')
  (in python shell) nltk.download('averaged_perceptron_tagger')
```

## Running the Project

You can start the project by:

```bash
  python -m human_robot_negotiation
```
