from mee6_py_api import API
from discord.ext import commands
from discord import app_commands, Embed, Colour
from discord.utils import get
import discord
import os


def ordinal(n):
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
        if 11 <= (n % 100) <= 13:
            suffix = 'th'
        return str(n) + suffix


class AdminTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='meesux', description='Import user info from Mee6 and kick it out of the server')
    @app_commands.checks.has_permissions(administrator=True)
    async def meesux(self, interaction):
        await interaction.response.defer()
        mee6 = interaction.guild.get_member(159985870458322944)
        if mee6 is None:
            await interaction.followup.send("The Mee6 bot is not in this server. Please add it to continue.")
            return
        await interaction.followup.send("Importing XP and level data from the Mee6 leaderboard...")
        try:
            api = API(str(interaction.guild.id))
            leaderboard_page = await api.levels.get_leaderboard_page()
            #print(leaderboard_page) 
            if leaderboard_page is None or 'players' not in leaderboard_page:
                await interaction.channel.send("No data available from the Mee6 bot for this server.")
                return
            db_cog = self.bot.get_cog('Database')
            for player in leaderboard_page['players']:
                user_id = int(player['id'])  # Convert the user ID to int
                xp = player['xp']
                level = player['level']
                message = player['message_count']
                username = player['username']
                # Update the user's XP and level in the SQLite database
                user = db_cog.get_user(user_id, interaction.guild.id)
                user['xp'] = xp
                user['level'] = level
                user['message_count'] = message
                db_cog.update_user(user, interaction.guild.id)
                await interaction.channel.send(f"User {username}'s XP and level data has been imported from the Mee6 leaderboard.")
            await interaction.channel.send("All data has been imported from the Mee6 leaderboard.")
            await mee6.kick(reason="Replaced by custom level system")
        except Exception as e:
            await interaction.channel.send(f"An error occurred: {e}")


    @app_commands.command(name='mute', description='Mute a member')
    @app_commands.describe(user='The member to mute')
    @app_commands.describe(reason='The reason for the mute')
    @app_commands.checks.has_permissions(administrator=True)
    async def mute(self, interaction, user: discord.Member, reason: str = None):
        await interaction.response.defer()
        try:
            role = get(interaction.guild.roles, name="Muted")
            if not role:
                role = await interaction.guild.create_role(name="Muted")
                for channel in interaction.guild.channels:
                    await channel.set_permissions(role, speak=False, send_messages=False)
            await user.add_roles(role, reason=reason)
            embed = Embed(title="Mute", description=f"{user.mention} has been muted.", color=Colour.red())
            if reason:
                embed.add_field(name="Reason", value=reason)
            await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.channel.send(f"An error occurred: {e}")

    @app_commands.command(name='unmute', description='Unmute a member')
    @app_commands.describe(user='The member to mute')
    @app_commands.checks.has_permissions(administrator=True)
    async def unmute(self, interaction, user: discord.Member):
        await interaction.response.defer()
        try:
            role = get(interaction.guild.roles, name="Muted")
            if role in user.roles:
                await user.remove_roles(role)
                embed = Embed(title="Unmute", description=f"{user.mention} has been unmuted.", color=Colour.green())
                await interaction.followup.send(embed=embed)
            else:
                await interaction.channel.send(f"{user.mention} is not muted.")
        except Exception as e:
            await interaction.channel.send(f"An error occurred: {e}")

    @app_commands.command(name='kick', description='Kick a member from the server')
    @app_commands.describe(user='The member to kick')
    @app_commands.describe(reason='The reason for the kick')
    @app_commands.checks.has_permissions(administrator=True)
    async def kick(self, interaction, user: discord.Member, reason: str = None):
        await interaction.response.defer()
        await user.kick(reason=reason)
        await interaction.followup.send(f"{user.mention} has been kicked for {reason}.")

    @app_commands.command(name='ban', description='Ban a member from the server')
    @app_commands.describe(user='The member to ban')
    @app_commands.describe(reason='The reason for the ban')
    @app_commands.checks.has_permissions(administrator=True)
    async def ban(self, interaction, user: discord.Member, reason: str = None):
        await interaction.response.defer()
        await user.ban(reason=reason)
        await interaction.followup.send(f"{user.mention} has been banned for {reason}.")

    @app_commands.command(name='adjust_roles', description='Add or remove a user\'s role')
    @app_commands.describe(user='The user to adjust the role of')
    @app_commands.describe(action='The action to perform (add or remove)')
    @app_commands.checks.has_permissions(administrator=True)
    async def adjust_roles(self, interaction, user: discord.Member, action: str):
        await interaction.response.defer()

        if action.lower() == 'add':
            # Create a role select menu of all roles in the server
            roles = [role for role in interaction.guild.roles if role != interaction.guild.default_role]
            role_select = discord.ui.RoleSelect(custom_id='role_select_add', roles=roles, placeholder='Select a role to add')

            # Send a message with the role select menu
            await interaction.followup.send("Select a role to add to the user:", components=role_select)

        elif action.lower() == 'remove':
            # Create a role select menu of all roles the user has
            roles = [role for role in user.roles if role != interaction.guild.default_role]
            role_select = discord.ui.RoleSelect(custom_id='role_select_remove', roles=roles, placeholder='Select a role to remove')

            # Send a message with the role select menu
            await interaction.followup.send("Select a role to remove from the user:", components=role_select)

        else:
            await interaction.followup.send("Invalid action. Please enter 'add' or 'remove'.")

    @commands.Cog.listener()
    async def on_role_select_option(self, interaction: discord.Interaction):
        # Get the selected role and the user
        role = interaction.guild.get_role(interaction.values[0])
        user_id = interaction.message.mentions[0].id
        user = interaction.guild.get_member(user_id)

        if interaction.custom_id == 'role_select_add':
            # If the role select menu for adding a role was used, add the selected role to the user
            await user.add_roles(role)
            await interaction.response.send_message(f"{user.mention} has been given the {role.name} role.")
        elif interaction.custom_id == 'role_select_remove':
            # If the role select menu for removing a role was used, remove the selected role from the user
            await user.remove_roles(role)
            await interaction.response.send_message(f"{user.mention} has been removed from the {role.name} role.")


    @app_commands.command(name='announcement', description='Send an announcement message to all users')
    @app_commands.describe(message='The message to send to all users')
    @app_commands.checks.has_permissions(administrator=True)
    async def send_message(self, interaction, *, message: str = None):
        await interaction.response.defer()
        for member in interaction.guild.members:
            if not member.bot:
                await member.send(message)


    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        print(f"{after.name} changed their name to {after.display_name}")
        if before.display_name != after.display_name:
            db_cog = self.bot.get_cog('Database')
            user_id = after.id
            user = db_cog.get_user(user_id, after.guild.id)
            if user is not None:
                user['name_changes'] += 1
                db_cog.update_user(user, after.guild.id)

                # Get the channel name from the environment variable
                channel_id = int(os.getenv('BOT_CHANNEL'))

                bot_channel = after.guild.get_channel(channel_id)
                if bot_channel is not None:
                    message = f"Heads up! **{after.name}** just switched their name from **{before.display_name}** to **{after.display_name}**. This is the **{ordinal(user['name_changes'])}** time they've needed a new identity."
                    await bot_channel.send(message)



async def setup(bot):
    await bot.add_cog(AdminTools(bot))
