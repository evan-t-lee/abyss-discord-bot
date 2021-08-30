# Abyss

## Usage

Click this [link](https://discord.com/api/oauth2/authorize?client_id=878333211946672188&permissions=8&scope=bot%20applications.commands) to invite Abyss to your Discord server, then follow the steps and accept the permissions.

Once Abyss has succesfully joined the server, just start a game by typing `/play` and following the tab prompts in any channel. Abyss will join the voice channel you are currently in and begin the game, just follow Abyss' message prompts to play.

The following are the list of commands with which to use Abyss.

#### Commands

`/play {playlist_link} {points_to_win} {rounds}`

Connects Abyss to the user's voice channel and starts a game with the specified settings.

- **playlist\_link**: The spotify playlist that you want to use for the game, this can be found by right clicking the playlist, then clicking share and copying the playlist link.
- **points\_to\_win** (optional): The amount of points needed to win the game, default is set to 15.
- **rounds** (optional): The amount of rounds in a game, default is set to 30.

`/end`

Ends any currently running game, will continue to play the last song.

`/pause`

Pauses the game in the current state if there is a game currently running. Cannot be called before a round has started.

`/resume`

Resumes the game to the last played round while retaining state at which the game was paused.

`/skip`

Skips the current round being played, while retaining any points that may have been earned. Cannot be called before a round has started.

`/extend`

Extends the current round, this is not in addition to the original 30 seconds but rather plays for 30 seconds from the point the command was called.

`/leave`

Disconnects Abyss from any voice channel it may be connected to and forcibly ends any games currently being played.

## Versions

### V1.2 (Current)

**Released 30/08/21**

- **New** readme documentation on how to use bot.
- **New** `/extend` command will extend the current round by 30 seconds.
- **Updated** song searching algorithm to select song more accurately.
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
