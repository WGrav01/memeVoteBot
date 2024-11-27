# memeVoteBot: A Discord bot to assist with managing meme channels

## Features
- Automatically create a like and dislike reaction system in specified channels
- Block the original poster from liking their own meme
- Showcase memes that reach a server-specified threshold of likes
- Delete memes that reach an admin-specified threshold of dislikes or recycle emojis (for reuploaded memes)
- Automatically update the like counter of showcased memes as they receive new likes
- Prevent text-only messages from being sent in designated meme channels

## Add to Discord server
Currently, there is no public bot to add to your Discord server. This may change in the future, (although there is no current plan to do so) but you are welcome to self-host it yourself.

## How to host:
Run as a docker container (`docker pull ghcr.io/wgrav01/memevotebot:nightly`) with a persistant disk and an environment variable titled "TOKEN", (with your Discord bot token) if you have any errors relating to running out of threads set up a cron job to autuomatically restart the bot every hour if possible, and open an issue.

## Disclaimer
- ~~Not actively maintained, (as It Just Works™) but open a PR and I may merge it.~~ (Somewhat maintained)
- Apologies for the messy source code, if you are willing to clean it up open a PR!

> Made with ❤️ by WGrav
