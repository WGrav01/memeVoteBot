import os
import ast
import discord
from discord.ext import tasks
import aiosqlite
import pytz
from itertools import cycle

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

bot = discord.AutoShardedBot(intents=intents)


@bot.event
async def on_ready():
    db_init_query = """CREATE TABLE IF NOT EXISTS Messages 
                (message_id BIGINT PRIMARY KEY, 
                guild_id BIGINT, 
                likes INT, 
                dislikes INT, 
                reuploadreactions INT,  
                in_showcase VARCHAR);"""

    db_init_query2 = """CREATE TABLE IF NOT EXISTS serverSettings
             (guild_id BIGGINT PRIMARY KEY,
             memeChannels VARCHAR,
             showcaseChannel BIGINT,
             reuploadReactions INT,
             showcaseLikes INT,
             deleteDislikes INT);"""

    db_path = "/data/memevotebot.sqlite"
    db = await aiosqlite.connect(db_path)

    await db.execute(db_init_query)
    await db.execute(db_init_query2)
    await db.commit()
    await db.close()
    change_status.start()
    print(f"Logged in successfully as {bot.user}")


@bot.slash_command(name="add-meme-channel", description="Add a meme channel to the bot")
async def addMemeChannel(ctx, channel: discord.abc.GuildChannel):
    await ctx.defer(ephemeral=True)
    if ctx.user.guild_permissions.administrator:

        db_path = "/data/memevotebot.sqlite"
        db = await aiosqlite.connect(db_path)


        key = f"{ctx.guild.id} memeChannels"
        query = "SELECT * FROM serverSettings WHERE guild_id = :guild_id;"
        values = {"guild_id": ctx.guild.id}

        result = await db.execute_fetchall(query, values)
        if len(result) == 0:
            query = (
                "INSERT INTO serverSettings(guild_id, memeChannels, showcaseChannel, reuploadReactions,"
                " showcaseLikes, deleteDislikes) VALUES (:guild_id, :memeChannels, :showcaseChannel,"
                " :reuploadReactions, :showcaseLikes, :deleteDislikes);"
            )
            values = {
                "guild_id": ctx.guild.id,
                "memeChannels": str(channel.id),
                "showcaseChannel": None,
                "reuploadReactions": None,
                "showcaseLikes": None,
                "deleteDislikes": None,
            }
            await db.execute(query, values)
            await db.commit()
            await db.close()
        else:
            query = "UPDATE serverSettings SET memeChannels = :memeChannels WHERE guild_id = :guild_id;"
            if result and result[0][1]:
                meme_channels = result[0][1]
                if isinstance(meme_channels, str):
                    meme_channels = ast.literal_eval(meme_channels)
                if isinstance(meme_channels, list):
                    if channel.id in meme_channels:
                        error = discord.Embed(
                            title="Error",
                            description="Meme channel already added",
                            color=discord.Color.red(),
                        )
                        await ctx.respond(embed=error, ephemeral=True)
                        return
                    meme_channels.append(channel.id)
                else:
                    if channel.id == meme_channels:
                        error = discord.Embed(
                            title="Error",
                            description="Meme channel already added",
                            color=discord.Color.red(),
                        )
                        await ctx.respond(embed=error, ephemeral=True)
                        return
                    meme_channels = [meme_channels, channel.id]
                values = {"guild_id": ctx.guild.id, "memeChannels": str(meme_channels)}
            await db.execute(query, values)
            await db.commit()
            await db.close()

        success = discord.Embed(
            title="Success",
            description="Meme channel added successfully",
            color=discord.Color.green(),
        )
        success.add_field(name="Channel", value=channel.mention)
        await ctx.respond(embed=success, ephemeral=True)
        return
    else:
        error = discord.Embed(
            title="Error",
            description="You do not have permission to use this command",
            color=discord.Color.red(),
        )
        await ctx.respond(embed=error, ephemeral=True)
        return


