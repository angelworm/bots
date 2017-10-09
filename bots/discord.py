
import requests
import discord
import json

from .common import Status, FilterBase

class DiscordClient(FilterBase):
    def __init__(self, confs):
        super().__init__(confs['filtername'])
        self.token = confs['token']
        self.is_bot = confs.get('bot', True)
        self.client = None
        self.heartbeat = None
        self.state = 0
        
    def run_(self):
        try:
            self.client = discord.Client()
            self.client.async_event(self.on_message)

            self.client.run(self.token, bot=self.is_bot)
        finally:
            if self.client is not None:
                self.client.close()

    def on_message(self, message):
        dispname, name = self.getauthorname(message.author)
        
        data = {
            'server': message.server,
            'channel': message.channel,
            'account': {
                'disp': dispname,
                'name': name,
                'avatar': self.getavatar(message.author)
            },
            'timestamp': message.timestamp,
            'content': message.clean_content
        }
        
        self.Q.put(Status(self.filtername, 'discord.update', data))
        
    def getauthorname(self, author):
        if isinstance(author, discord.Member):
            if author.nick is not None:
                return (author.nick, author.name)
        return (author.name, author.name)

    def getavatar(self, author):
        return 'https://cdn.discordapp.com/avatars/{}/{}.png'.format(
            author.id,
            author.avatar
        )
        
