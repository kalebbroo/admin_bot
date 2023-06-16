import discord
from discord.ext import commands
from discord import app_commands, Member, Embed
from disrank.generator import Generator
from pymongo import MongoClient

class RankCore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = MongoClient('mongodb://localhost:27017/')  # Connect to your MongoDB server
        self.db = self.client['your_database_name']  # Select your database
        self.users = self.db['users']  # Select your collection

    @app_commands.command(name='rank', description='Check a users rank')
    async def rank(self, interaction, member: discord.Member = None):
        try:
            await interaction.response.defer()
            if member is None:
                member = interaction.author  # If no member is specified, use the user who invoked the command

            user = self.get_user(member.id)
            if user is None:
                await interaction.channel.send("User not found in the database.")
                return
        except Exception as e:
            await interaction.channel.send(f"An error occurred: {str(e)}")

        user = self.get_user(member.id)
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
            'user_name': f'{member.name}#{member.discriminator}',  # user name with discriminator
            'user_status': str(member.status),  # User status eg. online, offline, idle, streaming, dnd
        }

        image = Generator().generate_profile(**args)

        # In a discord command
        file = discord.File(fp=image, filename='image.png')
        await interaction.channel.send(file=file)


    @app_commands.command(name='leaderboard', description='Display the top 10 users')
    async def leaderboard(self, interaction):
        top_users = self.users.find().sort("level", -1).limit(10)  # Get the top 10 users sorted by level in descending order
        embed = Embed(title="Leaderboard", description="Top 10 users by level")

        for i, user in enumerate(top_users, start=1):
            member = await interaction.guild.fetch_member(user["_id"])
            embed.add_field(
                name=f"{i}. {member.name}",
                value=f"Level: {user['level']}\nXP: {user['xp']}\nMessages: {user.get('messages', 0)}\nReactions: {user.get('reactions', 0)}",
                inline=False
            )

        await interaction.response.send_message(embed=embed)


def setup(bot):
    bot.add_cog(RankCore(bot))
