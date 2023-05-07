import time
import roslibpy
import threading
       
def play(text,gesture,speed,delay):
    gesturePack = {
        "annoyed":"ozyegin.edu/HANT/annoyed-1",
        "content-1":"ozyegin.edu/HANT/content-1",
        "content-2":"ozyegin.edu/HANT/content-2",
        "convinced-1":"ozyegin.edu/HANT/convinced-1",
        "convinced-2":"ozyegin.edu/HANT/convinced-2",
        "convinced-4":"ozyegin.edu/HANT/convinced-4",
        "dissatisfied-1":"ozyegin.edu/HANT/dissatisfied-1",
        "dissatisfied-2":"ozyegin.edu/HANT/dissatisfied-2",
        "frustrated":"ozyegin.edu/HANT/frustrated-1",
        "worried":"ozyegin.edu/HANT/worried",
        "neutral":"ozyegin.edu/HANT/newNeutral",
    }
    
    def gestureM(message):
            client= roslibpy.Ros('192.168.100.2',port=9091)
            #talker=roslibpy.Topic(client,'/qt_robot/behavior/talkText','std_msgs/String')
            talkers=roslibpy.Service(client,'/qt_robot/gesture/play','/qt_robot_gesture_play')
            client.run()
            talkers.call({'name': message,'speed':speed}) 
            client.close()
    
    def talkM(message):
            client= roslibpy.Ros('192.168.100.2',port=9091)
            #talker=roslibpy.Topic(client,'/qt_robot/behavior/talkText','std_msgs/String')
            talkers=roslibpy.Service(client,'/qt_robot/behavior/talkText','/qt_robot_behavior_talk_text')
            client.run()
            talkers.call({'message': message}) 
            client.close()
    talkThread=threading.Thread(target=talkM,args=(text,))
    gestureThread=threading.Thread(target=gestureM,args=(gesturePack[gesture],))
    gestureThread.start()
    time.sleep(delay)
    talkThread.start()
    talkThread.join()
    gestureThread.join()

def announce(message):
            client= roslibpy.Ros('192.168.100.2',port=9091)
            #talker=roslibpy.Topic(client,'/qt_robot/behavior/talkText','std_msgs/String')
            talkers=roslibpy.Service(client,'/qt_robot/behavior/talkText','/qt_robot_behavior_talk_text')
            client.run()
            talkers.call({'message': message}) 
            client.close()

if __name__=="__main__":
    
    announce("content gestures")
    play(" It is getting better but not enough.","content-1",0.0,0)
    play("That sounds good but you can give me a little bit more. ","content-2",0.0,0)

    announce("convinced gestures")
    play("Let me think about it. It is getting better but not enough. ","convinced-1",1.0,1.5)
    play("I appreciate your offer. It would be great if you concede a little bit more. ","convinced-2",0.0,1)
    play("If I am going to consider your offer, it would be great if you concede little bit more.","convinced-2",0.9,0)
    play("Umn Sounds good, we are almost there. ","convinced-4",1.0,0)

    announce("Dissatisfied gestures")
    play("No, I can not accept that unfortunately","dissatisfied-1",0.0,0)
    play("Sorry, I can not accept that.","dissatisfied-1",0.0,0)
    play("That is not going to work for me!","dissatisfied-2",0.0,0)
    play("I'm sorry but I could not agree to your offer. ","dissatisfied-1",0.0,0)
    play("I really can't agree to your offer.","dissatisfied-1",0.0,0)
    play("Your offer is not fair enough.","dissatisfied-1",0.0,0)
    play("Sorry, your offer doesn't go far enough.","dissatisfied-2",0.0,0)
    play("I don't consider that fair.","dissatisfied-1",0.0,0)

    announce("Annoyed gestures")
    play("No, It is not acceptable! ","annoyed",0.0,0)
    play("I wish you did not make this offer.","annoyed",0.0,0)
    play("That's so disappointing!","annoyed",0.0,0)
    play("How am I supposed to accept this offer?","annoyed",0.0,0)
    play("Are you serious? ","annoyed",0.0,0)
    play("I don’t like your offer. You should revise it.","annoyed",0.0,0)
    play("I hope we can find a deal today!","annoyed",0.0,0)

    announce("Frustrated gestures")
    play("Do you really think that is a fair offer? It is not acceptable at all. ","frustrated",0.8,0)
    play("I am very disappointed with your offer. It is not acceptable at all. ","frustrated",0.8,0)
    play("Your offer is not acceptable. Please put yourself on my shoes. ","frustrated",0.8,0)
    play("We cannot reach an agreement. Let's try to be more collaborative.","frustrated",0.8,0)

    announce("Worried gestures")
    play("The deadline is approaching. Let's find a deal soon.","worried",0.0,0)
    play("We are running out of time. Let's be more cooperative to find a deal.","worried",0.0,0)
    play("Hurry up! We need to find an agreement soon.","worried",0.0,0)
