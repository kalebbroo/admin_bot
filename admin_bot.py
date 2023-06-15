import datetime
import discord
from discord.ext import commands
from discord import app_commands, Member
from disrank.generator import Generator
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import time


load_dotenv()  # take environment variables from .env.

bot_token = os.getenv('DISCORD_TOKEN')
mongodb = os.getenv('MONGODB_URI')

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
intents.messages = True
bot = commands.Bot(command_prefix='/', intents=intents)


# Connect to your MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['discord_bot']
users = db['users']




@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name =f"{bot.command_prefix}help"))  # noqa: E501
    print(discord.__version__)

bot.run(bot_token)
