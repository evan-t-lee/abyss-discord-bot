# bot.py
import os
from dotenv import load_dotenv

import asyncio
import discord
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option

from ytdl import YTDLSource
from game import Game
import strings

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = os.getenv('DISCORD_GUILD')

intents = discord.Intents().all()
bot = discord.ext.commands.Bot(command_prefix='!', intents=intents)
slash = SlashCommand(bot, sync_commands=True)

guild_ids = [int(GUILD_ID), 183878793713287169]

GAMES = {}

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@slash.slash(
    name='play',
    description='Start a game of guess the song.',
    options=[
        create_option(
            name='playlist_link',
            option_type=3,
            description='The spotify playlist link to use for game.',
            required=True
        ),
        create_option(
            name='points_to_win',
            option_type=4,
            description='The amount of points needed to win.',
            required=False
        ),
        create_option(
            name='rounds',
            option_type=4,
            description='The total number of rounds in the game.',
            required=False
        )
    ],
    guild_ids=guild_ids
)
async def play(ctx, playlist_link, points_to_win=15, rounds=30, guild_ids=guild_ids):
    global GAMES

    if ctx.voice_client is None:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("You are not connected to a voice channel.")
            raise commands.CommandError("Author not connected to a voice channel.")

    start_message = strings.create_error('Game is already in progress.')

    if ctx.guild not in GAMES:
        game = Game(playlist_link, points_to_win, rounds)
        game.start(bot.loop.create_task(game_handler(ctx)))
        start_message = strings.start_message(game.playlist_info, points_to_win, rounds)
        GAMES[ctx.guild] = game

    await ctx.send(embed=start_message)

@slash.slash(name='end',description='To end the game.', guild_ids=guild_ids)
async def end(ctx):
    global GAMES

    game = GAMES.get(ctx.guild)
    if not game:
        await ctx.send(embed=strings.create_error('No game in progress.'))
    else:
        await ctx.send(embed=discord.Embed(description='Game forcibily ended.'))
        game.end_round(skipped=True)
        await ctx.channel.send(embed=strings.round_message(game.round_info, game.leaderboard()))
        game.suspend()
        await ctx.channel.send(embed=strings.end_message(game.playlist_info, game.leaderboard()))
        del GAMES[ctx.guild]

@slash.slash(name='leave',description='To get Abyss to disconnect.', guild_ids=guild_ids)
async def leave(ctx):
    global GAMES

    server = ctx.guild
    voice_channel = server.voice_client

    if voice_channel:
        if not GAMES.get(ctx.guild):
            await ctx.send(embed=strings.create_error('Abyss has disconnected.'))
        else:
            await ctx.invoke(end)
        await voice_channel.disconnect()
    else:
        await ctx.send(embed=strings.create_error('Abyss is not currently connected.'))

@slash.slash(name='pause', description='To pause the game.', guild_ids=guild_ids)
async def pause(ctx):
    message = strings.create_error('No game in progress.')
    game = GAMES.get(ctx.guild)
    if game:
        if game.is_running():
            message = discord.Embed(description=strings.PAUSE_MESSAGE)
            server = ctx.guild
            voice_channel = server.voice_client
            voice_channel.stop()
            game.suspend()
        else:
            message = strings.create_error('Game is not in progress.')

    await ctx.send(embed=message)

@slash.slash(name='resume', description='To resume the game.', guild_ids=guild_ids)
async def resume(ctx):
    message = strings.create_error('No game in progress.')
    game = GAMES.get(ctx.guild)
    if game:
        if game.is_running():
            message = strings.create_error('Game is already in progress.')
        else:
            message = discord.Embed(description='**Game Resumed**')
            game.start(bot.loop.create_task(game_handler(ctx)), resume=True)

    await ctx.send(embed=message)

@slash.slash(name='skip', description='To skip round.', guild_ids=guild_ids)
async def skip(ctx):
    message = strings.create_error('No game in progress.')
    game = GAMES.get(ctx.guild)
    if game:
        if game.is_running():
            message = discord.Embed(description='**Round Skipped**')
            game.end_round(skipped=True)
        else:
            message = strings.create_error('Round has not started.')

    await ctx.send(embed=message)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    game = GAMES.get(message.guild)
    if game and game.is_running():
        if game.check(message.author, message.content):
            if not game.score(message.author):
                await message.channel.send(embed=strings.guess_message(game.round_info))
            else:
                print('yo')
                game.end_round()

    print(f'{message.author.name} : {message.content} : {strings.normalise(message.content)}')

async def game_handler(ctx):
    global GAMES

    server = ctx.guild
    voice_channel = server.voice_client

    game = GAMES[ctx.guild]
    while game.in_progress:
        game.in_progress = False
        voice_channel.stop()
        await asyncio.sleep(3)

        round_info = game.round_info
        async with ctx.channel.typing():
            player = await YTDLSource.from_url(round_info['search_string'], loop=bot.loop)
            voice_channel.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
        print(player.title)

        await ctx.channel.send(embed=strings.guess_message(round_info))

        game.in_progress = True
        await asyncio.sleep(30)

        await ctx.channel.send(embed=strings.round_message(round_info, game.leaderboard()))
        game.new_round()

    await ctx.channel.send(embed=strings.end_message(game.playlist_info, game.leaderboard()))
    del GAMES[ctx.guild]

bot.run(TOKEN)
