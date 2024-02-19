import abc
import random
import ast

from nao_gesture import NaoGestures
from naoqi import ALProxy
import qi


class NaoRobot:
    def __init__(self):
        self.folder_path = "untitled-2f26e7/ExperimentVersion - NaoBehaviorsProjectFolder-Choregraphe-2.8/"
        self.robotIP = "nao.local"
        self.robot_gestures = NaoGestures()

    def init_robot(self):
        self.session = qi.Session() # 169.254.103.236
        self.session.connect("tcp://nao.local:9559")

        self.tts = self.session.service("ALTextToSpeech")
        self.managerProxy = self.session.service("ALBehaviorManager")
        self.autonomousProxy = self.session.service("ALAutonomousLife")
        self.animatedSpeechProxy = self.session.service("ALAnimatedSpeech")

        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)
        self.autonomousProxy.setAutonomousAbilityEnabled("AutonomousBlinking", False)
        self.autonomousProxy.setAutonomousAbilityEnabled("BasicAwareness", False)
        self.autonomousProxy.setAutonomousAbilityEnabled("ListeningMovement", False)
        self.autonomousProxy.setAutonomousAbilityEnabled("SpeakingMovement", False)
        # Set speaking speed and volume of the robot.
        self.tts.setParameter("speed", 75)
        self.tts.setVolume(0.5)

        self.after_offer_sentences = [
            "Is it okay for you?",
            "Do we \\pau=10\\ agree?",
            "Do we have \\pau=10\\ a deal?",
            "Is it enough for you?",
            "Is it acceptable?",
        ]
        self.after_offer_index = 0
        # Set offer verbs for "you take you get etc."
        self.you_offer_verbs = ["take", "get", "have"]
        self.you_offer_index = 0
        # Set offer verbs for "i give you, i offer etc."
        self.i_offer_verbs = ["give", "offer"]
        self.i_offer_index = 0
        # Index for i or you offers.
        self.type_index = 0
        # Rest phrases.
        self.rest_phrases = [
            "That's it",
            "The rest is mine",
            "I \\pau=10\\ will take the rest.",
            "I \\pau=10\\ will have the rest",
            "That's all",
        ]
        self.rest_index = 0
        # Keywords.
        self.keywords = ["apple", "orange", "banana", "watermelon"]
        return {"status":"success"}

    def receive_bid(self, bid):
        return self.tell_offer(ast.literal_eval(bid))

    def receive_mood(self, mood):
        gesture_to_run = self.robot_gestures.get_gesture(mood)
        self.play_gesture_file(gesture_to_run)
        return {"status": "success"}

    def receive_start_nego(self):
        self.greet()
        return {"status": "success"}

    def receive_nego_over(self, termination_type):
        if termination_type == "human":
            self.say("Okay the negotiation is over.")
        elif termination_type == "agent":
            self.accept()
        else:
            self.leave_negotiation()
        return {"status": "success"}

    def say(self, message):
        self.tts.say(message)

    def tell_offer(self, offer):
        if "duration" in offer.keys() and "season" in offer.keys():
            speak_strings = [
                "I'd like to visit %s in %s for %s and stay at a %s" % (
                offer['destination'], offer['season'], offer['duration'], offer['accommodation']),
                "I want to stay at a %s in %s for %s in %s" % (
                offer['accommodation'], offer['season'], offer['duration'], offer['destination']),
                "Let's go to %s this %s for %s and stay at a %s" % (
                offer['destination'], offer['season'], offer['duration'], offer['accommodation']),
                "How about visiting %s in %s for %s and stay at a nice %s?" % (
                offer['destination'], offer['season'], offer['duration'], offer['accommodation']),
                "I want to spend %s in %s during %s and stay at a %s" % (
                offer['duration'], offer['destination'], offer['season'], offer['accommodation'])]

        elif "events" in offer.keys() and "season" in offer.keys():
            activity_to_text = {
                "shopping": "shopping",
                "show": "see shows",
                "museum": "visiting museums",
                "sports": "do sports",
            }
            speak_strings = [
                "I'd like to visit %s in %s for %s and stay at a %s" % (
                offer['destination'], offer['season'], activity_to_text[offer['events']], offer['accommodation']),
                "I want to stay at a %s in %s and %s in %s" % (
                offer['accommodation'], offer['season'], activity_to_text[offer['events']], offer['destination']),
                "Let's go to %s this %s to %s and stay at a %s" % (
                offer['destination'], offer['season'], activity_to_text[offer['events']], offer['accommodation']),
                "How about visiting %s in %s for %s and stay at a nice %s" % (
                offer['destination'], offer['season'], activity_to_text[offer['events']], offer['accommodation']),
                "I want to experience %s in %s during %s and stay at a %s" % (
                activity_to_text[offer['events']], offer['destination'], offer['season'], offer['accommodation'])]

        elif "duration" in offer.keys() and "events" in offer.keys():
            activity_to_text = {
                "shopping": "shopping",
                "festival": "participating festival",
                "museum": "visiting museums",
                "sports": "do sports",
            }
            speak_strings = [
                "I'd like to visit %s for %s for %s and stay at a %s" % (
                offer['destination'], offer['duration'], activity_to_text[offer['events']], offer['accommodation']),
                "I want to stay at a %s for %s and %s in %s" % (
                offer['accommodation'], offer['duration'], activity_to_text[offer['events']], offer['destination']),
                "Let's go to %s for %s to %s and stay at a %s" % (
                offer['destination'], offer['duration'], activity_to_text[offer['events']], offer['accommodation']),
                "How about visiting %s for %s for %s and stay at a nice %s" % (
                offer['destination'], offer['duration'], activity_to_text[offer['events']], offer['accommodation']),
                "I want to experience %s in %s for %s and stay at a %s" % (
                activity_to_text[offer['events']], offer['destination'], offer['duration'], offer['accommodation'])]
        else:
            speak_string = "I give you"
            non_zero_count = 0
            for key, value in offer.items():
                if int(value) > 0:
                    non_zero_count += 1
                    speak_string += " " + str(value) + " " + key + "s "

            if non_zero_count == 0:
                speak_string = "I want all of them"

            # if non_zero_count < len(offer):
            #    speak_string += " and the rest is yours."

            speak_strings = [speak_string]

        sentence = random.choice(speak_strings)
        self.tts.say(sentence)
        # self.send_after_offer_sentence()
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

        random.shuffle(non_zero_keywords)
        for keyword in non_zero_keywords:
            offer_message += "\\pau=100\\ " + str(offer[keyword]) + " " + keyword + " "

        if len(zero_keywords) != 0:
            offer_message += "and " + self.rest_phrases[self.rest_index % 5]
            self.rest_index += 1

        return str(offer_message)

    def greet(self):
        if self.managerProxy.isBehaviorRunning('standup/behavior_1'):
            self.managerProxy.stopBehavior('standup/behavior_1')

        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.managerProxy.runBehavior("standup/behavior_1", _async=True)
        if self.managerProxy.isBehaviorRunning('standup/behavior_1'):
            self.managerProxy.stopBehavior('standup/behavior_1')
        self.tts.say("Hello my name is Pepper! Let's negotiate!")
        self.tts.say("What is your offer?")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    def play_gesture_file(self, gesture_file):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.animatedSpeechProxy.say(gesture_file)
        self.managerProxy.runBehavior("standup/behavior_1", _async=True)
        if self.managerProxy.isBehaviorRunning('standup/behavior_1'):
            self.managerProxy.stopBehavior('standup/behavior_1')
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    def leave_negotiation(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.tts.say("Negotiation is over.")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    def accept(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.animatedSpeechProxy.say("Great! ^start(pepper-c91fbb/Pepper 2/accept) I accept your offer!")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)
