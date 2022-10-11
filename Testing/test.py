# #!/usr/bin/env python3
#
import time

# import speech recognition modules.

import difflib

encoding = "utf8"
import sys

reload(sys)
sys.setdefaultencoding("utf8")
for index, name in enumerate(sr.Microphone.list_microphone_names()):
    print(
        'Microphone with name "{1}" found for `Microphone(device_index={0})`'.format(
            index, name
        )
    )

import speech_recognition as sr


class SpeechRecognizer:
    def __init__(self):
        self.r = sr.Recognizer()
        self.r.pause_threshold = 1
        self.r.phrase_threshold = 0.5
        self.r.non_speaking_duration = 1
        self.r.dynamic_energy_threshold = False
        ## IMPORTANT: THIS LINE IS ADDED (CHANGED) AFTER BARIS' FIRST NEGOTIATION IN ORDER TO RECORD MORE ACCURATE SOUND.
        self.r.energy_threshold = 150

    def listen_and_convert_to_text(self):
        while True:
            # get audio from the microphone
            with sr.Microphone(device_index=1) as source:
                ## IMPORTANT: THIS LINE IS ADDED (CHANGED) AFTER BARIS' FIRST NEGOTIATION IN ORDER TO RECORD MORE ACCURATE SOUND.
                self.r.adjust_for_ambient_noise(source, duration=0.5)
                print(
                    "Your sentence:",
                )
                audio = self.r.listen(source)
                with open("audio_data_set/orange.wav", "wb") as file:
                    file.write(audio.get_wav_data())
            try:
                # Try to recognize sentence from user by using google api.
                sentence = self.r.recognize_google(audio)
                print("Recognized sentence:", sentence)
                return sentence
            except sr.UnknownValueError:
                print("Sorry, i could not understand you")
            except sr.RequestError as e:
                print("Could not request results, it is about api do not worry")


if __name__ == "__main__":
    speech_recognizer = SpeechRecognizer()
    speech_recognizer.listen_and_convert_to_text()

# !/usr/bin/env python3
#
# NOTE: this example requires PyAudio because it uses the Microphone class

# import time
#
# import speech_recognition as sr
# from offer_classifier import OfferClassifier
#
# action = None
# done = False
# index = 0
#
# # this is called from the background thread
# def callback(recognizer, audio):
#     global index, action, done
#     # received audio data, now we'll recognize it using Google Speech Recognition
#     start_time = time.time()
#     try:
#         # for testing purposes, we're just using the default API key
#         # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
#         # instead of `r.recognize_google(audio)`
#         sentence = recognizer.recognize_google(audio)
#         end_time = time.time()
#         print("API response: ", end_time - start_time)
#         action, done = classifier.get_offer_and_arguments(sentence)
#         print("Google Speech Recognition thinks you said " + sentence)
#     except sr.UnknownValueError:
#         with open("audio_data_set/unknown_voices/test" + str(index) + ".wav", "wb") as file:
#             file.write(audio.get_wav_data())
#             index += 1
#         end_time = time.time()
#         print("API response: ", end_time - start_time)
#         print("Google Speech Recognition could not understand audio")
#     except sr.RequestError as e:
#         with open("audio_data_set/unknown_voices/test" + str(index) + ".wav", "wb") as file:
#             file.write(audio.get_wav_data())
#             index += 1
#         end_time = time.time()
#         print("API response: ", end_time - start_time)
#         print("Could not request results from Google Speech Recognition service; {0}".format(e))
#
#
# r = sr.Recognizer()
# m = sr.Microphone(device_index=1)
# r.pause_threshold = 1
# r.non_speaking_duration = 1
# r.phrase_threshold = 0.5
# r.energy_threshold = 300
# r.dynamic_energy_threshold = False
#
# with m as source:
#     r.adjust_for_ambient_noise(source)  # we only need to calibrate once, before we start listening
#
# # Create offer classifier instance.
# classifier = OfferClassifier()
# # start listening in the background (note that we don't have to do this inside a `with` statement)
# stop_listening = r.listen_in_background(m, callback)
# # `stop_listening` is now a function that, when called, stops background listening
#
# # do some unrelated computations for 5 seconds
# while not done:
#     continue
#
# # calling this function requests that the background listener stop listening
# stop_listening(wait_for_stop=False)
#
# if isinstance(action, negoAction.Offer):
#     print(action.get_bid())
#     print(action.get_arguments())
# elif isinstance(action, negoAction.Accept):
#     print("Acceptance")
