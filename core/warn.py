import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import time
import json

class WarnCore(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot


    @app_commands.command(name='warn', description='Log a warning for a user')
    @app_commands.describe(member='The member to warn')
    @app_commands.describe(reason='The reason for the warn')
    @app_commands.checks.has_permissions(administrator=True)
    async def warn(self, interaction, member: discord.Member, reason: str):
        await interaction.response.defer()
        self.db_cog = self.bot.get_cog('Database')
        user_id = member.id
        guild_id = interaction.guild.id
        user = self.db_cog.get_user(user_id, guild_id)
        warnings = json.loads(user['warnings'])  # Convert the warnings string to a list
        warnings.append({
            "guild_id": guild_id,
            "user_id": user_id,
            "issuer_id": interaction.user.id,
            "time": time.time(),
            "reason": reason
        })
        user['warnings'] = json.dumps(warnings)
        self.db_cog.update_user(user, guild_id)

        # Create the embed
        color = 0xff0000  # Red color for warning
        embed = discord.Embed(title="⚠️ Warning Issued ⚠️", color=color)
        embed.set_author(name=member.name, icon_url=member.avatar.url)  # Set the user's name and avatar as the author
        embed.add_field(name="📊 User Stats", value=f"Level: {user['level']}\nXP: {user['xp']}\nTotal Warnings: {len(warnings)}", inline=False)
        embed.add_field(
            name=f"⚠️ Warned by {interaction.user.name}",
            value=f"**Reason:** {reason}",
            inline=False
        )
        embed.add_field(
            name="🔔 Notice",
            value="Repeated warnings may result in being muted or kicked from the server. Please follow the rules.",
            inline=False
        )
        embed.set_footer(text=f"Total Warnings: {len(warnings)}")  # Set the total number of warnings as the footer

        await interaction.channel.send(embed=embed)


    @app_commands.command(name='view_warnings', description='View all warnings of a user')
    @app_commands.describe(member='The member to view warnings of')
    async def view_warnings(self, interaction, member: discord.Member):
        await interaction.response.defer()
        self.db_cog = self.bot.get_cog('Database')
        user_id = member.id
        guild_id = interaction.guild.id
        user = self.db_cog.get_user(user_id, guild_id)
        warnings = json.loads(user['warnings'])  # Convert the warnings string to a list
        if len(warnings) == 0:
            await interaction.channel.send(f"{member.name} has no warnings.")
            return

        color = 0x00ff00 if len(warnings) == 1 else 0xff0000  # Light color for 1 warning, dark color for multiple warnings
        embed = discord.Embed(title="⚠️ Warnings ⚠️", color=color)
        embed.set_author(name=member.name, icon_url=member.avatar.url)  # Set the user's name and avatar as the author
        embed.add_field(name="📊 User Stats", value=f"Level: {user['level']}\nXP: {user['xp']}\nTotal Warnings: {len(warnings)}", inline=False)

        for warning in warnings:
            issuer = await interaction.guild.fetch_member(warning["issuer_id"])
            reason = warning["reason"]
            timestamp = datetime.fromtimestamp(warning["time"]).strftime('%Y-%m-%d %H:%M:%S')
            embed.add_field(
                name=f"⚠️ Warned on {timestamp} by {issuer.name}",
                value=f"**Reason:** {reason}",
                inline=False
            )

        embed.set_footer(text=f"Total Warnings: {len(warnings)}")  # Set the total number of warnings as the footer
        await interaction.channel.send(embed=embed)


async def setup(bot:commands.Bot):
    await bot.add_cog(WarnCore(bot))
