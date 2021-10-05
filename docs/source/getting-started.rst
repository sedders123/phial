Getting started with phial
===========================

## What can phial do?

phial's a Slack bot framework. That means that with phial you can build your very own bot that'll respond to commands and do other things in your Slack workspace. You can read more about Slack bots [here](https://api.slack.com/bot-users). 

## Installation thru pip

`pip install phial`

## Setting up your bot

To make your own bot, you'll need the following ~~ingredients~~ parts:

* A Slack workspace (that you're an admin of)
* A basic understanding of Python
* A Python 3 installation
* A copy of phial

Log in to your Slack community and create an 'app' on it: https://api.slack.com/apps?new_app=1

![The Slack 'Create a Slack App' dialogue](https://i.imgur.com/xS97o8M.png)

Now let's add a bot user to your app:

![The method to add a Bot User](https://i.imgur.com/ZEgL2ca.png)

Give it a name and username. You'll probably want to set it to always be online. You can customise the bot later, but for now you'll need the bot's credentials for your phial instance.

On the "basic information" tab of the app, click "install app into workplace". For the next step, you'll need to copy the "bot user oauth access token":

![The process for setting up the app and grabbing the token](https://i.imgur.com/mN6ZWMZ.png)

Last but not least, you'll need some permissions for the bot to work. On the "oauth & permissions" tab, add the following permissions:

* Send messages as \<username> (`chat:write:bot`)
* Post to specific channels in Slack (`incoming-webhook`)
* Add a bot user with the username @\<username> (`bot`)
* Add slash commands and add actions to messages (and view related content) (`commands`)

You'll then need to re-authorise the app with your workspace.

Create a new instance of phial with the token you got in the last step:

```python
from phial import Phial

bot = Phial('xoxb--your-token-here-000zzz')

bot.run()
```

Run the function and you should get the following output:

> λ py run.py    
> 2018-10-01 09:41:00,000 - Phial connected and running!

## Example 0 - Hello World

## Example 1 - Ping Pong

## Example 2 - Hello User