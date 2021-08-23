import discord
import re
import string

def round_message(round_info, scoreboard):
    desc = []
    for target in round_info['targets']:
        data = round_info['targets'][target]
        line = f"**{data['type']}**: {data['print']}"
        if data['guessed_by']:
            line += f" guessed by {data['guessed_by'].mention}"
        line = line.ljust(50)
        desc.append(line)
    desc = '\n'.join(desc)
    message = discord.Embed(
        title=f"Round {round_info['round_no']} - Summary",
        description=desc,
        color=discord.Color.blue()
    )
    message.set_thumbnail(url=round_info['thumbnail'])
    message.add_field(name='Leaderboard', value=scoreboard if scoreboard else 'No scores yet.')
    return message

def normalise(s, target=False):
    s = s.lower()
    s = re.sub(r'&', 'and', s)
    if target:
        s = hide_details(s)
    # s = re.sub(r'[\!\?][^w]', ' ', s)
    s = re.sub(r' +', ' ', s)
    s = s.translate(str.maketrans('', '', string.punctuation))
    s = s.strip()
    return s

def hide_details(s):
    s = re.sub(r'[\(\[].+[\)\]]', '', s)
    s = re.sub(r' - .*', '', s)
    s = s.strip()
    return s