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
import roslibpy
import threading


from agent_interaction_models.robot_interface import IRobot
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
        }

        self.files_by_mood = {
            "Annoyed": [
                "annoyed_1",
                "annoyed_3",
                "annoyed_6",
                "annoyed_2",
                "annoyed_4",
                "annoyed_7",
                "annoyed_5",
            ],
            "Frustrated": [
                "frustrated_1",
                "frustrated_3",
                "frustrated_2",
                "frustrated_4",
            ],
            "Dissatisfied": [
                "dissatisfied_1",
                "dissatisfied_3",
                "dissatisfied_6",
                "dissatisfied_2",
                "dissatisfied_4",
                "dissatisfied_7",
                "dissatisfied_5",
                "dissatisfied_8",
            ],
            "Neutral": ["neutral_1", "neutral_2"],
            "Convinced": [
                "convinced_1",
                #"convinced_2",
                "convinced_3",
                "convinced_4",
            ],
            "Content": ["content_1", "content_2"],
            "Worried": ["worried_1", "worried_2", "worried_3"],
        }
        self.mood_Phrases = {
            "Annoyed": "Are you serious? I can't accept that!",
            "Frustrated": "Your answers make me tired. Please be reasonable.",
            "Dissatisfied": "I think we can do better.",
            "Neutral": "Let me think about it",
            "Convinced": "It\'s getting better.",
            "Content": "That was nice. Let\'s keep going.",
            "Worried": "No! I cannot accept that!",
        }
        self.gesturePack = {
            "Annoyed": "QT/imitation/hands-on-head-back",
            "Frustrated": "QT/emotions/disgusted",
            "Dissatisfied": "QT/peekaboo",
            "Neutral": "QT/neutral",
            "Convinced": "QT/clapping",
            "Content": "QT/imitation/nodding-yes",
            "Worried": "QT/angry",
        }
        #self.TalkRobot("Wake up Neo!")
        #self.GestureRobot("QT/show_QT")
        self.aSyncRobotController("Wake up Neo!","QT/show_QT")
        self.GestureRobot("QT/neutral")

    def receive_start_nego(self):
        self.aSyncRobotController("Hello, My name is QT! Let\'s start negotiation!","QT/point_front")
        self.GestureRobot("QT/send_kiss")   #TODO adjust speed
        #self.TalkRobot()
        #self.GestureRobot("QT/neutral")
        
    def receive_bid(self, bid):
        return self.tell_offer(ast.literal_eval(bid))
        
    def receive_mood(self, mood):
        self.num_of_moods[mood] += 1
        mood_file_idx = (self.num_of_moods[mood] % (len(self.files_by_mood[mood]) - 1 )) + 1
        mood_file = mood.lower() + "_%s" % mood_file_idx
        gesture_to_run = mood_file
        self.aSyncRobotController(self.mood_Phrases[mood],self.gesturePack[mood])
        self.GestureRobot("QT/neutral")
        #getattr(self, gesture_to_run)()
        
    def GestureRobot(self,message):
        client= roslibpy.Ros('192.168.100.2',port=9091)
        #talker=roslibpy.Topic(client,'/qt_robot/behavior/talkText','std_msgs/String')
        talkers=roslibpy.Service(client,'/qt_robot/gesture/play','/qt_robot_gesture_play')
        client.run()
        talkers.call({'name': message}) 
        client.close()
    
    def TalkRobot(self,message):
        client= roslibpy.Ros('192.168.100.2',port=9091)
        #talker=roslibpy.Topic(client,'/qt_robot/behavior/talkText','std_msgs/String')
        talkers=roslibpy.Service(client,'/qt_robot/behavior/talkText','/qt_robot_behavior_talk_text')
        client.run()
        talkers.call({'message': message}) 
        client.close()
    
    def receive_nego_over(self, type):
        self.aSyncRobotController("We are finished then! Take care","QT/bye")
        self.GestureRobot("QT/neutral")
        #self.TalkRobot("We are finished then! Take care")
        #self.GestureRobot("QT/bye")
    
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
        self.TalkRobot(sentence)
        return sentence    
    
    def aSyncRobotController(self,talkText,GestureName):
        def gestureM(message):
            client= roslibpy.Ros('192.168.100.2',port=9091)
            #talker=roslibpy.Topic(client,'/qt_robot/behavior/talkText','std_msgs/String')
            talkers=roslibpy.Service(client,'/qt_robot/gesture/play','/qt_robot_gesture_play')
            client.run()
            talkers.call({'name': message}) 
            client.close()
    
        def talkM(message):
            client= roslibpy.Ros('192.168.100.2',port=9091)
            #talker=roslibpy.Topic(client,'/qt_robot/behavior/talkText','std_msgs/String')
            talkers=roslibpy.Service(client,'/qt_robot/behavior/talkText','/qt_robot_behavior_talk_text')
            client.run()
            talkers.call({'message': message}) 
            client.close()
        talkThread=threading.Thread(target=talkM,args=(talkText,))
        gestureThread=threading.Thread(target=gestureM,args=(GestureName,))
        talkThread.start()
        gestureThread.start()
        talkThread.join()
        gestureThread.join()
