import argparse
import sys
import time
from Adafruit_IO import MQTTClient
from dotenv import load_dotenv
import os 

load_dotenv()
ADAFRUIT_IO_KEY = os.getenv("ADAFRUIT_IO_KEY")
ADAFRUIT_IO_USERNAME = os.getenv("ADAFRUIT_IO_USERNAME")
DELIMITER_TOKEN = '#'

parser = argparse.ArgumentParser(
    prog='Subscriber',
    description='Face Recognition Subscriber')
parser.add_argument("-t", "--type", required=True, choices=[
                    'gate', 'unknown_faces', 'blacklist', 'time_logger'], help='Type of subscriber to be started')
parser.add_argument("-n", "--name", required=True, help='Subscriber name')
args = parser.parse_args()

subscriberType = args.type
subscriberName = args.name
print(f"Subscriber type: {subscriberType}")
print(f"Subscriber name: {subscriberName}")

if (subscriberType == 'gate' or subscriberType == 'time_logger'):
    feedName = "face-recognition.knownfaces"
elif subscriberType == 'blacklist':
    feedName = "face-recognition.blacklist"
else:
    feedName = "face-recognition.unknownfaces"


def process_message_gate(faceDetected, time):
    print(f"Open the gate {subscriberName} for user {faceDetected} at {time}")


def process_message_unknown_faces(faceDetected, time):
    print(f"Unknown face detected on subscriber {subscriberName} at {time}")


def process_message_blacklist_faces(faceDetected, time):
    print(
        f"Blacklist face detected, name of user: {faceDetected}, subscriberName: {subscriberName}, date time:{time}")


def process_message_time_logger(faceDetected, time):
    print(
        f"Log time on subscriber {subscriberName} for user {faceDetected} at {time}")


def process_message_default(faceDetected, time):
    print(
        f"Not possible to process message, callback not found for {subscriberType}")


process_message_callbacks = {
    "gate": process_message_gate,
    "unknown_faces": process_message_unknown_faces,
    "blacklist": process_message_blacklist_faces,
    "time_logger": process_message_time_logger,
    "default": process_message_default,
}


def connected(client):
    client.subscribe(feedName)
    print(f"Subscribed to feed: {feedName}")
    print(f"Listening on feed {feedName}, press Ctrl-C to quit...")


def disconnected(client):
    print('Disconnected from Adafruit IO')
    sys.exit(1)


def message(client, feed_id, payload):
    if DELIMITER_TOKEN not in payload:
        print("Not possible to process message, DELIMITER_TOKEN not found")
        return

    payloadArray = payload.split(DELIMITER_TOKEN)

    if len(payloadArray) != 2:
        print("Not possible to process message, wrong format")
        return

    face = payloadArray[0]
    time = payloadArray[1]
    callbackIndex = subscriberType if subscriberType in process_message_callbacks else "default"

    process_message_callbacks[callbackIndex](face, time)


client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message

client.connect()
client.loop_background()

while True:
    time.sleep(1)
