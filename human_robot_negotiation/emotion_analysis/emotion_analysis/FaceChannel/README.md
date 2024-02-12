# My Face Channel Module
Our Facial Expression Module for Negotiation

## Requirements
- CUDA 11.0
- Python 3.6 or higher

## Installation
- **Python 3.6**: [Download](https://www.python.org/downloads/release/python-360/)
- **CUDA 11.0**: [Download](https://www.tensorflow.org/install/gpu)
- For necessary Python libraries:
 ```sh
 pip3 install -r requirements.txt
 ```
- Copy checkpoint files into `CLModel/checkpoint/`

## Usage:

You can call necessary function via **GET** or **POST** Requests and they return via **JSON**.

- **Join**
  For generate an experiment, you need to call Join function with an experiment ID:

  ```sh
  http://<IP>:<PORT>/join/<ExperimentID>
  ```

  or to specify Camera ID

  ```sh
  http://<IP>:<PORT>/join/<CameraID>/<ExperimentID>
  ```

  > Note: It should return `{status: True}`
  
- **Start**
  It starts capturing and saves images in LOG_DIR. You need to call Start function with the experiment ID:
  ```sh
  http://<IP>:<PORT>/start/<ExperimentID>
  ```
  
  > Note: It should return `{status: True}`

- **Stop**
  It stops capturing and trains CL Model. It returns the average of prediction. You need to call Stop function with the experiment ID:
  ```sh
  http://<IP>:<PORT>/stop/<ExperimentID>
  ```
  
  > Note: It should return `{status: True, predictions: {Arousal: Float, Valance: Float}}`
  
- **Next**
  This function must be called at the end of first Session. First Session returns prediction of **FaceChannel** while Second Session returns prediction of **CL Model**.
  This function also train **CL Model**, it may take a few minutes to complete.
  You need to call Next function with the experiment ID:
  ```sh
  http://<IP>:<PORT>/next/<ExperimentID>
  ```
  
  > Note: It should return `{status: True}`
  
- **Exit**
  This function closes the Experiment you created. You need to call Exit function with the Experiment ID:
  ```sh
  http://<IP>:<PORT>/exit/<ExperimentID>
  ```
  
  > Note: It should return `{status: True}`
