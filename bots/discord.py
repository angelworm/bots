
import requests
import discord
import json
import asyncio

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
            loop = asyncio.get_event_loop()
            loop.close()
            policy = asyncio.get_event_loop_policy()
            policy.set_event_loop(policy.new_event_loop())

    def on_message(self, message):
        dispname, name = self.getauthorname(message.author)

        servername = ''
        if message.server is not None:
            servername = message.server.name
        
        data = {
            'server': servername,
            'channel': message.channel.name,
            'account': {
                'disp': dispname,
                'name': name,
                'avatar': self.getavatar(message.author)
            },
            'timestamp': message.timestamp,
            'content': self.getcontent(message)
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

    def getcontent(self, message):
        if message.type is discord.MessageType.default:
            ret = message.clean_content
            if ret is None:
                ret = message.system_content
            if ret is None:
                ret = ''
            
            for e in message.embeds:
                ret += " " + self.getembettext(e)
            for a in message.attachments:
                ret += " " + a.get('url', str(a))
            return ret
        else:
            return message.system_content

    def getembettext(self, embed):
        ret = None
        if embed['type'] == 'rich':
            ret = embed.get('description', '')
        elif embed['type'] == 'photo':
            ret = embed.get('url', '')
        elif embed['type'] == 'video':
            ret = embed.get('html', '')
        elif embed['type'] == 'link':
            ret = str(embed)
        if ret is None:
            ret = 'None'
        return ret
