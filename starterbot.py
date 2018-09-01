import os
import time
import re
from slackclient import SlackClient
import datetime
import catchphrase_list as cl
import random

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "get quote"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
ian_count = 0
phrases = cl.catchphrases
random.shuffle(phrases)

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(EXAMPLE_COMMAND):
        post_ian_catchphrase(channel)
        return

    if command.startswith("sass"):
        sass()
        return

    if command.startswith("echo"):
        echo(command)
        return

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )

def post_ian_catchphrase(channel="#house-crew"):
    global ian_count
    global phrases
    if ian_count == len(phrases):
        ian_count = 0
        random.shuffle(phrases)
    message = "Ian's catch phrase of the day is:\n>"
    message = message + phrases[ian_count]
    ian_count = ian_count + 1
    slack_client.api_call(
        "chat.postMessage",
        channel = channel,
        text=message
    )

def sass(channel="#house-crew"):
    message = cl.navy
    slack_client.api_call(
        "chat.postMessage",
        channel = channel,
        text=message
    )


def echo(message, channel="#house-crew"):
    message = message[5:]
    slack_client.api_call(
        "chat.postMessage",
        channel = channel,
        text=message
    )
if __name__ == "__main__":
    if slack_client.rtm_connect(auto_reconnect=True,with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            now = datetime.datetime.now()
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
            if now.hour == 13 and now.minute == 0 and now.second == 00:
        	    post_ian_catchphrase()

    else:
        print("Connection failed. Exception traceback printed above.")
