# bot.py
import os
from dotenv import load_dotenv
import asyncio
import pickle

import discord
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option

from ytdl import YTDLSource
from game import Game
import helper
import strings

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents().all()
bot = discord.ext.commands.Bot(command_prefix='!', intents=intents)
slash = SlashCommand(bot, sync_commands=True)

# DEBUGGING STUFF
guild_ids = [878334089747365919, 183878793713287169]#, 501288815659581442]

GAMES = {}
with open('data.pkl', 'rb') as f:
    DATA = pickle.load(f)
print(DATA)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_guild_join(guild):
    global DATA

    DATA[guild.id] = helper.create_server_data()
    with open('data.pkl', 'wb') as f:
        pickle.dump(DATA, f)
    print(DATA)

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
async def play(ctx, playlist_link, points_to_win=None, rounds=None):
    global GAMES

    if ctx.voice_client is None:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("You are not connected to a voice channel.")
            raise commands.CommandError("Author not connected to a voice channel.")

    start_message = strings.create_error('Game is already in progress.')
    game = GAMES.get(ctx.guild.id)
    if not game:
        args = [points_to_win, rounds]
        settings = helper.create_settings(*args) if any(args) else DATA[ctx.guild.id]['settings']
        game = Game(playlist_link, settings)
        game.start(bot.loop.create_task(game_handler(ctx)))
        GAMES[ctx.guild.id] = game
        start_message = strings.start_message(game.playlist_info, game.points_to_win)

    await ctx.send(embed=start_message)

@slash.slash(name='end',description='To end the game.')
async def end(ctx):
    global GAMES

    game = GAMES.get(ctx.guild.id)
    if not game:
        await ctx.send(embed=strings.create_error('No game in progress.'))
    else:
        await ctx.send(embed=discord.Embed(description='**Game Forcibily Ended**'))
        game.end_round(skipped=True)
        await ctx.channel.send(embed=strings.round_message(game.round_info, game.leaderboard()))
        game.suspend()
        await ctx.channel.send(embed=strings.end_message(game.playlist_info, game.leaderboard()))
        del GAMES[ctx.guild.id]

@slash.slash(name='leave',description='To get Abyss to disconnect.')
async def leave(ctx):
    server = ctx.guild
    voice_channel = server.voice_client

    if voice_channel:
        if not GAMES.get(ctx.guild.id):
            await ctx.send(embed=discord.Embed(description='**Abyss has Disconnected.**'))
        else:
            await ctx.invoke(end)
        await voice_channel.disconnect()
    else:
        await ctx.send(embed=strings.create_error('Abyss is not currently connected.'))

@slash.slash(name='pause', description='To pause the game.')
async def pause(ctx):
    game = GAMES.get(ctx.guild.id)
    state = Game.get_state(game)
    if state == 0:
        server = ctx.guild
        voice_channel = server.voice_client
        voice_channel.stop()
        game.suspend()

    await ctx.send(embed=strings.PAUSE_MESSAGE[state])

@slash.slash(name='resume', description='To resume the game.')
async def resume(ctx):
    game = GAMES.get(ctx.guild.id)
    state = Game.get_state(game)
    if state == 2:
        game.start(bot.loop.create_task(game_handler(ctx)), resume=True)

    await ctx.send(embed=strings.RESUME_MESSAGE[state])

@slash.slash(name='skip', description='To skip the current round.')
async def skip(ctx):
    game = GAMES.get(ctx.guild.id)
    state = Game.get_state(game)

    if state == 0:
        game.end_round(skipped=True)

    await ctx.send(embed=strings.SKIP_MESSAGE[state])

@slash.slash(name='extend', description='To extend the current round.')
async def extend(ctx):
    game = GAMES.get(ctx.guild.id)
    state = Game.get_state(game)

    if state == 0:
        game.round_info['remaining_time'] += 30
        game.end_round()

    await ctx.send(embed=strings.EXTEND_MESSAGE[state])

@slash.slash(
    name='settings',
    description='To view and change the default settings of a game.',
    options=[
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
        ),
        create_option(
            name='round_time',
            option_type=4,
            description='The duration of time each round runs for.',
            required=False
        )
    ], guild_ids=guild_ids
)
async def settings(ctx, points_to_win=None, rounds=None, round_time=None):
    global DATA

    args = (points_to_win, rounds, round_time)
    updated = False
    if any(args):
        updated = True
        DATA[ctx.guild.id]['settings'] = helper.create_settings(*args)
        print(DATA)
        with open('data.pkl', 'wb') as f:
            pickle.dump(DATA, f)
    await ctx.send(embed=strings.settings_message(DATA[ctx.guild.id]['settings'], updated))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    game = GAMES.get(message.guild.id)
    if game and game.in_progress:
        print(f'{message.author.name} : {message.content} : {strings.normalise(message.content)}')
        if game.check(message.author, message.content):
            if not game.score(message.author):
                await message.channel.send(embed=strings.guess_message(game.round_info))
            else:
                game.end_round()

async def game_handler(ctx):
    global GAMES

    server = ctx.guild
    voice_channel = server.voice_client

    game = GAMES[ctx.guild.id]
    while game.in_progress:
        voice_channel.stop()
        await asyncio.sleep(3)

        round_info = game.round_info
        async with ctx.channel.typing():
            player = await YTDLSource.from_url(round_info['song_info'], loop=bot.loop)
            voice_channel.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
        print(player.title)
        await ctx.channel.send(embed=strings.guess_message(round_info))

        game.round_info['remaining_time'] = 30
        while game.round_in_progress():
            await asyncio.sleep(30)
            game.round_info['remaining_time'] -= 30


        await ctx.channel.send(embed=strings.round_message(round_info, game.leaderboard()))
        game.new_round()

    await ctx.channel.send(embed=strings.end_message(game.playlist_info, game.leaderboard()))
    del GAMES[ctx.guild]

bot.run(TOKEN)
