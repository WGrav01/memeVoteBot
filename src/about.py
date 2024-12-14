import discord
from discord.ext import commands
from src import Bot

bot = Bot()


@bot.group()
async def about():
    pass


@about.slash_command(name="ping", description="Get latency information for the bot")
async def ping(ctx):
    await ctx.defer(ephemeral=False)
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
    await ctx.respond(embed=pong, ephemeral=False)


@about.slash_command(name="github", description="Get the link to memeVoteBot's github")
async def github(ctx):
    await ctx.defer(ephemeral=False)
    github = "https://github.com/WGrav01/memeVoteBot"
    response = discord.Embed(title="memeVoteBot's Github", description=f"{github}")
    about = response.add_field(
        name="About",
        value="Made with love by wgrav, open source under the AGPLv3 license.",
    )
    await ctx.respond(embed=response, ephemeral=False)


@about.slash_command(
    name="Version",
    description="Get the version of memeVoteBot this instance is running",
)
async def version(ctx):
    await ctx.defer(ephemeral=False)
    response = discord.Embed(title="memeVoteBot Version", description=f"Running v2.0.0")
    await ctx.respond(embed=response, ephemeral=False)
