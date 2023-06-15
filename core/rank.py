




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