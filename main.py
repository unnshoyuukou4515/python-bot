from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, LocationMessage
)
from linebot.v3.messaging import MessagingApi
import scrape as sc
from geopy.distance import geodesic
import os

app = Flask(__name__)
user_requests = {}

# 環境変数
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
messaging_api = MessagingApi(line_bot_api)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text
    user_requests[user_id] = text

    if '天気' in text:
        messaging_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text='Your location Please'),
                TextSendMessage(text='line://nv/location')
            ]
        )
    elif 'weather' in text:
        result = sc.get_weather_from_english()
        messaging_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result)
        )
    elif 'CC' in text:
        messaging_api.reply_message(
            event.reply_token,
            [TextSendMessage(text='Your location Please'), 
             TextSendMessage(text='line://nv/location')]
        )
    else:
        messaging_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text)
        )

CC_location = (35.6547486111, 139.7307916667)

@handler.add(MessageEvent, message=LocationMessage)
def handle_location(event):
    user_id = event.source.user_id
    user_location = (event.message.latitude, event.message.longitude)
    result = "Failed to process request"

    if user_requests.get(user_id) == '天気':
        result = sc.get_weather_from_location_JP(event.message.address)
    elif user_requests.get(user_id) == 'CC':
        distance = geodesic(user_location, CC_location).kilometers
        result = f'You are {distance:.2f} km away from Code Chrysalis.'

    messaging_api.reply_message(
    event.reply_token,
    [TextSendMessage(text=result)]
)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
