from agent_interaction_models.robot_interface import IRobot
#from naoqi import ALProxy¶
import random
from random import shuffle
#from GestureModels.nao_gesture import NaoGestures
from abc import ABCMeta, abstractmethod
import ast

class RobotAction(IRobot):
    __metaclass__ = ABCMeta

    def init_robot(self, robot_folder):
        self.keywords = ["apple", "orange", "banana", "watermelon"]

    def receive_bid(self, bid):
        return self.tell_offer(ast.literal_eval(bid))
    
    def receive_mood(self, mood):
        gesture_to_run = self.robot_gestures.get_gesture(mood)
        getattr(self, gesture_to_run)()

    def receive_start_nego(self):
        self.greet()

    def receive_nego_over(self, termination_type):
        if termination_type == "human":
            self.say("Okay the negotiation is over.")
        elif termination_type == "agent":
            self.accept()
        else:
            self.leave_negotiation()

    def say(self, message):
        self.tts.say(message)

    def tell_offer(self, offer):
        if "duration" in offer.keys():
            speak_strings = [
                "I'd like to visit %s in %s for %s and stay at a %s" % (offer['destination'], offer['season'], offer['duration'], offer['accommodation']),
                "I want to stay at a %s in %s for %s in %s" % (offer['accommodation'], offer['season'], offer['duration'], offer['destination']),
                "Let's go to %s this %s for %s and stay at a %s" % (offer['destination'], offer['season'], offer['duration'], offer['accommodation']),
                "How about visiting %s in %s for %s and stay at a nice %s?" % (offer['destination'], offer['season'], offer['duration'], offer['accommodation']),
                "I want to spend %s in %s during %s and stay at a %s" % (offer['duration'], offer['destination'], offer['season'], offer['accommodation'])]
        
        elif "events" in offer.keys():
            activity_to_text = {
                "shopping": "shopping",
                "show": "see shows",
                "museum": "visiting museums",
                "sports": "do sports",
            }
            speak_strings = [
                "I'd like to visit %s in %s for %s and stay at a %s" % (offer['destination'], offer['season'], activity_to_text[offer['events']], offer['accommodation']),
                "I want to stay at a %s in %s and %s in %s" % (offer['accommodation'], offer['season'], activity_to_text[offer['events']], offer['destination']),
                "Let's go to %s this %s to %s and stay at a %s" % (offer['destination'], offer['season'], activity_to_text[offer['events']], offer['accommodation']),
                "How about visiting %s in %s for %s and stay at a nice %s" % (offer['destination'], offer['season'], activity_to_text[offer['events']], offer['accommodation']),
                "I want to experience %s in %s during %s and stay at a %s" % (activity_to_text[offer['events']], offer['destination'], offer['season'], offer['accommodation'])]

        else:
            speak_string = "I give you"
            non_zero_count = 0
            for key, value in offer.items():
                if int(value) > 0:
                    non_zero_count += 1
                    speak_string += " " + str(value) + " " + key + "s "
            
            if non_zero_count == 0:
                speak_string = "I want all of them"

            #if non_zero_count < len(offer):
            #    speak_string += " and the rest is yours."

            speak_strings = [speak_string]

        sentence = random.choice(speak_strings)
        self.tts.say(sentence)
        self.send_after_offer_sentence()
        return sentence

    def send_after_offer_sentence(self):
        sentence = self.after_offer_sentences[self.after_offer_index % 3]
        self.after_offer_index = self.after_offer_index + 1
        self.tts.say(sentence)

    def preprocess_offer(self, offer):
        if self.type_index % 2 == 0:
            # Set subject.
            offer_message = "I "
            # Set verb of the message.
            message_verb = self.i_offer_verbs[self.i_offer_index % 2]
            offer_message += message_verb + " you "
            self.i_offer_index += 1
            # Set offer in right format.
        else:
            # Set subject.
            offer_message = "You "
            # Set verb of the message.
            message_verb = self.you_offer_verbs[self.you_offer_index % 3]
            offer_message += message_verb + " "
            self.you_offer_index += 1
            # Set offer in right format.
        # Increase type's index.
        self.type_index += 1

        zero_keywords = []
        non_zero_keywords = []
        for index, keyword in enumerate(offer.keys()):
            amount = int(offer[keyword])
            if amount == 0:
                zero_keywords.append(keyword)
            else:
                non_zero_keywords.append(keyword)

        shuffle(non_zero_keywords)
        for keyword in non_zero_keywords:
            offer_message += "\\pau=100\\ " + str(offer[keyword]) + " " + keyword + " "

        if len(zero_keywords) != 0:
            offer_message += "and " + self.rest_phrases[self.rest_index % 5]
            self.rest_index += 1

        return str(offer_message)
