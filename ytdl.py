import discord
import youtube_dl
from ytmusicapi import YTMusic
from strings import similarity_ratio

ytm = YTMusic()

# YTDL constatnts
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

def get_url(song_info):
    search_string = f"{song_info[0]} {song_info[1]}"
    res1 = ytm.search(search_string, 'songs')
    res2 = ytm.search(search_string, 'videos')

    if not res1 and not res2:
        return search_string

    if res1 and res2:
        res1_artist = res1[0]['artists'][0]['name'].lower()
        res2_artist = res2[0]['artists'][0]['name'].lower()
        res1_ratio = similarity_ratio(res1_artist, song_info[1])
        res2_ratio = similarity_ratio(res2_artist, song_info[1])
        print(f"{res1_artist} : {res1_ratio} : youtu.be/{res1[0]['videoId']}")
        print(f"{res2_artist} : {res2_ratio} : youtu.be/{res2[0]['videoId']}")
        if res1_ratio >= 0.8 or res2_ratio >= 0.8:
            return res1[0]['videoId'] if res1_ratio >= res2_ratio else res2[0]['videoId']
    return res2[0]['videoId'] if res2 else res1[0]['videoId']

# Youtube Download
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, song_info, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        url = get_url(song_info)
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        return cls(discord.FFmpegPCMAudio(data['url'], **ffmpeg_options), data=data)
