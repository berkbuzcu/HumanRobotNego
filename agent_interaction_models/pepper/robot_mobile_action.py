from robot_action import RobotAction


class RobotMobileAction(RobotAction):
    def init_robot(self):
        self.folder_path = "untitled-2f26e7/ExperimentVersion - NaoBehaviorsProjectFolder-Choregraphe-2.8/"
        super(RobotMobileAction, self).init_robot(self.folder_path)

    def greet(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.managerProxy.runBehavior(self.folder_path + "LetsStart")
        self.managerProxy.runBehavior(self.folder_path + "StandUp")
        self.tts.say("What is your offer?")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    def play_gesture_file(self, gesture_file):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.managerProxy.runBehavior(self.folder_path + gesture_file)
        self.managerProxy.runBehavior(self.folder_path + "StandUp")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)
