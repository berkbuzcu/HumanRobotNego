from abc import ABCMeta, abstractmethod

class IRobot():
    __metaclass__ = ABCMeta

    @abstractmethod
    def init_robot(self):
        pass

    @abstractmethod
    def receive_start_nego(self):
        pass

    @abstractmethod
    def receive_bid(self, bid):
        pass
    
    @abstractmethod
    def receive_mood(self, mood):
        pass

    @abstractmethod
    def receive_nego_over(self, type):
        pass

# 
#
#
#
#
#
#
#
#
#
#
#