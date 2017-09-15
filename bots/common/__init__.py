
class Status:
    def __init__(self, sender, type, data):
        self.sender = sender
        self.type = type
        self.data = data

    def __str__(self):
        return str({
            'sender': self.sender,
            'type': self.type,
            'data': self.data
        })
