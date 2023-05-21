import discord
from discord.ext import commands
from disrank import RankCard
from pymongo import MongoClient
import time

@bot.slash_command(description='Warn a user')
async def warn(interaction: Interaction, member: Member, reason: str):
    if interaction.user.guild_permissions.administrator:
        user = get_user(member.id)
        if "warnings" not in user:
            user["warnings"] = []
        user["warnings"].append({"reason": reason, "time": time.time()})
        update_user(user)
        await interaction.response.send_message(f"{member.name} has been warned for {reason}.")
    else:
        await interaction.response.send_message("You do not have permission to use this command.")

@bot.slash_command(description='View warnings of a user')
async def view_warnings(interaction: Interaction, member: Member):
    if interaction.user.guild_permissions.administrator:
        user = get_user(member.id)
        if "warnings" not in user or len(user["warnings"]) == 0:
            await interaction.response.send_message(f"{member.name} has no warnings.")
            return

        embed = Embed(title=f"{member.name}'s Warnings")
        for warning in user["warnings"]:
            reason = warning["reason"]
            timestamp = datetime.fromtimestamp(warning["time"]).strftime('%Y-%m-%d %H:%M:%S')
            embed.add_field(name=f"Warned on {timestamp}", value=f"Reason: {reason}", inline=False)

        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("You do not have permission to use this command.")
