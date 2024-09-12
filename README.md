# memeVoteBot:

## Features
- Automatically create a like and dislike reaction system in specified channels
- Block the original poster from liking their own meme
- Showcase memes that reach a server-specified threshold of likes
- Delete memes that reach a server-specified threshold of dislikes or recycle emojis (for reuploaded memes)
- Automatically update the like counter of showcased memes as they receive new likes
- Prevent text-only messages from being sent in designated meme channels

## How to host:
Run as a docker container (docker pull ghcr.io/wgrav01/memevotebot:nightly) with a persistant disk and an environment variable titled "TOKEN", (with your token of course) if you have any errors relating to running out of threads set up a cron job to autuomatically restart the bot every hour if possible, and open an issue.

## Disclaimer
- Not actively maintained, (as It Just Works™) but open a PR and I may merge it.
- Apologies for the messy source code, if you are willing to clean it up open a PR!

> Made with ❤️ by WGrav
