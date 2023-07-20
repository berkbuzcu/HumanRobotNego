from robot_server.nao.robot_action import RobotAction


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

    ################################
    # 	      DISAGREEMENT         #
    ################################

    def leave_negotiation(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.managerProxy.runBehavior(self.folder_path + "LetsStop")
        self.managerProxy.runBehavior(self.folder_path + "StandUp")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    ################################
    # 		     ACCEPT            #
    ################################

    def accept(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.managerProxy.runBehavior(self.folder_path + "acceptingOffer")
        self.managerProxy.runBehavior(self.folder_path + "StandUp")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    ################################
    # 		   CONVINCED           #
    ################################

    def convinced_1(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.managerProxy.runBehavior(self.folder_path + "convinced_1")
        self.managerProxy.runBehavior(self.folder_path + "StandUp")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    #def convinced_2(self):
    #    self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
    #    self.managerProxy.runBehavior(self.folder_path + "convinced_2")
    #    self.managerProxy.runBehavior(self.folder_path + "StandUp")
    #    self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    def convinced_3(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.managerProxy.runBehavior(self.folder_path + "convinced_3")
        self.managerProxy.runBehavior(self.folder_path + "StandUp")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    def convinced_4(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.managerProxy.runBehavior(self.folder_path + "convinced_4")
        self.managerProxy.runBehavior(self.folder_path + "StandUp")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    ################################
    # 		   DISSATISFIED        #
    ################################

    def dissatisfied_1(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.managerProxy.runBehavior(self.folder_path + "dissatisfied_1")
        self.managerProxy.runBehavior(self.folder_path + "StandUp")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    def dissatisfied_2(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.managerProxy.runBehavior(self.folder_path + "dissatisfied_2")
        self.managerProxy.runBehavior(self.folder_path + "StandUp")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    def dissatisfied_3(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.managerProxy.runBehavior(self.folder_path + "dissatisfied_3")
        self.managerProxy.runBehavior(self.folder_path + "StandUp")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    def dissatisfied_4(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.managerProxy.runBehavior(self.folder_path + "dissatisfied_4")
        self.managerProxy.runBehavior(self.folder_path + "StandUp")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    def dissatisfied_5(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.managerProxy.runBehavior(self.folder_path + "dissatisfied_5")
        self.managerProxy.runBehavior(self.folder_path + "StandUp")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    def dissatisfied_6(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.managerProxy.runBehavior(self.folder_path + "dissatisfied_6")
        self.managerProxy.runBehavior(self.folder_path + "StandUp")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    def dissatisfied_7(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.managerProxy.runBehavior(self.folder_path + "dissatisfied_7")
        self.managerProxy.runBehavior(self.folder_path + "StandUp")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    def dissatisfied_8(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.managerProxy.runBehavior(self.folder_path + "dissatisfied_8")
        self.managerProxy.runBehavior(self.folder_path + "StandUp")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    ################################
    # 		    ANNOYED            #
    ################################

    def annoyed_1(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.managerProxy.runBehavior(self.folder_path + "annoyed_1")
        self.managerProxy.runBehavior(self.folder_path + "StandUp")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    def annoyed_2(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.managerProxy.runBehavior(self.folder_path + "annoyed_2")
        self.managerProxy.runBehavior(self.folder_path + "StandUp")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    def annoyed_3(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.managerProxy.runBehavior(self.folder_path + "annoyed_3")
        self.managerProxy.runBehavior(self.folder_path + "StandUp")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    def annoyed_4(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.managerProxy.runBehavior(self.folder_path + "annoyed_4")
        self.managerProxy.runBehavior(self.folder_path + "StandUp")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    def annoyed_5(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.managerProxy.runBehavior(self.folder_path + "annoyed_5")
        self.managerProxy.runBehavior(self.folder_path + "StandUp")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    def annoyed_6(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.managerProxy.runBehavior(self.folder_path + "annoyed_6")
        self.managerProxy.runBehavior(self.folder_path + "StandUp")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    def annoyed_7(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.managerProxy.runBehavior(self.folder_path + "annoyed_7")
        self.managerProxy.runBehavior(self.folder_path + "StandUp")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    ################################
    # 		   FRUSTRATED          #
    ################################

    def frustrated_1(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.managerProxy.runBehavior(self.folder_path + "frustrated_1")
        self.managerProxy.runBehavior(self.folder_path + "StandUp")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    def frustrated_2(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.managerProxy.runBehavior(self.folder_path + "frustrated_2")
        self.managerProxy.runBehavior(self.folder_path + "StandUp")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    def frustrated_3(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.managerProxy.runBehavior(self.folder_path + "frustrated_3")
        self.managerProxy.runBehavior(self.folder_path + "StandUp")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    def frustrated_4(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.managerProxy.runBehavior(self.folder_path + "frustrated_4")
        self.managerProxy.runBehavior(self.folder_path + "StandUp")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    ################################
    # 		   WORRIED             #
    ################################

    def worried_1(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.managerProxy.runBehavior(self.folder_path + "worried_1")
        self.managerProxy.runBehavior(self.folder_path + "StandUp")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    def worried_2(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.managerProxy.runBehavior(self.folder_path + "worried_2")
        self.managerProxy.runBehavior(self.folder_path + "StandUp")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    def worried_3(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.managerProxy.runBehavior(self.folder_path + "worried_3")
        self.managerProxy.runBehavior(self.folder_path + "StandUp")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    ################################
    # 		   CONTENT             #
    ################################

    def content_1(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.managerProxy.runBehavior(self.folder_path + "content_1")
        self.managerProxy.runBehavior(self.folder_path + "StandUp")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    def content_2(self):
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", False)
        self.managerProxy.runBehavior(self.folder_path + "content_2")
        self.managerProxy.runBehavior(self.folder_path + "StandUp")
        self.autonomousProxy.setAutonomousAbilityEnabled("BackgroundMovement", True)

    ################################
    # 		   NEUTRAL             #
    ################################

    def neutral_1(self):
        self.say("Hmmmm")

    def neutral_2(self):
        self.say("Let's talk about other options.")
