import discord
import aiosqlite

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True


# Main bot class to be used by all other files.
class Bot(discord.AutoShardedBot(intents=intents)):
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
