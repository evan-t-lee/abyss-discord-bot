import re
import string

from spotify import Spotify

class Game:
    def __init__(self, url, points_to_win=10, rounds=25):
        self.in_progress = False
        self.points_to_win = points_to_win
        self.playlist = Spotify.create_playlist_from_url(url)[:rounds]
        self.scoreboard = {}
        self.round_info = None
        self.task = None

    def start(self, task):
        self.in_progress = True
        self.task = task

    def pause(self):
        self.in_progress = False

    def skip(self):
        self.task._fut_waiter.set_result(None)
        self.task._fut_waiter.cancel()

    def new_round(self):
        song = self.playlist.pop(-1)
        round_info = {
            'search string': f"{song['artists'][0]} {song['name']} audio",
            'thumbnail': song['thumbnail'],
            'targets': Game.create_targets(song)
        }
        print(round_info)
        self.round_info = round_info

    def scoreboard_string(self):
        leaderboard = {}
        for p, s in self.scoreboard.items():
            leaderboard[s] = leaderboard.get(s, []) + [p.mention]

        iterable = enumerate(sorted(leaderboard, reverse=True))
        leaderboard = [f"**{rank+1}**: {', '.join(leaderboard[s])} ({s})" for rank, s in iterable]
        return '\n'.join(leaderboard)

    def check(self, player, guess):
        targets = self.round_info['targets']
        guess = Game.normalise(guess)
        if guess in targets and not targets[guess]['guessed_by']:
            targets[guess]['guessed_by'] = player
            return True
        return False

    def score(self, player):
        self.scoreboard[player] = self.scoreboard.get(player, 0) + 1

        if self.scoreboard[player] == self.points_to_win:
            self.in_progress = False

        targets = self.round_info['targets']
        if all([target['guessed_by'] for target in targets.values()]):
            return True
        return False


    @staticmethod
    def create_targets(song):
        targets = {
            Game.normalise(song['name']): {
                'type': 'Song',
                'print': song['name'],
                'guessed_by': None
            }
        }
        for artist in song['artists']:
            targets[Game.normalise(artist)] = {
                'type': 'Artist',
                'print': artist,
                'guessed_by': None
            }
        return targets

    @staticmethod
    def normalise(s):
        s = s.lower()
        s = re.sub(r'\(.+\)', '', s)
        s = re.sub(r'&', 'and', s)
        s = s.translate(str.maketrans('', '', string.punctuation))
        s = s.strip()
        return s