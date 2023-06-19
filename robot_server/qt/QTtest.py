"""
import roslibpy
client= roslibpy.Ros('192.168.100.2',port=9091)
talker=roslibpy.Topic(client,'/qt_robot/behavior/talkText','std_msgs/String')
talkers=roslibpy.Service(client,'/qt_robot/behavior/talkText','/qt_robot_behavior_talk_text')
if __name__=="__main__":
    client.run()
    print(client.is_connected)
    talkers.call({'message': 'what\'s up? I would like to let you know, I wanna die'}) 
    print("done")
"""
import time
import roslibpy
import threading


from robot_server.qt.robot_interface import IRobot
import random
from random import shuffle
from abc import ABCMeta, abstractmethod
import ast

"""
async def send_messages():
    while True:
        async with websockets.connect("ws://localhost:8765") as websocket:
            message = input("Enter a message: ")
            await websocket.send(message)

async def main():
    await send_messages()

if __name__ == "__main__":
    asyncio.run(main())
"""


class QTRobotClass(IRobot):
    __metaclass__ = ABCMeta

    def init_robot(self):
        self.num_of_moods = {
            "Frustrated": 0,
            "Annoyed": 0,
            "Dissatisfied": 0,
            "Neutral": 0,
            "Convinced": 0,
            "Content": 0,
            "Worried": 0,
            "Confirmation": 0
        }
        self.gesturePacks = {
        "annoyed-1":"ozyegin.edu/HANT/annoyed-1",
        "annoyed-1-1":"ozyegin.edu/HANT/annoyed-1-1",
        "annoyed-1-2":"ozyegin.edu/HANT/annoyed-1-2",
        "content-1":"ozyegin.edu/HANT/content-1",
        "content-2":"ozyegin.edu/HANT/content-2",
        "convinced-1":"ozyegin.edu/HANT/convinced-1",
        "convinced-2":"ozyegin.edu/HANT/convinced-2",
        "convinced-4":"ozyegin.edu/HANT/convinced-4",
        "dissatisfied-1":"ozyegin.edu/HANT/dissatisfied-1",
        "dissatisfied-2":"ozyegin.edu/HANT/dissatisfied-2",
        "frustrated-1":"ozyegin.edu/HANT/frustrated-1",
        "frustrated-1-1":"ozyegin.edu/HANT/frustrated-1-1",
        "worried":"ozyegin.edu/HANT/worried",
        "hurry":"ozyegin.edu/HANT/hurry",
        "neutral":"ozyegin.edu/HANT/newNeutral",
    }
        self.moodPhrases = {
            "Annoyed": [
                "No, It is not acceptable! ",
                "I wish you did not make this offer.",
                "That's so disappointing!",
                "How am I supposed to accept this offer?",
                "Are you serious? ",
                "I don’t like your offer. You should revise it.",
                "I hope we can find a deal today!"
            ],
            "Frustrated": [
                "Do you really think that is a fair offer? It is not acceptable at all. ",
                "I am very disappointed with your offer. It is not acceptable at all. ",
                "Your offer is not acceptable. Please put yourself on my shoes. ",
                "We cannot reach an agreement. Let's try to be more collaborative."],
            "Dissatisfied": [
                "No, I can not accept that unfortunately",
                "Sorry, I can not accept that.",
                "That is not going to work for me!",
                "I'm sorry but I could not agree to your offer. ",
                "I really can't agree to your offer.",
                "Your offer is not fair enough.",
                "Sorry, your offer doesn't go far enough.",
                "I don't consider that fair."],
            "Neutral": [
                "Omn",
                "Let's talk about other options."],
            "Convinced": [
                "Let me think about it. It is getting better but not enough.",
                "I appreciate your offer. It would be great if you concede a little bit more. ",
                "If I am going to consider your offer, it would be great if you concede little bit more.",
                "Umn Sounds good, we are almost there. "],
            "Content": [
                " It is getting better but not enough.",
                "That sounds good but you can give me a little bit more. "],
            "Worried": [
                "The deadline is approaching. Let's find a deal soon.",
                "We are running out of time. Let's be more cooperative to find a deal.",
                "Hurry up! We need to find an agreement soon."],
            "Confirmation": [
                "Is it okay for you?",
                "Do we agree?",
                "Do we have a deal?",
                "Is it enough for you?",
                "Is it acceptable?"
            ]
        }
        self.gesturesToRun = {
            "Annoyed": [
                "annoyed-1-2",
                "annoyed-1",
                "annoyed-1",
                "annoyed-1-1",
                "annoyed-1-2",
                "annoyed-1",
                "annoyed-1-2"
            ],
            "Frustrated": [
                "frustrated-1-1",
                "frustrated-1-1",
                "frustrated-1",
                "frustrated-1"
            ],
            "Dissatisfied": [
                "dissatisfied-1",
                "dissatisfied-1",
                "dissatisfied-2",
                "dissatisfied-1",
                "dissatisfied-1",
                "dissatisfied-1",
                "dissatisfied-2",
                "dissatisfied-1"
            ],
            "Neutral": [
                "neutral",
                "neutral"
            ],
            "Convinced": [
                "convinced-1",
                "convinced-2",
                "convinced-2",
                "convinced-4"
            ],
            "Content": [
                "content-1",
                "content-2"
            ],
            "Worried": [
                "hurry",
                "worried",
                "hurry"
            ],
            "Confirmation": [
                "neutral",
                "neutral",
                "neutral",
                "neutral",
                "neutral"
            ]
        }
        self.delays = {
            "Annoyed": [
                0,
                0,
                0,
                0,
                0,
                0,
                0
            ],
            "Frustrated": [
                0,
                0,
                0,
                0,
            ],
            "Dissatisfied": [
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0
            ],
            "Neutral": [
                0,
                0
            ],
            "Convinced": [
                1.5,
                1,
                0,
                0
            ],
            "Content": [
                0,
                0
            ],
            "Worried": [
                0,
                0,
                0
            ],
            "Confirmation": [
                0,
                0,
                0,
                0,
                0
            ]
        }
        self.speeds = {
            "Annoyed": [
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0
            ],
            "Frustrated": [
                0.8,
                0.8,
                0.8,
                0.8,
            ],
            "Dissatisfied": [
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0
            ],
            "Neutral": [
                0.0,
                0.0
            ],
            "Convinced": [
                1.0,
                0.0,
                0.9,
                1.0
            ],
            "Content": [
                0.0,
                0.0
            ],
            "Worried": [
                0.6,
                0.0,
                0.7
            ],
            "Confirmation": [
                0.0,
                0.0,
                0.0,
                0.0,
                0.0
            ]
        }
        # self.TalkRobot("Wake up Neo!")
        # self.GestureRobot("QT/show_QT")
        # self.aSyncRobotController("Wake up Neo!","QT/show_QT")
        self.GestureRobot(self.gesturePacks["neutral"])

    def receive_start_nego(self):
        self.aSyncRobotController(
            "Hello, My name is QT! Let's start negotiation! What is your offer?", "QT/show_QT", 0, 0)
        self.GestureRobot(self.gesturePacks["neutral"])
        # self.TalkRobot()
        # self.GestureRobot("QT/neutral")

    def receive_bid(self, bid):
        return self.tell_offer(ast.literal_eval(bid))

    def receive_mood(self, mood):
        self.num_of_moods[mood] += 1
        mood_file_idx = (self.num_of_moods[mood] % (
            len(self.moodPhrases[mood]) - 1))
        # ---------------------------#
        self.aSyncRobotController(self.moodPhrases[mood][mood_file_idx], self.gesturePacks[self.gesturesToRun[mood]
                                  [mood_file_idx]], self.speeds[mood][mood_file_idx], self.delays[mood][mood_file_idx])
        self.GestureRobot(self.gesturePacks["neutral"])
        # getattr(self, gesture_to_run)()

    def GestureRobot(self, message):
        client = roslibpy.Ros('192.168.100.2', port=9091)
        # talker=roslibpy.Topic(client,'/qt_robot/behavior/talkText','std_msgs/String')
        talkers = roslibpy.Service(
            client, '/qt_robot/gesture/play', '/qt_robot_gesture_play')
        client.run()
        talkers.call({'name': message})
        client.close()

    def TalkRobot(self, message):
        client = roslibpy.Ros('192.168.100.2', port=9091)
        # talker=roslibpy.Topic(client,'/qt_robot/behavior/talkText','std_msgs/String')
        talkers = roslibpy.Service(
            client, '/qt_robot/behavior/talkText', '/qt_robot_behavior_talk_text')
        client.run()
        talkers.call({'message': message})
        client.close()

    def receive_nego_over(self, type):
        self.aSyncRobotController(
            "We are finished then! Take care", "QT/bye", 0, 0)
        self.GestureRobot(self.gesturePacks["neutral"])
        # self.TalkRobot("We are finished then! Take care")
        # self.GestureRobot("QT/bye")

    def tell_offer(self, offer):
        if "duration" in offer.keys() and "season" in offer.keys():
            speak_strings = [
                "I'd like to visit %s in %s for %s and stay at a %s" % (offer['destination'], offer['season'], offer['duration'], offer['accommodation']),
                "I want to stay at a %s in %s for %s in %s" % (offer['accommodation'], offer['season'], offer['duration'], offer['destination']),
                "Let's go to %s this %s for %s and stay at a %s" % (offer['destination'], offer['season'], offer['duration'], offer['accommodation']),
                "How about visiting %s in %s for %s and stay at a nice %s?" % (offer['destination'], offer['season'], offer['duration'], offer['accommodation']),
                "I want to spend %s in %s during %s and stay at a %s" % (offer['duration'], offer['destination'], offer['season'], offer['accommodation'])]
        
        elif "events" in offer.keys() and  "season" in offer.keys():
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
            
        elif "duration" in offer.keys() and "events" in offer.keys():
            activity_to_text = {
                "shopping": "shopping",
                "festival": "participating festival",
                "museum": "visiting museums",
                "sports": "do sports",
            }
            speak_strings = [
                "I'd like to visit %s for %s for %s and stay at a %s" % (offer['destination'], offer['duration'], activity_to_text[offer['events']], offer['accommodation']),
                "I want to stay at a %s for %s and %s in %s" % (offer['accommodation'], offer['duration'], activity_to_text[offer['events']], offer['destination']),
                "Let's go to %s for %s to %s and stay at a %s" % (offer['destination'], offer['duration'], activity_to_text[offer['events']], offer['accommodation']),
                "How about visiting %s for %s for %s and stay at a nice %s" % (offer['destination'], offer['duration'], activity_to_text[offer['events']], offer['accommodation']),
                "I want to experience %s in %s for %s and stay at a %s" % (activity_to_text[offer['events']], offer['destination'], offer['duration'], offer['accommodation'])]
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
        self.aSyncRobotController(
            sentence, "ozyegin.edu/HANT/newNeutral", 0, 0)
        self.num_of_moods["Confirmation"] += 1
        mood_file_idx = (self.num_of_moods["Confirmation"] % (
            len(self.moodPhrases["Confirmation"]) - 1))
        # ---------------------------#
        self.aSyncRobotController(self.moodPhrases["Confirmation"][mood_file_idx], self.gesturePacks[self.gesturesToRun["Confirmation"]
                                  [mood_file_idx]], self.speeds["Confirmation"][mood_file_idx], self.delays["Confirmation"][mood_file_idx])
        self.GestureRobot(self.gesturePacks["neutral"])
        # self.TalkRobot(sentence)
        return sentence

    def aSyncRobotController(self, talkText, GestureName, speed, delay):
        def gestureM(message, speed):
            client = roslibpy.Ros('192.168.100.2', port=9091)
            # talker=roslibpy.Topic(client,'/qt_robot/behavior/talkText','std_msgs/String')
            talkers = roslibpy.Service(
                client, '/qt_robot/gesture/play', '/qt_robot_gesture_play')
            client.run()
            talkers.call({'name': message, 'speed': speed})
            client.close()

        def talkM(message):
            client = roslibpy.Ros('192.168.100.2', port=9091)
            # talker=roslibpy.Topic(client,'/qt_robot/behavior/talkText','std_msgs/String')
            talkers = roslibpy.Service(
                client, '/qt_robot/behavior/talkText', '/qt_robot_behavior_talk_text')
            client.run()
            talkers.call({'message': message})
            client.close()
        talkThread = threading.Thread(target=talkM, args=(talkText,))
        gestureThread = threading.Thread(
            target=gestureM, args=(GestureName, speed,))
        gestureThread.start()
        time.sleep(delay)
        talkThread.start()
        talkThread.join()
        gestureThread.join()
