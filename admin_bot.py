import datetime
import discord
from discord.ext import commands
from discord import app_commands, Member
from disrank.generator import Generator
from pymongo import MongoClient
import time
#from config import TOKEN

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
intents.messages = True
bot = commands.Bot(command_prefix='/', intents=intents)
token = "TOKEN"

# Connect to your MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['discord_bot']
users = db['users']


        

def get_user(user_id):
    user = users.find_one({"_id": user_id})
    if user is None:
        user = {"_id": user_id, "xp": 0, "level": 1, "last_message_time": 0, "spam_count": 0}  # noqa: E501
        users.insert_one(user)
    return user

def update_user(user):
    users.update_one({"_id": user["_id"]}, {"$set": user})

def add_xp(user_id, xp):
    user = get_user(user_id)
    user["xp"] += xp
    level = 1
    while user["xp"] >= ((1.2 ** level - 1) * 100) / 0.2:
        level += 1
    if level > user["level"]:
        user["level"] = level
        print(f"User {user_id} has leveled up to level {level}!")
    update_user(user)


def on_thread_create(user_id, thread):
    xp = 50
    add_xp(user_id, xp)


def on_reaction_add(user_id, reaction):
    get_user(user_id)
    xp = 5
    if reaction.count > 5:
        xp += 5  # Bonus for popular reactions
    add_xp(user_id, xp)

def on_server_boost(user_id):
    xp = 500
    add_xp(user_id, xp)

def on_slash_command(user_id, command):
    xp = 20
    add_xp(user_id, xp)

def on_invite(user_id, invite):
    xp = 200
    if invite.status == "accepted":
        xp += 50  # Bonus for successful invites
    add_xp(user_id, xp)

def on_new_user_engage(user_id, message):
    xp = 30
    if message.reply_count > 5:
        xp += 10  # Bonus for engaging with new users
    add_xp(user_id, xp)

def on_stream_start(user_id, stream):
    xp = 3 * stream.duration
    if stream.viewer_count > 2:
        xp += stream.viewer_count  # Bonus for popular streams
    add_xp(user_id, xp)

def on_event_participate(user_id, event):
    xp = 100
    if event.participant_count > 5:
        xp += 20  # Bonus for popular events
    add_xp(user_id, xp)

def on_long_message(user_id, message):
    xp = 20
    if len(message) > 200:
        xp += 1 * (len(message) - 200) // 10  # Bonus for long messages
    add_xp(user_id, xp)

def on_message_pinned(user_id, message):
    xp = 1000
    add_xp(user_id, xp)


def on_voice_chat_participation(user_id, duration):
    xp = 2 * duration  # Example: 2 XP per minute of voice chat
    add_xp(user_id, xp)

def on_daily_login(user_id):
    xp = 50  # Example: 50 XP for daily login
    add_xp(user_id, xp)

def on_weekly_challenge_completion(user_id):
    xp = 500  # Example: 500 XP for completing a weekly challenge
    add_xp(user_id, xp)



@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    user_id = message.author.id
    user = get_user(user_id)
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
    update_user(user)
    add_xp(user_id, xp)



@bot.tree.command(name='warn', description='Warn a user')
async def warn(interaction: discord.Interaction, member: Member, reason: str):
    if interaction.user.guild_permissions.administrator:
        user = get_user(member.id)
        if "warnings" not in user:
            user["warnings"] = []
        user["warnings"].append({"reason": reason, "time": time.time()})
        update_user(user)
        await interaction.channel.send(f"{member.name} has been warned for {reason}.")  # noqa: E501
    else:
        await interaction.channel.send("You do not have permission to use this command.")  # noqa: E501

@bot.tree.command(name='view', description='View warnings of a user')
async def view_warnings(interaction: discord.Interaction, member: Member):
    if interaction.user.guild_permissions.administrator:
        user = get_user(member.id)
        if "warnings" not in user or len(user["warnings"]) == 0:
            await interaction.channel.send(f"{member.name} has no warnings.")
            return

        embed = embed(title=f"{member.name}'s Warnings")  # noqa: F821
        for warning in user["warnings"]:
            reason = warning["reason"]
            timestamp = datetime.fromtimestamp(warning["time"]).strftime('%Y-%m-%d %H:%M:%S')  # noqa: E501
            embed.add_field(name=f"Warned on {timestamp}", value=f"Reason: {reason}", inline=False)  # noqa: E501

        await interaction.channel.send(embed=embed)
    else:
        await interaction.channel.send("You are not allowed to use this command.")
    
    


@bot.tree.command(name='rank', description='Check a users rank')
@app_commands.describe(member='Check your rank or the rank of another user')
async def rank(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author  # If no member is specified, use the user who invoked the command  # noqa: E501

    user = get_user(member.id)
    xp = user["xp"]
    level = user["level"]
    xp_to_next_level = ((1.2 ** (level + 1) - 1) * 100) / 0.2 - xp

    args = {
        'bg_image': '',  # Background image link
        'profile_image': str(member.avatar_url),  # User profile picture link
        'level': level,  # User current level
        'current_xp': xp,  # Current level minimum xp
        'user_xp': xp,  # User current xp
        'next_xp': xp_to_next_level,  # xp required for next level
        'user_position': 1,  # User position in leaderboard
        'user_name': f'{member.name}#{member.discriminator}',  # user name with discriminator  # noqa: E501
        'user_status': str(member.status),  # User status eg. online, offline, idle, streaming, dnd  # noqa: E501
    }

    image = Generator().generate_profile(**args)

    # In a discord command
    file = discord.File(fp=image, filename='image.png')
    await ctx.send(file=file)


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name =f"{bot.command_prefix}help"))  # noqa: E501
    print(discord.__version__)

bot.run(token)
