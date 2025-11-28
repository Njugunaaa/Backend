# models.py
from datetime import datetime

class Event:
    def __init__(self, data):
        self.id = data.get('id')
        self.title = data.get('title')
        self.description = data.get('description')
        self.image_path = data.get('image_path')
        self.date = data.get('date')
        self.time = data.get('time')
        self.location = data.get('location')
        self.category = data.get('category')
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')

    def to_dict(self):
        return self.__dict__


class Sermon:
    def __init__(self, data):
        self.id = data.get('id')
        self.title = data.get('title')
        self.speaker_or_leader = data.get('speaker_or_leader')
        self.date = data.get('date')
        self.description = data.get('description')
        self.media_url = data.get('media_url')  # YouTube or other link
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')

    def to_dict(self):
        return self.__dict__
