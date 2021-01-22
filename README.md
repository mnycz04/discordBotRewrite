## discordBotRewrite
 A Rewrite of my discord Bot, with optimizations and fixes.


# Commands

## reddit
A command that takes one argument, subreddit, to grab a random post from.
>>>$reddit memes
 returns a random post from r/memes
 alaises = r, red
 
## purge
A command that takes one optional argument, limit, which deletes a large amount of messages = limit
default of limit is 10
>>>$purge 1000
Deletes 1000 messages
>>>$purge
deletes 10 messages
aliases = delete

## schedule
A command that returns an image of our school schedule
>>>$schedule
aliases= shed

## ping
A command that takes two optional arguments, IP, and port.
The command will try to establish a TCP connection with IP on port.
>>>$ping 0.0.0.0:0000


# Required Permissions

This bot would require permissions to delete messages, send messages, and send embeds.
