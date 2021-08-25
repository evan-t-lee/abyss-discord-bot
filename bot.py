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

intents = discord.Intents().all()
bot = discord.ext.commands.Bot(command_prefix='!', intents=intents)
slash = SlashCommand(bot, sync_commands=True)

game = None

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
    ]
)
async def play(ctx, playlist_link, points_to_win=5, rounds=30):
    global game

    print(points_to_win, rounds)

    if ctx.voice_client is None:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("You are not connected to a voice channel.")
            raise commands.CommandError("Author not connected to a voice channel.")

    start_message = strings.create_error('Game is already in progress.')
    if not game:
        game = Game(playlist_link, points_to_win, rounds)
        print(game.playlist_info)
        game.start(bot.loop.create_task(game_handler(ctx)))
        start_message = strings.start_message(game.playlist_info, points_to_win, rounds)

    await ctx.send(embed=start_message)

@slash.slash(name='end',description='To end the game.')
async def end(ctx):
    global game

    if not game:
        await ctx.send(embed=strings.create_error('No game in progress.'))
        return

    server = ctx.guild
    voice_channel = server.voice_client
    await voice_channel.disconnect()

    game.in_progress = False
    game.end_round(skipped=True)
    await ctx.send(embed=discord.Embed(title='Game Forcibily Ended'))

@slash.slash(name='pause', description='To pause the game.')
async def pause(ctx):
    message = strings.create_error('No game in progress.')
    if game:
        if game.in_progress:
            message = strings.create_message('Game Paused', 'Game is currently paused, type */resume* to resume.')
            server = ctx.guild
            voice_channel = server.voice_client
            voice_channel.stop()
            game.suspend()
        else:
            message = strings.create_error('Game is not in progress.')

    await ctx.send(embed=message)

@slash.slash(name='resume', description='To resume the game.')
async def resume(ctx):
    message = strings.create_error('No game in progress.')
    if game:
        if game.in_progress:
            message = strings.create_error('Game is already in progress.')
        else:
            message = discord.Embed(title='Game Resumed')
            game.start(bot.loop.create_task(game_handler(ctx)))

    await ctx.send(embed=message)

@slash.slash(name='skip', description='To skip round.')
async def skip(ctx):
    message = strings.create_error('No game in progress.')
    if game:
        if game.in_progress:
            message = discord.Embed(title='Round Skipped')
            game.end_round(skipped=True)
        else:
            message = strings.create_error('Round has not started.')

    await ctx.send(embed=message)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if game and game.in_progress:
        if game.check(message.author, message.content):
            if not game.score(message.author):
                await message.channel.send(embed=strings.guess_message(game.round_info))
            else:
                game.end_round()

    print(f'{message.author.name} : {message.content} : {strings.normalise(message.content)}')

    await bot.process_commands(message)

async def game_handler(ctx):
    global game

    server = ctx.guild
    voice_channel = server.voice_client

    while game.in_progress:
        game.in_progress = False
        voice_channel.stop()
        await asyncio.sleep(3)

        round_info = game.round_info
        async with ctx.channel.typing():
            player = await YTDLSource.from_url(round_info['search_string'], loop=bot.loop, stream=True)
            voice_channel.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

        print('hi')
        await ctx.channel.send(embed=strings.guess_message(round_info))
        print(player.title)

        game.in_progress = True
        await asyncio.sleep(30)

        await ctx.channel.send(embed=strings.round_message(round_info, game.leaderboard()))
        game.new_round()

    print('yeet')
    end_message = strings.end_message(game.playlist_info, game.leaderboard())
    await ctx.channel.send(embed=end_message)
    game = None

bot.run(TOKEN)
