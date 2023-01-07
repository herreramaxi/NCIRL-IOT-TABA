# REF: https://github.com/ageitgey/face_recognition/blob/master/examples/facerec_from_webcam_faster.py
# This code is based on above example, and adjusted to the requirements from IOT TABA

from dotenv import load_dotenv
from os.path import isfile, join
from os import listdir
import os
from Adafruit_IO import MQTTClient
from datetime import datetime
import face_recognition
import numpy as np
import time
import cv2

load_dotenv()
ADAFRUIT_IO_KEY = os.getenv("ADAFRUIT_IO_KEY")
ADAFRUIT_IO_USERNAME = os.getenv("ADAFRUIT_IO_USERNAME")
DELIMITER_TOKEN = '#'
KNOWN_FACES_FOLDER = 'knownFaces'
BLACK_LIST_FACES_FOLDER = 'BlackList'


def getFaceEncodingsAndNames(folder):
    face_encodings = []
    face_names = []

    print(f"Loading faces from folder: {folder}")
    files = [f for f in listdir(folder) if isfile(join(folder, f))]

    for f in files:
        path = join(folder, f)
        filename, file_extension = os.path.splitext(f)
        face_names.append(filename)

        # print(path)
        image = face_recognition.load_image_file(path)
        face_encoding = face_recognition.face_encodings(image)[0]
        face_encodings.append(face_encoding)

    return face_encodings, face_names


known_face_encodings, known_face_names = getFaceEncodingsAndNames(
    KNOWN_FACES_FOLDER)
blacklist_face_encodings, blacklist_face_names = getFaceEncodingsAndNames(
    BLACK_LIST_FACES_FOLDER)

client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
client.connect()
client.loop_background()

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)
process_this_frame = True
face_locations = []
face_names = []

while True:
    # Grab a single frame of video
    ret, frame = video_capture.read()

    # Only process every other frame of video to save time
    if process_this_frame:
        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(
            rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            dateTime = datetime.now().strftime("%d-%b-%Y %H:%M:%S.%f")
            name = "Unknown"

            # See if the face is a match on blacklist_face_encodings
            blacklist_matches = face_recognition.compare_faces(
                blacklist_face_encodings, face_encoding)
            blacklist_face_distances = face_recognition.face_distance(
                blacklist_face_encodings, face_encoding)
            blacklist_best_match_index = np.argmin(blacklist_face_distances)

            if blacklist_matches[blacklist_best_match_index]:
                name = blacklist_face_names[blacklist_best_match_index]
                client.publish("face-recognition.blacklist",
                               f"{name}{DELIMITER_TOKEN}{dateTime}")
            else:
                known_matches = face_recognition.compare_faces(
                    known_face_encodings, face_encoding)
                face_distances = face_recognition.face_distance(
                    known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)

                if known_matches[best_match_index]:
                    name = known_face_names[best_match_index]
                    client.publish("face-recognition.knownfaces",
                                   f"{name}{DELIMITER_TOKEN}{dateTime}")
                else:
                    client.publish("face-recognition.unknownfaces",
                                   f"Unknown{DELIMITER_TOKEN}{dateTime}")

            face_names.append(name)

    process_this_frame = not process_this_frame

    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35),
                      (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6),
                    font, 1.0, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    time.sleep(1)

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
