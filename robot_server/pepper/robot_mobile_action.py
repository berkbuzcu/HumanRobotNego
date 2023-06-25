from robot_server.pepper.robot_action import RobotAction


class RobotMobileAction(RobotAction):
    def init_robot(self,robot_ip):
        self.folder_path = "pepper-c91fbb/Pepper 2/"
        super(RobotMobileAction, self).init_robot(self.folder_path,robot_ip)

    def greet(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        #<self.managerProxy.runBehavior(self.folder_path + "LetsStart")
        #self.managerProxy.runBehavior("pepper-c91fbb/StandUp")
        self.managerProxy.runBehavior("standup/behavior_1")
        self.tts.say("Hello my name is Pepper! Let's negotiate!")
        self.tts.say("What is your offer?")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)



    def play_gesture_file(self, gesture_file):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.animatedSpeechProxy.say(gesture_file)
        self.managerProxy.runBehavior("standup/behavior_1")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)
    
    def leave_negotiation(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.tts.say("Negotiation is over.")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    ################################
    # 		     ACCEPT            #
    ################################

    def accept(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.animatedSpeechProxy.say("Great! ^start(pepper-c91fbb/Pepper 2/accept) I accept your offer!")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    