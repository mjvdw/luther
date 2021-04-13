import os, logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class Slack(object):

    def __init__(self):
        # WebClient instantiates a client that can call API methods
        # When using Bolt, you can use either `app.client` or the `client` passed to listeners.
        self.client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
        # ID of the channel you want to send the message to
        self.channel_id = "C01N1L6LAN6"

    def send(self, message: str):
        try:
            # Call the chat.postMessage method using the WebClient
            result = self.client.chat_postMessage(
                channel=self.channel_id,
                text=message
            )
            logging.info(result)

        except SlackApiError as e:
            logging.error(f"Error posting message: {e}")
