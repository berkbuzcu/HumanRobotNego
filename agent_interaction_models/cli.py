from .robot_interface import IRobot

class CLI(IRobot):
    def say(self, message):
        print(message)

    def greet(self):
        print("Hello, I am Caduceus ! Let's start the negotiation.")

    def leave_negotiation(self):
        print("Let's stop ! We cannot reach an agreement.")

    def accept(self):
        print("Yes, I accept your offer!")

    def unpleasant(self):
        print("I don't like your offer. You should revise it.")

    def mild(self):
        print("I like your offer but you can increase a little bit.")

    def offended(self):
        print("It is not acceptable!")

    def hurry_up(self):
        print("Hurry up! We need to find an agreement soon.")

    def pleasant(self):
        print("It is getting better but not enough.")

    def neutral(self):
        print("Hmm")

    def tell_offer(self, agent_offer_to_something):
        pass

    def send_after_offer_sentence(self):
        pass
