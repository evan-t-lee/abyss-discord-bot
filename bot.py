# bot.py
import os
from dotenv import load_dotenv

import asyncio
import discord
from discord.ext import commands,tasks

from ytdl import YTDLSource
from game import Game
import generate

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

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
	game.start(bot.loop.create_task(game_handler(ctx)))

@bot.command(name='end', help='To end game')
async def end(ctx):
	global game

	if not game:
		await ctx.send('No game in progress.')
		return

	server = ctx.message.guild
	voice_channel = server.voice_client
	await voice_channel.disconnect()

	scores = [f'@{p} {s}' for p, s in game.get_scoreboard()]
	desc = '\n'.join(scores)
	game = None

	end_message = discord.Embed(
		title='Game Summary',
		description=desc,
		color=discord.Color.red()
	)

	await ctx.send(embed=end_message)

@bot.event
async def on_message(message):
	if message.author == bot.user:
		return
	# await message.channel.send('hi' + message.author.mention)

	if game and game.in_progress:
		if game.check(message.author, message.content):
			round_info = game.round_info
			if not game.score(message.author):
				score_message = discord.Embed()

				targets = round_info['targets']
				for target in targets:
					data = targets[target]
					if data['guessed_by']:
						score_message.add_field(name=data['type'], value=f"{data['print']} guessed by {data['guessed_by'].mention}")
					else:
						score_message.add_field(name=data['type'], value='???')
				await message.channel.send(embed=score_message)
			else:
				round_message = generate.round_message(round_info, game.scoreboard_string())
				await message.channel.send(embed=round_message)

				game.skip()

		print(message.author.name, message.content, Game.normalise(message.content))

	await bot.process_commands(message)

async def game_handler(ctx):
	server = ctx.message.guild
	voice_channel = server.voice_client

	while game.in_progress:
		voice_channel.stop()
		await asyncio.sleep(3)

		game.new_round()
		round_info = game.round_info

		async with ctx.typing():
			player = await YTDLSource.from_url(round_info['search string'], loop=bot.loop, stream=True)
			voice_channel.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

		message = discord.Embed()
		targets = round_info['targets']
		for target in targets:
			message.add_field(name=targets[target]['type'], value='???')

		await ctx.send(embed=message)
		print(player.title)

		await asyncio.sleep(30)

bot.run(TOKEN)
