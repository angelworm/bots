
class Status:
    def __init__(self, sender, type, data):
        self.sender = sender
        self.type = type
        self.data = data

    def to_dict(self):
        return {
            'sender': self.sender,
            'type': self.type,
            'data': self.data
        }
        
    def __str__(self):
        return str(self.to_dict())