@bot.slash_command(
    name="remove-meme-channel", description="Remove a meme channel from the bot"
)
async def removeMemeChannel(ctx, channel: discord.abc.GuildChannel):
    await ctx.defer(ephemeral=True)

    db_path = "/data/memevotebot.sqlite"
    db = await aiosqlite.connect(db_path)


    query = "SELECT * FROM serverSettings WHERE guild_id = :guild_id;"
    values = {"guild_id": ctx.guild.id}
    result = await db.execute_fetchall(query, values)
    if ctx.user.guild_permissions.administrator:
        if isinstance(result[0][1], str):
            channel_result = ast.literal_eval(result[0][1])
            if channel_result is None:
                await db.close()
                error = discord.Embed(
                    title="Error",
                    description="Channel is not set as a meme channel",
                    color=discord.Color.red(),
                )
                await ctx.respond(embed=error, ephemeral=True)
                return
            if channel.id in channel_result:
                new_meme_channel = channel_result.remove(channel.id)
                query = "UPDATE serverSettings SET memeChannels = :memeChannels WHERE guild_id = :guild_id;"
                values = {
                    "guild_id": ctx.guild.id,
                    "memeChannels": str(new_meme_channel),
                }
                await db.execute(query, values)
                await db.commit()
                await db.close()
                success = discord.Embed(
                    title="Success",
                    description="Meme channel removed successfully",
                    color=discord.Color.green(),
                )
                success.add_field(name="Channel", value=channel.mention)
                await ctx.respond(embed=success, ephemeral=True)
                return
            else:
                error = discord.Embed(
                    title="Error",
                    description="Channel is not set as a meme channel",
                    color=discord.Color.red(),
                )
                await ctx.respond(embed=error, ephemeral=True)
                return
        elif isinstance(result[0][1], int):
            channel_result = result[0][1]
            if channel.id == channel_result:
                query = "UPDATE serverSettings SET memeChannels = :memeChannels WHERE guild_id = :guild_id;"
                values = {"guild_id": ctx.guild.id, "memeChannels": None}
                await db.execute(query, values)
                await db.commit()
                await db.close()
                success = discord.Embed(
                    title="Success",
                    description="Meme channel removed successfully",
                    color=discord.Color.green(),
                )
                success.add_field(name="Channel", value=channel.mention)
                await ctx.respond(embed=success, ephemeral=True)
                return
            elif channel.id != channel_result:
                await db.close()
                error = discord.Embed(
                    title="Error",
                    description="Channel is not set as a meme channel",
                    color=discord.Color.red(),
                )
                await ctx.respond(embed=error, ephemeral=True)
                return
    else:
        await db.close()
        error = discord.Embed(
            title="Error",
            description="You do not have permission to use this command",
            color=discord.Color.red(),
        )
        await ctx.respond(embed=error, ephemeral=True)
        return


