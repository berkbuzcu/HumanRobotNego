from robot_server.pepper.robot_action import RobotAction


class RobotMobileAction(RobotAction):
    def init_robot(self):
        self.folder_path = "pepper-c91fbb/Pepper 2/"
        super(RobotMobileAction, self).init_robot(self.folder_path)

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


    ################################
    # 		     ACCEPT            #
    ################################

    def accept(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.animatedSpeechProxy.say("Great! ^start(pepper-c91fbb/Pepper 2/accept) I accept your offer!")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)
