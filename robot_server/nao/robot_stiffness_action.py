from robot_server.nao.robot_action import RobotAction


class RobotStiffnessAction(RobotAction):
    def __init__(self):
        super(RobotStiffnessAction, self).__init__()

    def greet(self):
        self.managerProxy.runBehavior("standup-a650fd/StandUp")
        self.tts.say("Hello, my name is Caduceus.")
        self.tts.say("Let's start the negotiation.")
        self.tts.say("What is your offer?")

    def leave_negotiation(self):
        self.tts.say("Let's stop ! We cannot reach an agreement.")

    def accept(self):
        self.tts.say("Yes, I accept your offer !")

    def mild(self):
        self.tts.say("I liked your offer. You should increase a little.")

    def offended(self):
        self.tts.say("It is not acceptable.")

    def hurry_up(self):
        self.tts.say("Hurry up ! We need to find an agreement soon.")

    def unpleasant(self):
        self.tts.say("I do not like your offer. You should revise it")

    def pleasant(self):
        self.tts.say("It is getting better.")

    def neutral(self):
        self.tts.say("Hmmmm")
