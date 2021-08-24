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
async def play(ctx, playlist_link, points_to_win=10, rounds=25):
    global game

    print(points_to_win, rounds)

    if ctx.voice_client is None:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("You are not connected to a voice channel.")
            raise commands.CommandError("Author not connected to a voice channel.")

    game = Game(playlist_link, points_to_win, rounds)
    game.start(bot.loop.create_task(game_handler(ctx)))
    await ctx.send('Yeet :P', hidden=True)
    await ctx.channel.send('Game started!')

@slash.slash(name='end',description='To end the game.')
async def end(ctx):
    global game

    if not game:
        await ctx.send('No game in progress.')
        return

    server = ctx.message.guild
    voice_channel = server.voice_client
    await voice_channel.disconnect()

    end_message = strings.round_message(game.round_info, game.scoreboard_string())
    await ctx.send(embed=end_message)

    game.pause()
    game = None

@slash.slash(name='pause', description='To pause the game.')
async def pause(ctx):
    message = 'No game in progress.'
    if game:
        if game.in_progress:
            message = 'Game paused.'
            server = ctx.message.guild
            voice_channel = server.voice_client
            voice_channel.stop()
            game.pause()
        else:
            message = 'Game is not in progress.'

    await ctx.send(message)

@slash.slash(name='resume', description='To resume the game.')
async def resume(ctx):
    message = 'No game in progress.'
    if game:
        if game.in_progress:
            message = 'Game is already in progress'
        else:
            message = 'Game resumed.'
            game.start(bot.loop.create_task(game_handler(ctx)))

    await ctx.send(message)

@slash.slash(name='skip', description='To skip round.')
async def skip(ctx):
    message = 'No game in progress.'
    if game:
        if game.in_progress:
            message = 'Song skipped.'
            game.skip()
        else:
            message = 'Round has not started.'

    await ctx.send(message)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if game and game.in_progress:
        if game.check(message.author, message.content):
            if not game.score(message.author):
                await message.channel.send(embed=strings.guess_message(game.round_info))
            else:
                game.skip()

    print(f'{message.author.name} : {message.content} : {strings.normalise(message.content)}')

    await bot.process_commands(message)

async def game_handler(ctx):
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

        await ctx.channel.send(embed=strings.guess_message(round_info))
        print(player.title)

        game.in_progress = True
        await asyncio.sleep(30)

        await ctx.channel.send(embed=strings.round_message(round_info, game.scoreboard_string()))
        game.new_round()

bot.run(TOKEN)
