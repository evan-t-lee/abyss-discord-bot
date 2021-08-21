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
            'song': song,
            'targets': [
                {'song': song['name']},
                # insert artist
            ]
        }
        print(curr_round)
        self.curr_round = curr_round
        return curr_round

    def get_scoreboard(self):
        return [(p, s) for p, s in sorted(self.scoreboard.items(), key=lambda p: -p[1])]

    def start(self):
        self.in_progress = True

    def pause(self):
        self.in_progress = False

    def score(self, player):
        self.scoreboard[player] = self.scoreboard.get(player, 0) + 1
        if self.scoreboard[player] == self.points_to_win:
            return 'end'
