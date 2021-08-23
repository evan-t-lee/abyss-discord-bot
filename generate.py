import discord

def round_message(round_info, scoreboard):
	targets = round_info['targets']
	desc = '\n'.join([f"**{targets[t]['type']}**: {targets[t]['print']} guessed by {targets[t]['guessed_by'].mention}" for t in targets])
	message = discord.Embed(
		title='Round Summary',
		description=desc,
		color=discord.Color.blue()
	)
	message.set_thumbnail(url=round_info['thumbnail'])
	message.add_field(name='Leaderboard', value=scoreboard)
	return message