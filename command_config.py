import os
from dotenv import load_dotenv
import requests

load_dotenv()
APP_ID = os.getenv('APPLICATION_ID')
GUILD_ID = os.getenv('DISCORD_GUILD')
TOKEN = os.getenv('DISCORD_TOKEN')

r = input('method: ')

# URL
url = f'https://discord.com/api/v8/applications/{APP_ID}/guilds/{GUILD_ID}/commands'
if r.startswith('del'):
    r, command_id = r.split()
    url += f'https://discord.com/api/v8/{command_id}'

# url = 'https://discord.com/api/v8/gateway/bot'

# PAYLOAD
json = {
    "name": "test",
    "type": 1,
    "description": "testing command."
}

headers = {
    "Authorization": f"Bot {TOKEN}"
}

# REQUEST
result = 'invalid request'
if r.startswith('post'):
    result = requests.post(url, json=json, headers=headers)
elif r.startswith('get'):
    result = requests.get(url, headers=headers)
elif r.startswith('del'):
    result = requests.delete(url, headers=headers)

print(result)
if result != 'invalid request':
    print(result.json())
