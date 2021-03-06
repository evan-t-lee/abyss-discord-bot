import re
import strings

import spotify

class Game:
    def __init__(self, url, settings):
        self.in_progress = False
        self.points_to_win = settings['points_to_win']
        self.playlist_info, self.playlist = spotify.get_playlist(url, settings['rounds'])
        self.scoreboard = {}
        self.round_info = {'round_no': 0, 'in_progress': False}
        self.task = None

    def round_in_progress(self):
        return self.round_info['remaining_time'] > 0

    def start(self, task, resume=False):
        self.in_progress = True
        self.task = task
        if not resume:
            self.new_round()

    def suspend(self):
        if self.in_progress:
            self.task.cancel()
            self.task = None
        self.in_progress = False

    def new_round(self):
        round_no = self.round_info['round_no']
        if round_no == len(self.playlist):
            self.in_progress = False
            return

        song = self.playlist[round_no]
        self.round_info = {
            'round_no': round_no + 1,
            'remaining_time': 0,
            'skipped': False,
            'song_info': (strings.hide_details(song['name']), song['artists'][0]),
            'thumbnail': song['thumbnail'],
            'targets': Game.create_targets(song)
        }
        print('\n-------------------------NEW ROUND---------------------------')
        print(self.round_info)


    def end_round(self, skipped=False):
        self.round_info['skipped'] = skipped
        if self.task and self.task._fut_waiter:
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

    @staticmethod
    def get_state(game):
        if game:
            if game.in_progress:
                if game.round_in_progress():
                    return 0
                return 1
            return 2
        return 3
