import numpy

from tensorflow.keras.models import load_model, Model
from tensorflow.keras.layers import Input

from .imageProcessingUtil import imageProcessingUtil
from .metrics import *

import os


#os.environ["CUDA_VISIBLE_DEVICES"] = "0"

#from keras import backend as K

class modelLoader:

    IMAGE_SIZE = (64,64)
    BATCH_SIZE = 32

    GPU = '/gpu:0' #'/cpu:0'

    @property
    def modelDictionary(self):
        return self._modelDictionary

    @property
    def model(self):
        return self._model

    @property
    def dataLoader(self):
        return self._dataLoader


    def __init__(self, modelDictionary, printSummary=True):

        self._modelDictionary = modelDictionary
        self._dataLoader = imageProcessingUtil()

        self.loadModel(printSummary=printSummary)


    def loadModel(self, printSummary=True):

        self._model = load_model(self.modelDictionary.modelDirectory, custom_objects={'fbeta_score': fbeta_score, 'rmse': rmse, 'recall': recall, 'precision': precision, 'ccc': ccc})
        if printSummary:
            self._model.summary()


    def classify(self, image):

        classification = self.model.predict(numpy.array([image]),batch_size=self.BATCH_SIZE, verbose=0)

        return classification

    def get_dense_model(self):
        denseLayerOutput = self.model.get_layer(name="denseLayer").output

        classifier = Model(inputs=self.model.inputs, outputs=[denseLayerOutput])

        return classifier

    def getDense(self, image):
        denseLayerOutput = self.model.get_layer(name="denseLayer").output

        classifier = Model(inputs=self.model.inputs, outputs=[denseLayerOutput])

        denseRepresentation = classifier.predict(numpy.array([image]), batch_size=self.BATCH_SIZE)

        return denseRepresentation


