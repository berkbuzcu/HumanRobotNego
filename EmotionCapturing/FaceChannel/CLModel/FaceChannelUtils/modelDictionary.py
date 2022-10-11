import os

parentDir = "CLModel/"

class CategoricaModel:
    modelname = "Categorical Trained on FER+"
    modelDirectory = os.path.join(parentDir, "TrainedNetworks", "CategoricalFaceChannel.h5")
    modelType = "Categorical"
    classsesOrder = ["Neutral", "Happiness", "Surprise", "Sadness", "Anger", "Disgust", "Fear", "Contempt"]
    classesColor = [(255, 255, 255), (0, 255, 0),  (0, 222, 255), (255, 0, 0), (0, 0, 255), (255, 0, 144), (0, 144, 255), (75, 75, 96)]



class DimensionalModel:
    modelname = "Arousal and Valence Trained on AffectNet"
    modelDirectory = ".\EmotionCapturing\FaceChannel\CLModel\TrainedNetworks\DimensionalFaceChannel.h5"
    modelType = "Dimensional"
    classsesOrder = ["Arousal", "Valence"]
    classesColor = [(0, 255, 0), (255, 0, 0)]







        # ["'0':'Neutral',", "'1':'Surprise',", "'2':'Sad',", "'3':'Disgust',", "'4':'Angry',", "'5':'Fear',", "'6':'Happy',"]
