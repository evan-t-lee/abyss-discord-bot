# Abyss

## Usage

Click this [link](https://discord.com/api/oauth2/authorize?client_id=878333211946672188&permissions=8&scope=bot%20applications.commands) to invite Abyss to your Discord server, then follow the steps and accept the permissions.

Once Abyss has succesfully joined the server, just start a game by typing `/play` and following the tab prompts in any channel. Abyss will join the voice channel you are currently in and begin the game, just follow Abyss' message prompts to play.

The following are the list of commands with which to use Abyss.

#### Commands

`/play {playlist_link} {points_to_win} {rounds}`

Connects Abyss to the user's voice channel and starts a game with the specified settings if supplied, otherwise the defaults are used.

- **playlist\_link**: The spotify playlist that you want to use for the game, this can be found by right clicking the playlist, then clicking share and copying the playlist link.
- **points\_to\_win** (optional): The amount of points needed to win the game.
- **rounds** (optional): The amount of rounds in a game

`/end`

Ends any currently running game, will continue to play the last song.

`/pause`

Pauses the game in the current state if there is a game currently running. Cannot be called before a round has started.

`/resume`

Resumes the game to the last played round while retaining state at which the game was paused.

`/skip`

Skips the current round being played, while retaining any points that may have been earned. Cannot be called before a round has started.

`/extend {duration}`

Extends the current round by 30 seconds or the specified duration if supplied. Note that this is in addition to the original duration of each round.

- **duration**: The duration of time that you would like to extend the round by, acceptable range is between 10 and 60.

`/leave`

Disconnects Abyss from any voice channel it may be connected to and forcibly ends any games currently being played.

`/settings {points_to_win} {rounds} {round_time}`

When no arguments are supplied, will show the current settings of a game. With any arguments, the updated settings will be shown.

- **points\_to\_win** (optional): The amount of points needed to win the game, default is set to 15.
- **rounds** (optional): The amount of rounds in a game, default is set to 30.
- **round\_time** (optional): The duration of time each round runs for, default is set to 30 and acceptable range is between 10 and 60 but can be extended by */extend*.

## Versions

### V1.3 (Current)

**Released 03/09/21**

- **New** `/settings` command to view or change the default settings of a game..
- **Updated** song searching algorithm to select song more accurately.
- **Updated** `/extend` command to handle varying extend durations.
- **Updated** commands to handle more invalid arguments.
- **Fixed** bug with games not being properly ended.

### V1.2

**Released 30/08/21**

- **New** readme documentation on how to use bot.
- **New** `/extend` command will extend the current round by 30 seconds.
- **Fixed** bug with game not ending when round limit was reached.
- **Fixed** bug with rounds not being correctly shown when playlist was less than rounds.
- Tldr: Faster performance and cleaner code.
	- Abstracted functionality of string comparison and message generation.
	- Games now use *guild_id* as keys instead of the entire guild.

### V1.1

**Released 28/08/21**

- Split /end functionality into /leave and /end.
	- **New** `/leave` command will cause bot to leave any voice channels, will also force end any games in progress.
	- **Updated** `/end` command will end the current game but bot will remain in voice channel and continue playing the last song.
- **Updated** bot to handle multiple games in different servers.
- **Fixed** issue with /end when game is paused.
- **Fixed** issue with extremely large playlists.

### V1.0

**Released 26/08/21**

- First version of bot deployed and now available on live servers!
- Available commands: /play, /end, /pause, /resume, and /skip
