pip3 -r requirements.txt --no-deps

python3 -m human_robot_negotiation

# Human-Robot-Negotiation
Human Robot Negotiation Framework that enables a human negotiator to negotiate with a nao humanoid robot.

## RUNNING A NEGOTIATION SESSION

### Before starting

Nao's IP address changes everytime it opens, so the code. Go to ```/Agent_Interaction_Models/robot_action.py``` and change the IP address accordingly. Example:

```
  self.robotIP = "169.254.15.237"
```

After that you can start by:

```bash
  python main.py
```

If you are running and trying it the first time, check the NLTK title in troubleshooting section.

## INSTALLING

### Python - Virtual Env

Create a virtual environment with python version 2.7 (If going to use red nao, python version should be 32-bit, otherwise use default 64-bit).

### Requirements

In the created virtual environment, now you can install requirements.

```bash
  pip install -r requirements.txt
```

### Pynaoqi

Download pynaoqi from aldebaran website.

For older nao versions (red nao in our case):

```
  http://doc.aldebaran.com/2-5/dev/python/install_guide.html
```

For newer nao versions (v6, gray one in our case):

```
  http://doc.aldebaran.com/2-8/dev/python/install_guide.html
```

After downloading, add its lib folder to PYTHONPATH in the system environment variables. If you are asking yourself what is PYTHONPATH, check the troubleshooting section.

For newer version of nao (v6, gray one):

```
  "C:\pynaoqi-python2.7-2.8.7.4-win64-vs2015\lib"
```

For older version of nao (red one):

```
"C:\pynaoqi-python2.7-2.5.5.5-win32-vs2013\lib"
```

To check whether it is success or not, simply go into python shell and import the library (Don't forget to activate the virtual environment).

```bash
  python
  (in python shell) import naoqi
```

## TROUBLESHOOTING

### C++ compilers for Python 2.7

If you are lacking c++ compilers for python 2.7 (You will probably lack if you are installing from zero). The download links are removed from microsoft website for 2.7, you can download it from the web archieve. The problem and solution is in the stackoverflow comments.

```
https://stackoverflow.com/questions/35118312/microsoft-compilers-for-python-2-7-cant-download-it-what-higher-version-shoul
```

### NLTK

If you are first time installing and trying to get a working version, nltk will ask you several times to download some libraries. You can download them from python shell as follows:

```bash
  python
  (in python shell) import nltk
  (in python shell) nltk.download('punkt')
  (in python shell) nltk.download('averaged_perceptron_tagger')
```

### Adding naoqi to PYTHONPATH

If you are on Windows, go to 'Search' -> 'Edit the system environment variables' -> Click on 'Environment Variables...' -> Check if there is a variable called 'PYTHONPATH' in user variables -> If there is one, double click on it -> Click on 'New' -> Add the path as that is shown in Naoqi section example.

-> If there is not 'PYTHONPATH', click on 'New' -> Set variable name 'PYTHONPATH' -> Set variable value the path as that is shown in Naoqi section example. Now you are good to go!

