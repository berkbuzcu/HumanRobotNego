import roslibpy
import threading
if __name__=="__main__":
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
        talkThread=threading.Thread(target=talkM,args=("Great! I accept your offer!",))
        gestureThread=threading.Thread(target=gestureM,args=("ozyegin.edu/nodding",))
        #talkThread.start()
        gestureThread.start()
        #talkThread.join()
        gestureThread.join()

