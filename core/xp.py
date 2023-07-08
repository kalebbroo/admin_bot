import discord
from discord.ext import commands
from datetime import datetime
from dotenv import load_dotenv
import asyncio
import random
import time
import math
import os

load_dotenv()
bot_channel = os.getenv('BOT_CHANNEL')

class XPCore(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.db_cog = self.bot.get_cog('Database')  # Get the Database cog instance
        self.voice_channels = {}  # Add this line to initialize the voice_channels dictionary
        self.stream_check_task = None  # Store the background task
        self.xp_bonus = XPBonus()  # Instantiate XPBonus
        self.current_event = None
        self.event_start_time = None
        self.bot_channel = bot.get_channel(int(bot_channel))  # Get the bot channel
        self.event_task = self.bot.loop.create_task(self.select_event())
        self.last_reaction_time = {}  # Add this line to initialize the last_reaction_time dictionary


    async def add_xp(self, user_id, guild_id, xp, channel_id):
        user = self.db_cog.get_user(user_id, guild_id)
        if self.current_event is not None and self.current_event['name'] == "Double XP Day":
            xp = self.current_event['bonus'](xp)
        user['xp'] += xp
        user['xp'] = round(user['xp'])
        count = user['message_count']
        name = self.bot.get_user(user_id).display_name
        level = 1
        while user['xp'] >= ((1.2 ** level - 1) * 100) / 0.2:
            level += 1
        if level > user['level']:
            user['level'] = level
            await self.bot.get_cog('RankCore').level_up(user_id, guild_id, channel_id)
        next_level_xp = ((1.2 ** (user['level'] + 1) - 1) * 100) / 0.2
        xp_to_next_level = math.ceil(next_level_xp - user['xp'])
        print(f"{name} has {user['xp']} XP and is at level {user['level']}.")
        print(f"They need {xp_to_next_level} more XP to levelup. They have sent {count} messages.")
        self.db_cog.update_user(user, guild_id)  # Move this line to the end of the function



    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        user_id = message.author.id
        guild_id = message.guild.id
        user = self.db_cog.get_user(user_id, guild_id)
        if user is None:
            print(f"user was a bot or not in the database")
            return 
        xp = random.randint(5, 50)
        print(f"Adding {xp} XP to user {user_id}")
        await self.add_xp(user_id, guild_id, xp, message.channel.id)
        updated_user = self.db_cog.get_user(user_id, guild_id)
        print(f"User {user_id} now has {updated_user['xp']} XP")




    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user == self.bot.user:
            return
        user_id = user.id
        guild_id = reaction.message.guild.id
        user = self.db_cog.get_user(user_id, guild_id)
        user['emoji_count'] += 1  # Increment emoji count
        if user_id not in self.last_reaction_time:
            self.last_reaction_time[user_id] = -math.inf
        if time.time() - self.last_reaction_time[user_id] < 1:  # If the user is spamming reactions
            user['xp'] -= 100  # Remove 100 XP
            await reaction.message.channel.send(f"{user.mention} Stop spamming reactions! 100 XP has been deducted from your total.")
        self.last_reaction_time[user_id] = time.time()
        self.db_cog.update_user(user, guild_id)
        xp = 1  # Define xp before using it
        if self.current_event is not None and self.current_event['name'] == "Emoji Madness":
            xp = self.current_event['bonus'](xp)
        await self.add_xp(user_id, guild_id, xp, reaction.message.channel.id)  # Add 1 XP for the reaction



    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        xp = 10  # Set a base XP value
        if self.current_event is not None and self.current_event['name'] == "Voice Chat Vibes":
            xp = self.current_event['bonus'](xp)
        if not before.self_stream and after.self_stream:  # The member started streaming
            user_id = member.id
            guild_id = member.guild.id
            channel_id = after.channel.id
            self.voice_channels[channel_id] = {'streamer': user_id, 'watchers': []}  # Initialize the channel state
            await self.add_xp(user_id, guild_id, 10, channel_id)  # Add 10 XP for starting a stream
            if self.stream_check_task is None:  # If the background task is not running
                self.stream_check_task = self.bot.loop.create_task(self.check_streams())  # Start the background task
        elif before.self_stream and not after.self_stream:  # The member stopped streaming
            channel_id = before.channel.id
            if channel_id in self.voice_channels:  # Remove the channel state
                del self.voice_channels[channel_id]
            if not self.voice_channels and self.stream_check_task is not None:  # If no one is streaming
                self.stream_check_task.cancel()  # Stop the background task
                self.stream_check_task = None
        else:  # The member joined or left a voice channel
            if before.channel is not None:
                channel_id = before.channel.id
                if channel_id in self.voice_channels:  # Update the list of watchers
                    channel = self.bot.get_channel(channel_id)
                    self.voice_channels[channel_id]['watchers'] = [member.id for member in channel.members if not member.bot and not member.voice.self_stream]
            if after.channel is not None:
                channel_id = after.channel.id
                if channel_id in self.voice_channels:  # Update the list of watchers
                    channel = self.bot.get_channel(channel_id)
                    self.voice_channels[channel_id]['watchers'] = [member.id for member in channel.members if not member.bot and not member.voice.self_stream]
            xp = 0
            if self.current_event is not None and self.current_event['name'] == "Voice Chat Vibes":
                xp = self.current_event['bonus'](xp)
            if after.channel is not None:
                await self.add_xp(member.id, member.guild.id, xp, after.channel.id)


    async def check_streams(self):
        while True:
            for channel_id, state in list(self.voice_channels.items()):  # Iterate over a copy of the dictionary
                if len(state['watchers']) >= 4:  # If there are at least 2 watchers
                    await self.add_xp(state['streamer'], self.bot.get_channel(channel_id).guild.id, 5, channel_id)  # Add 5 XP to the streamer
            await asyncio.sleep(600)  # Wait for 10 minutes


    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        print(f"type: {interaction.type}")
        if interaction.type == discord.InteractionType.application_command:
            print(f"interaction was a slash command")
            user_id = interaction.user.id
            guild_id = interaction.guild.id
            xp = 100  # Base XP for using a slash command
            if self.current_event is not None and self.current_event['name'] == "Playing With Bots":
                xp = self.current_event['bonus'](xp)
            await self.add_xp(user_id, guild_id, xp, interaction.channel.id)
            user = self.db_cog.get_user(user_id, guild_id)  # Get the user from the database
            self.db_cog.update_user(user, guild_id)  # Update the user in the database


    async def select_event(self):
        # Select a random event
        self.current_event = random.choice(self.xp_bonus.event)
        self.event_start_time = datetime.now()

        # Announce the event
        await self.announce_event()

        # Wait for the duration of the event
        await asyncio.sleep(self.current_event['duration'] * 3600)

        # Reset the event
        self.current_event = None
        self.event_start_time = None

    async def announce_event(self):
        event = self.current_event
        embed = discord.Embed(title=event['name'], description=event['description'], color=0x00ff00)
        embed.add_field(name="Duration", value=f"{event['duration']} hours", inline=False)
        embed.add_field(name="Bonus", value=f"{event['bonus'](1)}x XP", inline=False)
        await self.bot_channel.send(embed=embed)



class XPBonus:
    def __init__(self):
        self.event = [
            {
                "name": "Double XP Day",
                "description": "Earn double XP for the next 8 hours!",
                "bonus": lambda xp: xp * 2,
                "duration": 8  # hours
            },
            # {
            #     "name": "Night Owl",
            #     "description": "Earn 50% more XP for activities done at night (6PM - 12AM)!",
            #     "bonus": lambda xp: xp * 1.5,
            #     "duration": 6  # hours
            # },
            {
                "name": "Playing With Bots",
                "description": "Earn 10% more XP for every bot command used in the next 8 hours!",
                "bonus": lambda xp: xp * 1.1,
                "duration": 8  # hour
            },
            {
                "name": "Active User Reward",
                "description": "Earn 20% more XP for every message sent in the next 3 hours!",
                "bonus": lambda xp: xp * 1.2,
                "duration": 3  # hours
            },
            {
                "name": "Emoji Madness",
                "description": "Earn 10x XP for every emoji in the next 2 hours! Spamming will result in a SEVERE reduction of xp!",
                "bonus": lambda xp: xp * 10,
                "duration": 2  # hours
            },
            # {
            #     "name": "Trivia Time",
            #     "description": "Earn triple XP for participating in trivia in the next hour!",
            #     "bonus": lambda xp: xp * 3,
            #     "duration": 1  # hour
            # },
              {
                 "name": "Voice Chat Vibes",
                 "description": "Earn bonus XP for participating in a voice chat in the next 8 hours!",
                 "bonus": lambda xp: xp * 1.5,
                 "duration": 4  # hours
              }
            # {
            #     "name": "Weekend Warrior",
            #     "description": "Earn 25% more XP for all activities during the weekend!",
            #     "bonus": lambda xp: xp * 1.25,
            #     "duration": 48  # hours
            # },
            # {
            #     "name": "Channel Explorer",
            #     "description": "Earn double XP for posting in a new channel in the next hour!",
            #     "bonus": lambda xp: xp * 2,
            #     "duration": 1  # hour
            # },
            # {
            #     "name": "Roleplay Bonus",
            #     "description": "Earn triple XP for participating in roleplay in the next 2 hours!",
            #     "bonus": lambda xp: xp * 3,
            #     "duration": 2  # hours
            # },
            # {
            #     "name": "Art Appreciation",
            #     "description": "Earn double XP for posting or reacting to art in the next 3 hours!",
            #     "bonus": lambda xp: xp * 2,
            #     "duration": 3  # hours
            # },
            # {
            #     "name": "Helping Hand",
            #     "description": "Earn 50% more XP for helping other users in the next hour!",
            #     "bonus": lambda xp: xp * 1.5,
            #     "duration": 1  # hour
            # }

        ]



async def setup(bot:commands.Bot):
    await bot.add_cog(XPCore(bot))
