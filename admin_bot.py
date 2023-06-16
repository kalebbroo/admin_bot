import os
import discord
from discord.ext import commands
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

bot_token = os.getenv('BOT_TOKEN')
mongodb = os.getenv('MONGODB_URI')
admin_role = os.getenv('ADMIN_ID')
user_role = os.getenv('USER_ID')
bot_channel = os.getenv('BOT_CHANNEL')
admin_channel = os.getenv('ADMIN_CHANNEL')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

# Connect to your MongoDB
client = MongoClient(mongodb)
db = client['discord_bot']
users = db['users']


async def load_extensions():
    for filename in os.listdir('./core'):
        if filename.endswith('.py'):
            await bot.load_extension(f'core.{filename[:-3]}')


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    await load_extensions()
    fmt = await bot.tree.sync()
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"{bot.command_prefix}help"))
    print(f"synced {len(fmt)} commands")
    print(f"Loaded: {len(bot.cogs)} core files")


@bot.event
async def on_command_error(ctx, error):
    # handle your errors here
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Command not found. Use {bot.command_prefix}help to see available commands.")
    else:
        print(f'Error occurred: {error}')


if __name__ == "__main__":
    bot.run(bot_token)