@bot.slash_command(name="view-settings", description="view the guild's settings")
async def viewSettings(ctx):
    await ctx.defer(ephemeral=True)
    if ctx.user.guild_permissions.administrator:
        try:
            db_path = "/data/memevotebot.sqlite"
            db = await aiosqlite.connect(db_path)

            embed = discord.Embed(
                title="Channels",
                description="List of channels set for bot use",
                color=discord.Color.blurple(),
            )
            formatted_memechannels = None
            meme_channels = None
            ch_list = None
            query = "SELECT * FROM serverSettings WHERE guild_id = :guild_id;"
            values = {"guild_id": ctx.guild.id}
            result = await db.execute_fetchall(query, values)
            await db.close()
            if result and result[0][1]:
                meme_channels = result[0][1]
                if isinstance(meme_channels, str):
                    meme_channels = ast.literal_eval(meme_channels)
                if isinstance(meme_channels, list):
                    formatted_memechannels = "\n".join(
                        f"- <#{item}>" for item in meme_channels
                    )
                else:
                    formatted_memechannels = f"- <#{meme_channels}>"
            if meme_channels is None:
                embed.add_field(
                    name="Meme Channels",
                    value="""There are no meme channels set,
          the bot will not handle memes being posted""",
                    inline=False,
                )
            else:
                embed.add_field(
                    name="Meme Channels",
                    value=str(formatted_memechannels),
                    inline=False,
                )
            showcasechannel = f" - <#{result[0][2]}>"
            if result[0][2] is None:
                embed.add_field(
                    name="Showcase Channel",
                    value="""There is no showcase channel set,
           bot will not showcase memes""",
                )
            else:
                embed.add_field(
                    name="Showcase Channel", value=str(showcasechannel), inline=False
                )

            showcaselikes = result[0][4]
            if showcaselikes is None:
                embed.add_field(
                    name="Showcase Likes",
                    value="""There are no showcase likes set,
                          the bot will not showcase any memes.""",
                    inline=False,
                )
            else:
                embed.add_field(
                    name="Showcase likes", value=str(showcaselikes), inline=False
                )
            deletedislikes = result[0][5]
            if deletedislikes is None:
                embed.add_field(
                    name="Delete Dislikes",
                    value="""Delete dislikes not set,
                          bot will not delete disliked posts""",
                    inline=False,
                )
            else:
                embed.add_field(
                    name="Delete dislikes", value=str(deletedislikes), inline=False
                )
            reuploadreactions = result[0][3]
            if reuploadreactions is None:
                embed.add_field(
                    name="Reupload Reactions",
                    value="""Reupload reactions not set,
                          bot will not delete reuploaded posts""",
                    inline=False,
                )
            else:
                embed.add_field(
                    name="Reupload Reactions",
                    value=str(reuploadreactions),
                    inline=False,
                )
            await ctx.respond(embed=embed, ephemeral=True)
            return
        except IndexError:
            error = discord.Embed(
                title="Error",
                description="There are no settings set for this server",
                color=discord.Color.red(),
            )
            await ctx.respond(embed=error, ephemeral=True)
            return
    else:
        error = discord.Embed(
            title="Error",
            description="You do not have permission to use this command",
            color=discord.Color.red(),
        )
        await ctx.respond(embed=error, ephemeral=True)
        return


@bot.slash_command(
    name="set-showcase-channel", description="Set a showcase channel to the bot"
)
async def addShowcaseChannel(ctx, channel: discord.abc.GuildChannel):
    await ctx.defer(ephemeral=True)
    if ctx.user.guild_permissions.administrator:

        db_path = "/data/memevotebot.sqlite"
        db = await aiosqlite.connect(db_path)

        query = "SELECT * FROM ServerSettings WHERE guild_id = :guild_id"
        values = {"guild_id": ctx.guild.id}
        try:
            result = await db.execute_fetchall(query, values)
        except IndexError:
            query = (
                "INSERT INTO serverSettings VALUES (:guild_id, :memeChannels, :showcaseChannel,"
                " :reuploadReactions, :showcaseLikes, :deleteDislikes);"
            )
            values = {
                "guild_id": ctx.guild.id,
                "memeChannels": None,
                "showcaseChannel": channel.id,
                "reuploadReactions": None,
                "showcaseLikes": None,
                "deleteDislikes": None,
            }
            await db.execute(query, values)
            await db.commit()
            await db.close()
        else:
            query = "UPDATE ServerSettings SET showcaseChannel = :showcaseChannel WHERE guild_id = :guild_id;"
            values = {
                "guild_id": ctx.guild.id,
                "showcaseChannel": channel.id,
            }
            await db.execute(query, values)
            await db.commit()
            await db.close()
        success = discord.Embed(
            title="Success",
            description="Showcase channel set successfully",
            color=discord.Color.green(),
        )
        success.add_field(name="Channel", value=channel.mention)
        await ctx.respond(embed=success, ephemeral=True)
        return
    else:
        error = discord.Embed(
            title="Error",
            description="You do not have permission to use this command",
            color=discord.Color.red(),
        )
        await ctx.respond(embed=error, ephemeral=True)
        return


