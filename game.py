import re
import strings

from spotify import Spotify

class Game:
    def __init__(self, url, points_to_win, rounds):
        self.in_progress = False
        self.points_to_win = points_to_win
        self.playlist_info, self.playlist  = Spotify.get_playlist(url)[:rounds]
        self.scoreboard = {}
        self.round_info = {'round_no': 0}
        self.task = None

    def start(self, task):
        self.in_progress = True
        self.task = task
        self.new_round()

    def suspend(self):
        self.in_progress = False
        self.round_info['round_no'] = self.round_info.get('round_no', 0) - 1
        self.task.cancel()
        self.task = None

    def new_round(self):
        round_no = self.round_info['round_no']
        if round_no == len(self.playlist):
            self.in_progress = False
            return

        song = self.playlist[round_no]
        self.round_info = {
            'round_no': round_no + 1,
            'skipped': False,
            'search_string': f"{song['name']} {song['artists'][0]} ",
            'thumbnail': song['thumbnail'],
            'targets': Game.create_targets(song)
        }
        print(self.round_info)


    def end_round(self, skipped=False):
        if skipped:
            self.round_info['skipped'] = True
        if self.task._fut_waiter:
            self.task._fut_waiter.set_result(None)
            self.task._fut_waiter.cancel()

    def leaderboard(self):
        leaderboard = {}
        for p, s in self.scoreboard.items():
            leaderboard[s] = leaderboard.get(s, []) + [p.mention]

        iterable = enumerate(sorted(leaderboard, reverse=True))
        leaderboard = [f"**{rank+1}**: {', '.join(leaderboard[s])} ({s})" for rank, s in iterable]
        return '\n'.join(leaderboard)

    def check(self, player, guess):
        targets = self.round_info['targets']
        guess = strings.normalise(guess)
        if guess in targets and not targets[guess]['guessed_by']:
            targets[guess]['guessed_by'] = player
            return True
        return False

    def score(self, player):
        self.scoreboard[player] = self.scoreboard.get(player, 0) + 1

        if self.scoreboard[player] == self.points_to_win:
            self.in_progress = False
            return True

        targets = self.round_info['targets']
        if all([target['guessed_by'] for target in targets.values()]):
            return True
        return False

    @staticmethod
    def create_targets(song):
        targets = {
            strings.normalise(song['name'], True): {
                'type': 'Song',
                'print':  strings.hide_details(song['name']),
                'guessed_by': None
            }
        }
        for artist in song['artists']:
            targets[strings.normalise(artist, True)] = {
                'type': 'Artist',
                'print': strings.hide_details(artist),
                'guessed_by': None
            }
        return targets
