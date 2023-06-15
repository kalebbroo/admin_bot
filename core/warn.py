





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
    
    