import discord
import aiosqlite
from src import Bot

bot = Bot()


@bot.group()
async def channels():
    pass


@channels.slash_command(name="add", description="Register a channel to the bot")
async def add_channel(
    ctx,
    channel: discord.abc.GuildChannel,
    type: discord.Option(str, choices=["Meme channel", "Showcase channel"]),
):
    await ctx.defer(ephemeral=False)
    if ctx.user.guild_permissions.administrator:

        if type == "Meme channel":
            type = "memeChannels"
        elif type == "Showcase channel":
            type = "showcaseChannel"
        else:
            error = discord.Embed(
                title="Error",
                description="Invalid channel type!",
                color=discord.Color.red(),
            )
            await ctx.respond(embed=error, ephemeral=False)
            return

        db_path = "/data/memevotebot.sqlite"
        db = await aiosqlite.connect(db_path)

        key = f"{ctx.guild.id} {type}"
        query = "SELECT * FROM serverSettings WHERE guild_id = :guild_id;"
        values = {"guild_id": ctx.guild.id}

        result = await db.execute_fetchall(query, values)
        if len(result) == 0:
            query = (
                "INSERT INTO serverSettings(guild_id, memeChannels, showcaseChannel, reuploadReactions,"
                " showcaseLikes, deleteDislikes) VALUES (:guild_id, :memeChannels, :showcaseChannel,"
                " :reuploadReactions, :showcaseLikes, :deleteDislikes);"
            )
            if type == "memeChannels":
                values = {
                    "guild_id": ctx.guild.id,
                    "memeChannels": str(channel.id),
                    "showcaseChannel": None,
                    "reuploadReactions": None,
                    "showcaseLikes": None,
                    "deleteDislikes": None,
                }
            else:
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
            query = f"UPDATE serverSettings SET {type} = :{type} WHERE guild_id = :guild_id;"
            if result and result[0][1]:
                channels = result[0][1]
                if isinstance(channels, str):
                    channels = ast.literal_eval(channels)
                if isinstance(channels, list):
                    if channel.id in channels:
                        error = discord.Embed(
                            title="Error",
                            description="Channel already added",
                            color=discord.Color.red(),
                        )
                        await ctx.respond(embed=error, ephemeral=True)
                        await db.close()
                        return
                    channels.append(channel.id)
                else:
                    if channel.id == channels:
                        error = discord.Embed(
                            title="Error",
                            description="Channel already added",
                            color=discord.Color.red(),
                        )
                        await ctx.respond(embed=error, ephemeral=True)
                        await db.close()
                        return
                    channels = [channels, channel.id]
                values = {"guild_id": ctx.guild.id, f"{type}": str(channels)}
            await db.execute(query, values)
            await db.commit()
            await db.close()

        success = discord.Embed(
            title="Success",
            description="Channel added successfully",
            color=discord.Color.green(),
        )
        success.add_field(name="Channel", value=channel.mention)
        await ctx.respond(embed=success, ephemeral=True)
        return
    else:
        error = discord.Embed(
            title="Error",
            description="Administrator permission is required to use this command.",
            color=discord.Color.red(),
        )
        await ctx.respond(embed=error, ephemeral=True)
        return