@bot.slash_command(
    name="remove-showcase-channel", description="Remove a showcase channel from the bot"
)
async def removeShowcaseChannel(ctx, channel: discord.abc.GuildChannel):
    await ctx.defer(ephemeral=True)
    if ctx.user.guild_permissions.administrator:

        db_path = "/data/memevotebot.sqlite"
        db = await aiosqlite.connect(db_path)

        query = "SELECT showcaseChannel FROM serverSettings WHERE guild_id = :guild_id;"
        values = {"guild_id": ctx.guild.id}
        try:
            result = await db.execute_fetchall(query, values)
            if channel.id != result[0][0]:
                error = discord.Embed(
                    title="Error",
                    description="This channel is not set as a showcase channel",
                    color=discord.Color.red(),
                )
                await ctx.respond(embed=error, ephemeral=True)
                return
        except IndexError:
            error = discord.Embed(
                title="Error",
                description="There are no showcase channels set",
                color=discord.Color.red(),
            )
            await ctx.respond(embed=error, ephemeral=True)
            return
        else:
            query = "UPDATE ServerSettings SET showcaseChannel = :showcaseChannel WHERE guild_id = :guild_id;"
            values = {
                "guild_id": ctx.guild.id,
                "showcaseChannel": list(result[0]).remove(channel.id),
            }
            await db.execute(query, values)
            await db.commit()
            await db.close()
            success = discord.Embed(
                title="Success",
                description="Showcase channel removed successfully",
                color=discord.Color.green(),
            )
            success.add_field(name="Channel", value=channel.mention)
            await ctx.respond(embed=success, ephemeral=True)
    else:
        error = discord.Embed(
            title="Error",
            description="You do not have permission to use this command",
            color=discord.Color.red(),
        )
        await ctx.respond(embed=error, ephemeral=True)
        return


@bot.slash_command(
    name="set-showcase-likes",
    description="Set the number of likes required for a meme to be showcased",
)
async def setShowcaseLikes(ctx, likes: int):
    await ctx.defer(ephemeral=True)
    if ctx.user.guild_permissions.administrator:

        db_path = "/data/memevotebot.sqlite"
        db = await aiosqlite.connect(db_path)

        query = "SELECT * FROM ServerSettings WHERE guild_id = :guild_id"
        values = {"guild_id": ctx.guild.id}
        try:
            result = await db.execute_fetchall(query, values)
        except IndexError:
            query = (
                "INSERT INTO ServerSettings VALUES (:guild_id, :memeChannels, :showcaseChannel,"
                " :reuploadReactions, :showcaseLikes, :deleteDislikes);"
            )
            values = {
                "guild_id": ctx.guild.id,
                "memeChannels": [],
                "showcaseChannel": None,
                "reuploadReactions": None,
                "showcaseLikes": likes,
                "deleteDislikes": None,
            }
            await db.execute(query, values)
            await db.commit()
            await db.close()
        else:
            query = "UPDATE ServerSettings SET showcaseLikes = :showcaseLikes WHERE guild_id = :guild_id;"
            values = {"guild_id": ctx.guild.id, "showcaseLikes": likes}
            await db.execute(query, values)
            await db.commit()
            await db.close()
        success = discord.Embed(
            title="Success",
            description="Showcase likes set successfully",
            color=discord.Color.green(),
        )
        success.add_field(name="Likes", value=str(likes))
        await ctx.respond(embed=success, ephemeral=True)
        return
    else:
        error = discord.Embed(
            title="Error",
            description="You do not have permission to use this command",
            color=discord.Color.red(),
        )
        await ctx.respond(embed=error, ephemeral=True)
        return


