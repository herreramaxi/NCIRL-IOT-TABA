# NCIRL-IOT-TABA
## Facial recognition system
The solution provided is a distributed system for facial recognition, that uses the protocol MQTT (message queueing telemetry transport) following publish-subscribe model. Two programs are provided, one for the publisher (publisher.py) and one for the subscriber (subscriber.py).

### Architecture
![alt text](https://github.com/herreramaxi/NCIRL-IOT-TABA/blob/main/solution%20architecture.drawio.png "Architecture")
### MQTT
I am using io.adafruit.com as the broker message with following feeds:
![image](https://user-images.githubusercontent.com/13004153/211159287-7b44093b-d2ad-4095-9264-33626fff49a9.png)

#### .env file for user credentials
User credentials are not included on repository, they are loaded from a .env file with following format:

ADAFRUIT_IO_KEY=A_VALID_KEY <br />
ADAFRUIT_IO_USERNAME=A_VALID_USER_NAME

### Publisher
The publisher uses a web cam to take pictures and try to identify faces detected, comparing those faces with pictures stored on local folders (knownFaces and BlackList). Depending on the faces recognized, the publisher publishes on different feeds as is indicated on below mapping table:
![image](https://user-images.githubusercontent.com/13004153/211152782-4df8dda2-962f-4d15-b3a1-398637a9a0d2.png)

#### How to run it
On an Ubuntu VM (face-recognition is not officially supported for Windows OS) run following command: python3 publisher.py

#### Main dependencies
* face-recognition
* adafruit-io
* cv2 and python-dotenv

### Subscriber
When publisher.py publishes facial recognition data, the MQTT broker (https://io.adafruit.com/) sends a message to the subscribers that are subscribed to specific feeds.
There are four types of subscribers, depending on the parameter the subscriber can be:
* gate: open a gate when detecting a “known face”.
* unknown_faces: inform that an unknown face was detected.
* Blacklist: inform that a person’s face from blacklist was detected.
* time_logger: inform date time when a known person is detected

#### Mapping table: Feed-subscriber type
![image](https://user-images.githubusercontent.com/13004153/211152833-69797f9e-5c85-4bce-8cdf-8ec6646b5d5a.png)

#### How to run it
On a Windows machine, run following command: py .\subscriber.py -t type_of_subscriber -n subscriber_name
Examples: 
* For help: py .\subscriber.py -h
* py .\subscriber.py -t gate -n d01
* py .\subscriber.py -t gate -n d02
* py .\subscriber.py -t blacklist -n blacklist_detector
* py .\subscriber.py -t unknown_faces -n unknown_faces_detector
