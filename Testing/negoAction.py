class AbstractAction(object):
    def __init__(self, agent_id):
        self.__bid = None
        self.__time_offered = None

    def set_time_offered(self, time):
        self.__time_offered = time

    def get_time_offered(self):
        return self.__time_offered


class Accept(AbstractAction):
    def __init__(self, acceptor):
        self.__acceptor = acceptor

    def set_bid(self, bid):
        self.__bid = bid

    def get_acceptor(self):
        return self.__acceptor

    def get_bid(self):
        return self.__bid


class Offer(AbstractAction):
    def __init__(self, bidder, bid, arguments):
        self.__bidder = bidder
        self.__bid = bid
        self.__arguments = arguments

    def get_bidder(self):
        return self.__bidder

    def get_bid(self):
        return self.__bid

    def get_arguments(self):
        return self.__arguments


class ErrorAction(AbstractAction):
    def __init__(self, error_type):
        self.error_type = error_type

    def get_error_type(self):
        return self.error_type