@bot.slash_command(
    name="set-delete-dislike",
    description="Set the number of dislikes required for a meme to be deleted",
)
async def setDeleteDislikes(ctx, dislikes: int):
    await ctx.defer(ephemeral=True)
    if ctx.user.guild_permissions.administrator:

        db_path = "/data/memevotebot.sqlite"
        db = await aiosqlite.connect(db_path)

        query = "SELECT * FROM ServerSettings WHERE guild_id = :guild_id;"
        values = {"guild_id": ctx.guild.id}
        try:
            result = await db.execute_fetchall(query, values)
        except IndexError:
            query = (
                "INSERT INTO ServerSettings VALUES (:guild_id, :memeChannels,"
                " :showcaseChannel, :reuploadReactions, :showcaseLikes, :deleteDislikes);"
            )
            values = {
                "guild_id": ctx.guild.id,
                "memeChannels": None,
                "showcaseChannel": None,
                "reuploadReactions": None,
                "showcaseLikes": None,
                "deleteDislikes": dislikes,
            }
            await db.execute(query, values)
            await db.commit()
            await db.close()
        else:
            query = "UPDATE ServerSettings SET deleteDislikes = :deleteDislikes WHERE guild_id = :guild_id;"
            values = {"guild_id": ctx.guild.id, "deleteDislikes": dislikes}
            await db.execute(query, values)
            await db.commit()
            await db.close()
        success = discord.Embed(
            title="Success",
            description="Delete dislikes set successfully",
            color=discord.Color.green(),
        )
        success.add_field(name="Dislikes", value=str(dislikes))
        await ctx.respond(embed=success, ephemeral=True)
        return
    else:
        error = discord.Embed(
            title="Error",
            description="You do not have permission to use this command",
            color=discord.Color.red(),
        )
        await ctx.respond(embed=error, ephemeral=True)
        return


@bot.slash_command(
    name="set-reupload-reactions",
    description="""Set the number of reupload reactions required
                  for a meme to be deleted""",
)
async def setDeleteReuploads(ctx, dislikes: int):
    await ctx.defer(ephemeral=True)
    if ctx.user.guild_permissions.administrator:

        db_path = "/data/memevotebot.sqlite"
        db = await aiosqlite.connect(db_path)

        query = "SELECT * FROM ServerSettings WHERE guild_id = :guild_id;"
        values = {"guild_id": ctx.guild.id}
        try:
            result = await db.execute_fetchall(query, values)
        except IndexError:
            query = (
                "INSERT INTO ServerSettings VALUES"
                " (:guild_id, :memeChannels, :showcaseChannel,"
                " :reuploadReactions, :showcaseLikes, :deleteDislikes);"
            )
            values = {
                "guild_id": ctx.guild.id,
                "memeChannels": [],
                "showcaseChannel": None,
                "reuploadReactions": dislikes,
                "showcaseLikes": None,
                "deleteDislikes": None,
            }
            await db.execute(query, values)
            await db.commit()
            await db.close()
        else:
            query = "UPDATE ServerSettings SET reuploadReactions = :reuploadReactions WHERE guild_id = :guild_id;"
            values = {"guild_id": ctx.guild.id, "reuploadReactions": dislikes}
            await db.execute(query, values)
            await db.commit()
            await db.close()
        success = discord.Embed(
            title="Success",
            description="Reupload reactions set successfully",
            color=discord.Color.green(),
        )
        success.add_field(name="Dislikes", value=str(dislikes))
        await ctx.respond(embed=success, ephemeral=True)
        return
    else:
        error = discord.Embed(
            title="Error",
            description="You do not have permission to use this command",
            color=discord.Color.red(),
        )
        await ctx.respond(embed=error, ephemeral=True)
        return


@bot.slash_command(name="ping", description="get latency for the bot")
async def ping(ctx):
    await ctx.defer(ephemeral=True)
    ping = round(bot.latency * 1000)
    color = None
    if ping <= 50:
        color = discord.Color.green()
    elif ping <= 100:
        color = discord.Color.yellow()
    elif ping <= 500:
        color = discord.Color.orange()
    elif ping <= 1000:
        color = discord.Color.red()
    pong = discord.Embed(title="Pong!", description=f"{ping}ms", color=color)
    await ctx.respond(embed=pong, ephemeral=True)


