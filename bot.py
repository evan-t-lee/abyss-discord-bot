# bot.py
import os
from dotenv import load_dotenv
import asyncio
import pickle

# import discord
# from discord_slash import SlashCommand
# from discord_slash.utils.manage_commands import create_option
import interactions
from interactions.api.voice.audio import AudioVolume

from ytdl import YTDLSource
from game import Game
import helper
import strings

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# intents = discord.Intents().all()
# bot = discord.ext.commands.Bot(command_prefix='!', intents=intents)
# slash = SlashCommand(bot, sync_commands=True)

bot = interactions.Client(intents=interactions.Intents.ALL, token=TOKEN)

# DEBUGGING STUFF
# guild_ids = [878334089747365919, 183878793713287169, 501288815659581442]

GAMES = {}
with open('data.pkl', 'rb') as f:
    DATA = pickle.load(f)
print(DATA)

@interactions.listen()
async def on_startup():
    print(f'{bot.user} has connected to Discord!')

# @interactions.listen()
# async def on_guild_join(guild):
#     global DATA
#     print(guild)
#     # DATA[guild.id] = helper.create_server_data()
#     # with open('data.pkl', 'wb') as f:
#     #     pickle.dump(DATA, f)
#     # print(DATA)

@interactions.slash_command(
    name='play',
    description='Start a game of guess the song.',
    # options=[
    #     create_option(
    #         name='playlist_link',
    #         option_type=3,
    #         description='The spotify playlist link to use for game.',
    #         required=True
    #     ),
    #     create_option(
    #         name='points_to_win',
    #         option_type=4,
    #         description='The amount of points needed to win.',
    #         required=False
    #     ),
    #     create_option(
    #         name='rounds',
    #         option_type=4,
    #         description='The total number of rounds in the game.',
    #         required=False
    #     )
    # ]
)
@interactions.slash_option(
    name='playlist_link',
    opt_type=interactions.OptionType.STRING,
    description='The spotify playlist link to use for game.',
    required=True
)
async def play(ctx, playlist_link, points_to_win=None, rounds=None):
    global GAMES

    await ctx.defer()

    game = GAMES.get(ctx.guild.id)
    if game:
        await ctx.send(embed=strings.create_error('Game is already in progress.'))
        return

    args = (points_to_win, rounds)
    if helper.has_invalid_args(*args):
        await ctx.send(embed=strings.create_error('Invalid arguments were supplied.'))
        return

    print(ctx.voice_state)
    if not ctx.voice_state:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("You are not connected to a voice channel.")
            # raise commands.CommandError("Author not connected to a voice channel.")

    settings = helper.create_settings(*args) if any(args) else DATA[ctx.guild.id]['settings']
    game = Game(playlist_link, settings)
    task = asyncio.create_task(game_handler(ctx))
    print(task)
    game.start(task)
    asyncio.gather(task)
    GAMES[ctx.guild.id] = game

    await ctx.send(embed=strings.start_message(game.playlist_info, game.points_to_win))


@interactions.slash_command(name='end',description='To end the game.')
async def end(ctx):
    global GAMES

    game = GAMES.get(ctx.guild.id)
    if not game:
        await ctx.send(embed=strings.create_error('No game in progress.'))
    else:
        await ctx.send(embed=interactions.Embed(description='**Game Forcibily Ended**'))
        game.end_round(skipped=True)
        await ctx.channel.send(embed=strings.round_message(game.round_info, game.leaderboard()))
        game.suspend()
        await ctx.channel.send(embed=strings.end_message(game.playlist_info, game.leaderboard()))
        del GAMES[ctx.guild.id]

@interactions.slash_command(name='leave',description='To get Abyss to disconnect.')
async def leave(ctx):
    server = ctx.guild
    voice_channel = server.voice_client

    if voice_channel:
        if not GAMES.get(ctx.guild.id):
            await ctx.send(embed=interactions.Embed(description='**Abyss has Disconnected**'))
        else:
            await ctx.invoke(end)
        await voice_channel.disconnect(force=True)
    else:
        await ctx.send(embed=strings.create_error('Abyss is not currently connected.'))

@interactions.slash_command(name='pause', description='To pause the game.')
async def pause(ctx):
    game = GAMES.get(ctx.guild.id)
    state = Game.get_state(game)
    if state == 0:
        server = ctx.guild
        voice_channel = server.voice_client
        voice_channel.stop()
        game.suspend()

    await ctx.send(embed=strings.PAUSE_MESSAGE[state])

