from robot_action import RobotAction


class RobotMobileAction(RobotAction):
    def init_robot(self):
        super(RobotMobileAction, self).init_robot()
        self.folder_path = "untitled-be6670/Pepper 2/"

    def greet(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.managerProxy.runBehavior(self.folder_path + "LetsStart")
        self.managerProxy.runBehavior(self.folder_path + "standup")
        self.tts.say("What is your offer?")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    def run_gesture(self, gesture_file):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.managerProxy.runBehavior(self.folder_path + gesture_file)
        self.managerProxy.runBehavior(self.folder_path + "standup")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)