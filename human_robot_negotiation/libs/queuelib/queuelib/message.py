

class Message:
    sender: str
    recipient: str
    payload: str
    status: str

    def __init__(self, sender, recipient, payload, status):
        self.sender = sender
        self.recipient = recipient
        self.payload = payload
        self.status = status