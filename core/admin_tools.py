from mee6_py_api import API
from discord.ext import commands
from discord import app_commands
import disocrd

api = API('your-guild-id')  # Replace 'your-guild-id' with your actual guild ID

# Get leaderboard page
leaderboard_page = api.get_leaderboard_page()

# Get user by rank
user = api.get_user_by_rank(1)  # Get the user with rank 1

# Get user by ID
user = api.get_user_by_id('user-id')  # Replace 'user-id' with the actual user ID



class AdminTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api = API('your-guild-id')  # Replace 'your-guild-id' with your actual guild ID

    @app_commands.command(name='meesux', description='Update XP and level from Mee6 leaderboard')
    @app_commands.has_permissions(administrator=True)
    async def meesux(self, interaction):
        leaderboard_page = self.api.get_leaderboard_page()
        for player in leaderboard_page.players:
            user_id = int(player.id)  # Convert the user ID to int
            user = self.get_user(user_id)
            user["xp"] = player.xp
            user["level"] = player.level
            self.update_user(user)
        await interaction.channel.send("XP and level data has been updated from the Mee6 leaderboard.")

    @app_commands.command(name='mute', description='Update XP and level from Mee6 leaderboard')
    @app_commands.has_permissions(administrator=True)
    async def mute(self, interaction, member: Member, *, reason=None):
        role = get(interaction.guild.roles, name="Muted")
        if not role:
            role = await interaction.guild.create_role(name="Muted")
            for channel in interaction.guild.channels:
                await channel.set_permissions(role, speak=False, send_messages=False)
        await member.add_roles(role, reason=reason)
        await interaction.channel.send(f"{member.mention} has been muted for {reason}.")

    @app_commands.command(name='unmute', description='Update XP and level from Mee6 leaderboard')
    @app_commands.has_permissions(administrator=True)
    async def unmute(self, interaction, member: Member):
        role = get(interaction.guild.roles, name="Muted")
        if role in member.roles:
            await member.remove_roles(role)
            await interaction.channel.send(f"{member.mention} has been unmuted.")
        else:
            await interaction.channel.send(f"{member.mention} is not muted.")

    @app_commands.command(name='kick', description='Update XP and level from Mee6 leaderboard')
    @app_commands.has_permissions(administrator=True)
    async def kick(self, interaction, member: Member, *, reason=None):
        await member.kick(reason=reason)
        await interaction.channel.send(f"{member.mention} has been kicked for {reason}.")

    @app_commands.command(name='ban', description='Update XP and level from Mee6 leaderboard')
    @app_commands.has_permissions(administrator=True)
    async def ban(self, interaction, member: Member, *, reason=None):
        await member.ban(reason=reason)
        await interaction.channel.send(f"{member.mention} has been banned for {reason}.")

    @app_commands.command(name='change_roll', description='Update XP and level from Mee6 leaderboard')
    @app_commands.has_permissions(administrator=True)
    async def change_role(self, interaction, member: Member, role: discord.Role):
        await member.add_roles(role)
        await interaction.channel.send(f"{member.mention} has been given the {role.name} role.")

    @app_commands.command(name='send_message', description='Update XP and level from Mee6 leaderboard')
    @app_commands.has_permissions(administrator=True)
    async def send_message(self, interaction, *, message):
        for member in interaction.guild.members:
            if not member.bot:
                await member.send(message)

    @app_commands.command(name='server_stats', description='Update XP and level from Mee6 leaderboard')
    @app_commands.has_permissions(administrator=True)
    async def server_stats(self, interaction):
        embed = Embed(title=f"{interaction.guild.name} Stats")
        embed.add_field(name="Members", value=interaction.guild.member_count)
        embed.add_field(name="Channels", value=len(interaction.guild.channels))
        embed.add_field(name="Roles", value=len(interaction.guild.roles))
        await interaction.channel.send(embed=embed)

    @app_commands.command(name='user_stats', description='Update XP and level from Mee6 leaderboard')
    @app_commands.has_permissions(administrator=True)
    async def user_stats(self, interaction, member: Member):
        embed = Embed(title=f"{member.name} Stats")
        embed.add_field(name="Joined At", value=member.joined_at)
        embed.add_field(name="Roles", value=len(member.roles))
        await interaction.channel.send(embed=embed)

def setup(bot):
    bot.add_cog(AdminTools(bot))
