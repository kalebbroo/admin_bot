import discord
from discord.ext import commands
import os
from pymongo import MongoClient
from datetime import datetime
import time


# Connect to your MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['discord_bot']
users = db['users']
        



class XPCore(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    def get_user(self, user_id):
        user = users.find_one({"_id": user_id})
        if user is None:
            user = {"_id": user_id, "xp": 0, "level": 1, "last_message_time": 0, "spam_count": 0}
            users.insert_one(user)
        return user

    def update_user(self, user):
        users.update_one({"_id": user["_id"]}, {"$set": user})

    def add_xp(self, user_id, xp):
        user = self.get_user(user_id)
        user["xp"] += xp
        level = 1
        while user["xp"] >= ((1.2 ** level - 1) * 100) / 0.2:
            level += 1
        if level > user["level"]:
            user["level"] = level
            print(f"User {user_id} has leveled up to level {level}!")
        self.update_user(user)

    @commands.cog.listener()
    def on_thread_create(self, user_id, thread):
        xp = 50
        self.add_xp(user_id, xp)

    @commands.Cog.listener()
    def on_reaction_add(self, user_id, reaction):
        self.get_user(user_id)
        xp = 5
        if reaction.count > 5:
            xp += 5  # Bonus for popular reactions
        self.add_xp(user_id, xp)

    @commands.Cog.listener()
    def on_server_boost(self, user_id):
        xp = 500
        self.add_xp(user_id, xp)

    @commands.Cog.listener()
    def on_slash_command(self, user_id, command):
        xp = 20
        self.add_xp(user_id, xp)

    @commands.Cog.listener()
    def on_invite(self, user_id, invite):
        xp = 200
        if invite.status == "accepted":
            xp += 50  # Bonus for successful invites
        self.add_xp(user_id, xp)

    @commands.Cog.listener()
    def on_new_user_engage(self, user_id, message):
        xp = 30
        if message.reply_count > 5:
            xp += 10  # Bonus for engaging with new users
        self.add_xp(user_id, xp)

    @commands.Cog.listener()
    def on_stream_start(self, user_id, stream):
        xp = 3 * stream.duration
        if stream.viewer_count > 2:
            xp += stream.viewer_count  # Bonus for popular streams
        self.add_xp(user_id, xp)

    @commands.Cog.listener()
    def on_event_participate(self, user_id, event):
        xp = 100
        if event.participant_count > 5:
            xp += 20  # Bonus for popular events
        self.add_xp(user_id, xp)

    @commands.Cog.listener()
    def on_long_message(self, user_id, message):
        xp = 20
        if len(message) > 200:
            xp += 1 * (len(message) - 200) // 10  # Bonus for long messages
        self.add_xp(user_id, xp)

    @commands.Cog.listener()
    def on_message_pinned(self, user_id, message):
        xp = 1000
        self.add_xp(user_id, xp)

    @commands.Cog.listener()
    def on_voice_chat_participation(self, user_id, duration):
        xp = 2 * duration  # Example: 2 XP per minute of voice chat
        self.add_xp(user_id, xp)

    def on_daily_login(self, user_id):
        xp = 50  # Example: 50 XP for daily login
        self.add_xp(user_id, xp)

    def on_weekly_challenge_completion(self, user_id):
        xp = 500  # Example: 500 XP for completing a weekly challenge
        self.add_xp(user_id, xp)



    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        user_id = message.author.id
        user = self.get_user(user_id)
        xp = 10
        if len(message.content) > 100:
            xp += 5
        if time.time() - user["last_message_time"] < 60:
            user["spam_count"] += 1
            if user["spam_count"] > 5:
                xp /= 2  # Spamming penalty
        else:
            user["spam_count"] = 0
        user["last_message_time"] = time.time()
        self.update_user(user)
        self.add_xp(user_id, xp)

def setup(bot:commands.Bot):
    bot.add_cog(XPCore(bot))