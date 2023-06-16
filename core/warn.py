import discord
from discord.ext import commands
from discord import app_commands
from discord import Member
from datetime import datetime
from pymongo import MongoClient
import time

# Connect to your MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['discord_bot']
users = db['users']

class WarnCore(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.users = users

    async def get_user(self, user_id):
        user = self.users.find_one({"_id": user_id})
        if user is None:
            user = {"_id": user_id, "xp": 0, "level": 1, "last_message_time": 0, "spam_count": 0, "warnings": []}
            self.users.insert_one(user)
        return user

    async def update_user(self, user):
        self.users.update_one({"_id": user["_id"]}, {"$set": user})

    @app_commands.command(name='warn', description='Warn a user')
    async def warn(self, ctx, member: Member, reason: str):
        if ctx.author.guild_permissions.administrator:
            user = self.get_user(member.id)
            user["warnings"] = user.get("warnings", [])
            user["warnings"].append({"reason": reason, "time": time.time()})
            self.update_user(user)
            await ctx.send(f"{member.name} has been warned for {reason}.")
        else:
            await ctx.send("You do not have permission to use this command.")

    @app_commands.command(name='view', description='View warnings of a user')
    async def view_warnings(self, ctx, member: Member):
        if ctx.author.guild_permissions.administrator:
            user = self.get_user(member.id)
            warnings = user.get("warnings", [])
            if len(warnings) == 0:
                await ctx.send(f"{member.name} has no warnings.")
                return

            embed = discord.Embed(title=f"{member.name}'s Warnings")
            for warning in warnings:
                reason = warning["reason"]
                timestamp = datetime.fromtimestamp(warning["time"]).strftime('%Y-%m-%d %H:%M:%S')
                embed.add_field(name=f"Warned on {timestamp}", value=f"Reason: {reason}", inline=False)

            await ctx.send(embed=embed)
        else:
            await ctx.send("You are not allowed to use this command.")

async def setup(bot:commands.Bot):
    await bot.add_cog(WarnCore(bot))