@bot.event
async def on_message(message):
    hasmeme = False
    if message.author == bot.user:
        return

    db_path = "/data/memevotebot.sqlite"
    db = await aiosqlite.connect(db_path)

    query = "SELECT * FROM ServerSettings WHERE guild_id = :guild_id;"
    values = {"guild_id": message.guild.id}
    try:
        result = await db.execute_fetchall(query, values)
        memechannels = ast.literal_eval(result[0][1])
        print(f"{memechannels}, type: {type(memechannels)}")
    except IndexError:
        return

    if isinstance(memechannels, int):
        if message.channel.id != memechannels:
            return
    elif isinstance(memechannels, list):
        memechannels = ast.literal_eval(memechannels)
        if message.channel.id not in memechannels:
            return

    if message.attachments:
        for attachment in message.attachments:
            if attachment.content_type.startswith(
                "image"
            ) or attachment.content_type.startswith("video"):
                hasmeme = True

        # Check if the message content contains a link to an image or video
        if "https://media.discordapp.net" in message.content:
            hasmeme = True

    if not hasmeme:
        await message.delete()
        return
    else:
        await message.add_reaction("👍")
        await message.add_reaction("👎")

        reactions = [reaction.emoji for reaction in message.reactions]

        num_thumbs_up = reactions.count("👍")
        num_thumbs_down = reactions.count("👎")
        num_reupload = reactions.count("♻️")

        query = (
            "INSERT INTO Messages VALUES"
            " (:message_id, :guild_id, :thumbs_up, :thumbs_down, :reupload, :in_showcase);"
        )
        values = {
            "message_id": message.id,
            "guild_id": message.guild.id,
            "thumbs_up": num_thumbs_up,
            "thumbs_down": num_thumbs_down,
            "reupload": num_reupload,
            "in_showcase": 0,
        }
        await db.execute(query, values)
        await db.commit()
        await db.close()


