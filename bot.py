from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

from gtts import gTTS
import os

app = Flask(__name__)

line_bot_api = LineBotApi('2m0r9EIU+Hg4LYMixZf2eIvwRqQSEY7hHNWmdooEIzlDYmDMwHysOf3SOFMZ7/DQgNr64qh0VXZ1eRaHQmpEgFuA2inyca1SOzB8oPIwaPU9O9Vuv/47M7U3WbARNi4lUzqBth1UYxAakQuN/a5/sgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('96b8579ecc77bbd327d8ca59778a040a')


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
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = open('output.txt', 'r').read() 
    myobj = gTTS(text=msg, lang='en', slow=False) 
    myobj.save("output.mp3")
    os.system('start output.mp3')
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=msg))


if __name__ == "__main__":
    app.run()
