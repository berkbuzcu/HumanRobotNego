from robot_action import RobotAction


class RobotMobileAction(RobotAction):
    def init_robot(self):
        self.folder_path = "pepper-c91fbb/Pepper 2/"
        super(RobotMobileAction, self).init_robot(self.folder_path)

    def greet(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        #<self.managerProxy.runBehavior(self.folder_path + "LetsStart")
        #self.managerProxy.runBehavior("pepper-c91fbb/StandUp")
        self.tts.say("What is your offer?")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    def accept(self):
        self.play_gesture_file("accept")

    def play_gesture_file(self, gesture_file):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.managerProxy.runBehavior(str(self.folder_path + gesture_file + "/behavior_1"))
        self.managerProxy.runBehavior("pepper-c91fbb/StandUp")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)