@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id != bot.user.id:
        
        db_path = "/data/memevotebot.sqlite"
        db = await aiosqlite.connect(db_path)

        query = "SELECT * FROM ServerSettings WHERE guild_id = :guild_id;"
        values = {"guild_id": payload.guild_id}
        try:
            result = await db.execute_fetchall(query, values)
            memechannels = result[0][1]
        except IndexError:
            return
        if isinstance(memechannels, int) and payload.channel_id != memechannels:
            return
        elif isinstance(memechannels, list) and payload.channel_id not in memechannels:
            return

        if payload.emoji.name in ["👍", "👎", "♻️"]:
            channel = bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)

            msg_entry = None

            num_thumbs_up = 0
            num_thumbs_down = 0
            num_reupload = 0

            # Iterate over each reaction in the message
            for reaction in message.reactions:
                # Check if the reaction's emoji matches the ones you're interested in
                if str(reaction.emoji) == "👍":
                    num_thumbs_up = reaction.count
                elif str(reaction.emoji) == "👎":
                    num_thumbs_down = reaction.count
                elif str(reaction.emoji) == "♻️":
                    num_reupload = reaction.count

            try:
                query = "SELECT * FROM Messages WHERE message_id = :message_id;"
                values = {"message_id": payload.message_id}
                result = await db.execute_fetchall(query, values)
            except IndexError:  # is thrown if the message is not in the database
                query = (
                    "INSERT INTO Messages VALUES (:message_id, :guild_id, :thumbs_up,"
                    " :thumbs_down, :reupload, :in_showcase);"
                )
                values = {
                    "message_id": payload.message_id,
                    "thumbs_up": num_thumbs_up,
                    "thumbs_down": num_thumbs_down,
                    "reupload": num_reupload,
                    "in_showcase": 0,
                }
                await db.execute(query=query, values=values)
                await db.commit()

            try:
                query = "SELECT * FROM serverSettings WHERE guild_id = :guild_id;"
                values = {"guild_id": payload.guild_id}
                settings = await db.execute_fetchall(query, values)
                showcaselikes = settings[0][4]
                showcasechannel_id = settings[0][2]
                if num_thumbs_up >= showcaselikes and not result[0][5] == 1:
                    showcasechannel = bot.get_channel(showcasechannel_id)
                    attachment = message.attachments[0]

                    # Download the attachment
                    attachment = await attachment.to_file()

                    author = message.author
                    embed = discord.Embed(
                        title="Meme",
                        description=str(message.content),
                        color=discord.Color.gold(),
                    )
                    embed.set_author(
                        name=str(author.name), icon_url=str(message.author.avatar.url)
                    )
                    embed.add_field(name="Channel", value=str(message.channel.mention))
                    embed.add_field(name="Likes", value=f"{num_thumbs_up} 👍")
                    embed.add_field(name="Link to message", value=str(message.jump_url))
                    utc_timezone = pytz.utc
                    utc_created_at = message.created_at.astimezone(utc_timezone)
                    embed.set_footer(
                        text=f"Sent at {utc_created_at.strftime('%m/%d/%Y %I:%M %p')} (UTC)"
                    )

                    # Send a new message with the attachment
                    await showcasechannel.send(embed=embed, file=attachment)
                    query = "UPDATE Messages SET in_showcase = :in_showcase WHERE message_id = :message_id;"
                    values = {"in_showcase": 1}
                    await db.execute(query, values)
                    await db.commit()
                    await db.close()

            except (IndexError, TypeError):
                pass

            try:
                deletedislikes = result[0][5]
                query = (
                    "UPDATE Messages SET likes = :likes, dislikes = :dislikes, reuploadreactions = :reuploadreactions"
                    " WHERE message_id = :message_id;"
                )
                values = {
                    "dislikes": num_thumbs_down,
                    "likes": num_thumbs_up,
                    "reuploadreactions": num_reupload,
                    "message_id": payload.message_id,
                }

                await db.execute(query, values)
                await db.commit()
            except (IndexError, TypeError):
                pass

            try:
                query = "SELECT deleteDislikes FROM serverSettings where guild_id = :guild_id;"
                values = {"guild_id": payload.guild_id}
                result = await db.execute_fetchall(query, values)
                if num_thumbs_down >= result[0][0]:
                    await message.delete()
                    query = "DELETE FROM Messages WHERE message_id = :message_id;"
                    values = {"message_id": payload.message_id}
                    await db.execute(query, values)
                    await db.commit()
                    return
            except (IndexError, TypeError):
                pass

            try:
                query = "SELECT reuploadReactions FROM serverSettings where guild_id = :guild_id;"
                values = {"guild_id": payload.guild_id}
                result = await db.execute_fetchall(query, values)
                if num_reupload >= result[0][0]:
                    await message.delete()
                    query = "DELETE FROM Messages WHERE message_id = :message_id;"
                    values = {"message_id": payload.message_id}
                    await db.execute(query, values)
                    await db.commit()
                    return
            except (IndexError, TypeError):
                pass

            await db.close()
            return
    else:
        return


@bot.event
async def on_raw_message_delete(payload):
    try:

        db_path = "/data/memevotebot.sqlite"
        db = await aiosqlite.connect(db_path)

        query = "DELETE FROM Messages WHERE message_id = :message_id;"
        values = {"message_id": payload.message_id}
        await db.execute(query, values)
        await db.commit()
        await db.close()
        return
    except KeyError:
        return


status = cycle(["the memes", "the likes", "the dislikes", "everyone's reuploads 🤦"])


@tasks.loop(seconds=10)
async def change_status():
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name=next(status))
    )


bot.run(os.environ.get('TOKEN'))