@interactions.slash_command(name='resume', description='To resume the game.')
async def resume(ctx):
    game = GAMES.get(ctx.guild.id)
    state = Game.get_state(game)
    if state == 2:
        game.start(bot.loop.create_task(game_handler(ctx)), resume=True)

    await ctx.send(embed=strings.RESUME_MESSAGE[state])

@interactions.slash_command(name='skip', description='To skip the current round.')
async def skip(ctx):
    game = GAMES.get(ctx.guild.id)
    state = Game.get_state(game)
    if state == 0:
        game.end_round(skipped=True)
    await ctx.send(embed=strings.SKIP_MESSAGE[state])

@interactions.slash_command(
    name='extend',
    description='To extend the current round.',
    # options=[
    #     create_option(
    #         name='duration',
    #         option_type=4,
    #         description='The duration of time to extend the round by.',
    #         required=False
    #     )
    # ]
)
@interactions.slash_option(
    name='duration',
    opt_type=interactions.OptionType.INTEGER,
    description='The duration of time to extend the round by.',
    required=False
)
async def extend(ctx, duration=30):
    game = GAMES.get(ctx.guild.id)
    state = Game.get_state(game)
    if state == 0:
        args = (None, None, duration)
        if helper.has_invalid_args(*args):
            await ctx.send(embed=strings.create_error('Invalid arguments were supplied.'))
            return
        game.round_info['remaining_time'] += duration
    await ctx.send(embed=strings.EXTEND_MESSAGE[state])

@interactions.slash_command(
    name='settings',
    description='To view or change the default settings of a game.',
    # options=[
    #     create_option(
    #         name='points_to_win',
    #         option_type=4,
    #         description='The amount of points needed to win.',
    #         required=False
    #     ),
    #     create_option(
    #         name='rounds',
    #         option_type=4,
    #         description='The total number of rounds in the game.',
    #         required=False
    #     ),
    #     create_option(
    #         name='round_time',
    #         option_type=4,
    #         description='The duration of time each round runs for.',
    #         required=False
    #     )
    # ]
)
@interactions.slash_option(
    name='points_to_win',
    opt_type=interactions.OptionType.INTEGER,
    description='The amount of points needed to win.',
    required=False
)
async def settings(ctx, points_to_win=None, rounds=None, round_time=None):
    global DATA

    args = (points_to_win, rounds, round_time)
    if helper.has_invalid_args(*args):
        await ctx.send(embed=strings.create_error('Invalid arguments were supplied.'))
        return

    updated = False
    if any(args):
        updated = True
        DATA[ctx.guild.id]['settings'] = helper.create_settings(*args)
        print(DATA)
        with open('data.pkl', 'wb') as f:
            pickle.dump(DATA, f)
    await ctx.send(embed=strings.settings_message(DATA[ctx.guild.id]['settings'], updated))

@interactions.listen()
async def on_message_create(event):
    # print(dir(message.message))
    message = event.message
    # print(message.author)
    # print(dir(message))
    if message.author == bot.user:
        return

    game = GAMES.get(message.guild.id)
    if game and game.in_progress:
        print(f'{message.author} : {message.content} : {strings.normalise(message.content)}')
        if game.check(message.author, message.content):
            if not game.score(message.author):
                await message.channel.send(embed=strings.guess_message(game.round_info))
            else:
                game.end_round()

async def game_handler(ctx):
    global GAMES

    server = ctx.guild
    # print(server.voice_state)
    voice_channel = server.voice_state
    # print(voice_channel.stop)
    # print(dir(voice_channel))

    game = GAMES.get(ctx.guild.id)
    settings = DATA[ctx.guild.id]['settings']
    # print('loop running!')
    while game.in_progress:
        # await voice_channel.stop()
        await asyncio.sleep(3)

        round_info = game.round_info
        # print(dir(ctx.channel))
        await ctx.channel.trigger_typing()
        # player = await YTDLSource.from_url(round_info['song_info'])
        # await voice_channel.play(player)
        # print(player.title)

        player = AudioVolume('https://www.youtube.com/watch?v=kffacxfA7G4')
        await voice_channel.play(player)

        await ctx.channel.send(embed=strings.guess_message(round_info))

        game.round_info['remaining_time'] = settings['round_time']
        while game.round_in_progress():
            run_time = game.round_info['remaining_time']
            await asyncio.sleep(run_time)
            game.round_info['remaining_time'] -= run_time

        print('hello')
        await ctx.channel.send(embed=strings.round_message(round_info, game.leaderboard()))
        print('world')
        game.new_round()

    await ctx.channel.send(embed=strings.end_message(game.playlist_info, game.leaderboard()))
    del GAMES[ctx.guild.id]

async def main():
    await bot.astart()

asyncio.run(main())
