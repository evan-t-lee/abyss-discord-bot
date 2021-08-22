# bot.py
import os
from dotenv import load_dotenv

import asyncio
import discord
from discord.ext import commands,tasks

from ytdl import YTDLSource
from game import Game

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# 2
intents = discord.Intents().all()
bot = commands.Bot(command_prefix='!', intents=intents)

game = None

@bot.event
async def on_ready():
	print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='play', help='To play song')
async def play(ctx, *, url):
	global game

	if ctx.voice_client is None:
		if ctx.author.voice:
			await ctx.author.voice.channel.connect()
		else:
			await ctx.send("You are not connected to a voice channel.")
			raise commands.CommandError("Author not connected to a voice channel.")

	game = Game(url)
	game.start()

	bot.loop.create_task(game_handler(ctx))

@bot.command(name='end', help='To end game')
async def end(ctx):
	global game

	if not game:
		await ctx.send('No game in progress.')
		return

	server = ctx.message.guild
	voice_channel = server.voice_client
	await voice_channel.disconnect()

	scores = [f'{p}: {s}' for p, s in game.get_scoreboard()]
	game = None

	end_message = '\n'.join(scores)
	await ctx.send(end_message)

@bot.event
async def on_message(message):
	if message.author == bot.user:
		return

	if game and game.in_progress:
		if game.check(message.author.name, message.content):
			round_message = discord.Embed()

			targets = game.curr_round['targets']
			for target in targets:
				data = targets[target]
				if data['guessed']:
					round_message.add_field(name=data['type'], value=data['print'])
				else:
					round_message.add_field(name=data['type'], value='???')
			await message.channel.send(embed=round_message)

		print(message.author.name, message.content)

	await bot.process_commands(message)

async def game_handler(ctx):
	server = ctx.message.guild
	voice_channel = server.voice_client

	while game.in_progress:
		voice_channel.stop()
		await asyncio.sleep(3)

		game.new_round()
		curr_round = game.curr_round

		async with ctx.typing():
			player = await YTDLSource.from_url(curr_round['search string'], loop=bot.loop, stream=True)
			voice_channel.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

		message = discord.Embed()
		message.add_field(name='Song', value='???')
		for _ in range(len(curr_round['targets'])-1):
			message.add_field(name='Artist', value='???')
		await ctx.send(embed=message)
		print(player.title)

		await asyncio.sleep(30)

@bot.command(name='test')
async def test(ctx, *, url):
	server = ctx.message.guild
	voice_channel = server.voice_client
	if ctx.voice_client is None:
		if ctx.author.voice:
			await ctx.author.voice.channel.connect()
		else:
			await ctx.send("You are not connected to a voice channel.")
			raise commands.CommandError("Author not connected to a voice channel.")
	else:
		voice_channel.stop()

	server = ctx.message.guild
	voice_channel = server.voice_client

	async with ctx.typing():
		player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
		voice_channel.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

	await ctx.send(f'testing {player.title}')
	print(player.title)

bot.run(TOKEN)
