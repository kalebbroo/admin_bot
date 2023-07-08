import os
import discord
from discord.ext import commands
import sqlite3
from dotenv import load_dotenv
from discord.ext.commands.errors import ExtensionAlreadyLoaded

load_dotenv()  # take environment variables from .env.

def load_db():
    try:
        # Check if the data directory exists
        if not os.path.exists('data'):
            # If not, create it
            os.makedirs('data')

        # Connect to your SQLite database
        sqlite_db = os.getenv('SQLITEDB')
        #print(f"Connecting to SQLite database at {sqlite_db}")
        conn = sqlite3.connect(sqlite_db)
        return conn
    except Exception as e:
        print(f"Error connecting to SQLite database: {e}")
        return None


bot_token = os.getenv('BOT_TOKEN')
admin_role = os.getenv('ADMIN_ID')
user_role = os.getenv('USER_ID')
bot_channel = os.getenv('BOT_CHANNEL')
admin_channel = os.getenv('ADMIN_CHANNEL')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

async def load_extensions():
    for filename in os.listdir('./core'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'core.{filename[:-3]}')
            except ExtensionAlreadyLoaded:
                pass

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    await load_extensions()
    db = load_db()
    fmt = await bot.tree.sync()
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"{bot.command_prefix}help"))
    print(f"synced {len(fmt)} commands")
    print(f"Loaded: {len(bot.cogs)} core files")
    print(f"Connection to SQLite database: {db is not None}")

    # Set up the database for each guild
    db_cog = bot.get_cog('Database')  # Get the Database cog
    if db_cog:
        for guild in bot.guilds:
            db_cog.setup_database(guild.id)

@bot.event
async def on_command_error(ctx, error):
    # handle your errors here
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Command not found. Use {bot.command_prefix}help to see available commands.")
    else:
        print(f'Error occurred: {error}')


if __name__ == "__main__":
    bot.run(bot_token)