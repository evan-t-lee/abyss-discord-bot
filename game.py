import re
import string

from spotify import Spotify

class Game:
    def __init__(self, url, points_to_win=10, rounds=25):
        self.in_progress = False
        self.points_to_win = points_to_win
        self.playlist = Spotify.generate_playlist_from_url(url)[:rounds]
        self.scoreboard = {}
        self.curr_round = None

    def new_round(self):
        song = self.playlist.pop(-1)
        curr_round = {
            'search string': f"{song['artists'][0]} {song['name']} audio",
            'targets': Game.create_targets(song)
        }
        print(curr_round)
        self.curr_round = curr_round

    def get_scoreboard(self):
        return [(p, s) for p, s in sorted(self.scoreboard.items(), key=lambda p: -p[1])]

    def start(self):
        self.in_progress = True

    def pause(self):
        self.in_progress = False

    def check(self, player, guess):
        targets = self.curr_round['targets']
        guess = Game.normalise(guess)
        if guess in targets and not targets[guess]['guessed']:
            targets[guess]['guessed'] = True
            self.scoreboard[player] = self.scoreboard.get(player, 0) + 1

            if self.scoreboard[player] == self.points_to_win:
                return 'end'
            return True
        return False

    @staticmethod
    def create_targets(song):
        targets = {
            Game.normalise(song['name']): {
                'type': 'Song',
                'print': song['name'],
                'guessed': False
            }
        }
        for artist in song['artists']:
            targets[Game.normalise(artist)] = {
                'type': 'Artist',
                'print': artist,
                'guessed': False
            }
        return targets

    @staticmethod
    def normalise(s):
        s = s.lower()
        s = re.sub(r'\(.+\)', '', s)
        s = s.translate(str.maketrans('', '', string.punctuation))
        return s