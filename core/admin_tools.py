from mee6_py_api import API
from discord.ext import commands
from discord import app_commands, Member, Embed, Colour
from discord.utils import get
#from discord.app_commands import OptionType


class AdminTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='meesux', description='Update XP and level from Mee6 leaderboard')
    @app_commands.checks.has_permissions(administrator=True)
    async def meesux(self, interaction):
        try:
            self.api = API(str(interaction.guild.id))
            leaderboard_page = self.api.get_leaderboard_page()
            for player in leaderboard_page.players:
                user_id = int(player.id)  # Convert the user ID to int
                user = self.get_user(user_id)
                user["xp"] = player.xp
                user["level"] = player.level
                self.update_user(user)
            await interaction.channel.send("XP and level data has been updated from the Mee6 leaderboard.")
        except Exception as e:
            await interaction.channel.send(f"An error occurred: {e}")


    @app_commands.command(name='mute', description='Mute a member')
    @app_commands.checks.has_permissions(administrator=True)
    async def mute(self, interaction, reason: str = None):
        try:
            role = get(interaction.guild.roles, name="Muted")
            if not role:
                role = await interaction.guild.create_role(name="Muted")
                for channel in interaction.guild.channels:
                    await channel.set_permissions(role, speak=False, send_messages=False)
            member = member
            await member.add_roles(role, reason=reason)
            embed = Embed(title="Mute", description=f"{member.mention} has been muted.", color=Colour.red())
            if reason:
                embed.add_field(name="Reason", value=reason)
            await interaction.channel.send(embed=embed)
        except Exception as e:
            await interaction.channel.send(f"An error occurred: {e}")

    @app_commands.command(name='unmute', description='Unmute a member')
    @app_commands.checks.has_permissions(administrator=True)
    async def unmute(self, interaction):
        member = member
        try:
            role = get(interaction.guild.roles, name="Muted")
            if role in member.roles:
                await member.remove_roles(role)
                embed = Embed(title="Unmute", description=f"{member.mention} has been unmuted.", color=Colour.green())
                await interaction.channel.send(embed=embed)
            else:
                await interaction.channel.send(f"{member.mention} is not muted.")
        except Exception as e:
            await interaction.channel.send(f"An error occurred: {e}")

    @app_commands.command(name='kick', description='Kick a member from the server')
    @app_commands.checks.has_permissions(administrator=True)
    async def kick(self, interaction, reason: str = None):
        member = member
        await member.kick(reason=reason)
        await interaction.channel.send(f"{member.mention} has been kicked for {reason}.")

    @app_commands.command(name='ban', description='Ban a member from the server')
    @app_commands.checks.has_permissions(administrator=True)
    async def ban(self, interaction, reason: str = None):
        member = member
        await member.ban(reason=reason)
        await interaction.channel.send(f"{member.mention} has been banned for {reason}.")

    @app_commands.command(name='change_role', description='Change a user\'s role')
    @app_commands.checks.has_permissions(administrator=True)
    async def change_role(self, interaction, role: str = None):
        member = member
        try:
            await member.add_roles(role)
            await interaction.channel.send(f"{member.mention} has been given the {role.name} role.")
        except Exception as e:
            await interaction.channel.send(f"An error occurred: {e}")


    @app_commands.command(name='send_message', description='Send a message to all members')
    @app_commands.checks.has_permissions(administrator=True)
    async def send_message(self, interaction, *, message: str = None):
        for member in interaction.guild.members:
            if not member.bot:
                await member.send(message)

    @app_commands.command(name='server_stats', description='Display server stats')
    @app_commands.checks.has_permissions(administrator=True)
    async def server_stats(self, interaction):
        embed = Embed(title=f"{interaction.guild.name} Stats")
        embed.add_field(name="Members", value=interaction.guild.member_count)
        embed.add_field(name="Channels", value=len(interaction.guild.channels))
        embed.add_field(name="Roles", value=len(interaction.guild.roles))
        await interaction.channel.send(embed=embed)

    @app_commands.command(name='user_stats', description='Display user stats')
    @app_commands.checks.has_permissions(administrator=True)
    async def user_stats(self, interaction):
        member = member
        embed = Embed(title=f"{member.name} Stats")
        embed.add_field(name="Joined At", value=member.joined_at)
        embed.add_field(name="Roles", value=len(member.roles))
        await interaction.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AdminTools(bot))
