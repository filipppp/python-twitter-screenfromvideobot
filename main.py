import json
import tweepy
import cv2
import sys
import traceback
import logging
from os import listdir, execl
from os.path import isfile, join


auth = tweepy.OAuthHandler(consumer_key='',
                           consumer_secret='')
auth.set_access_token(key='',
                      secret='')
api = tweepy.API(auth)


with open("config.json") as config:
    config = json.load(config)

try:
    frameCounter = int(config["nextFrame"])
except KeyError:
    frameCounter = config["startDelay"]

try:
    test = int(config["videoIndex"])
except KeyError:
    config["videoIndex"] = 0

try:
    files = [join(config["videoDir"], f) for f in listdir(config["videoDir"]) if isfile(join(config["videoDir"], f))]
    cap = cv2.VideoCapture(files[config["videoIndex"]])
    FPS = int(cap.get(cv2.CAP_PROP_FPS))
    END_DELAY = FPS * config["endDelay"]
    START_DELAY = FPS * config["startDelay"]
    frameCounter += START_DELAY
    INTERVALL = config["intervall"]
except Exception as e:
    logging.error(traceback.format_exc())
    sys.exit()

rval = True

while rval:
    rval, frame = cap.read()
    if cap.get(cv2.CAP_PROP_POS_FRAMES) == frameCounter:
        cv2.imwrite("temp.jpg", frame)
        config["nextFrame"] = frameCounter + INTERVALL * FPS
        with open("config.json", "w") as newConf:
            json.dump(config, newConf)
        api.update_with_media("temp.jpg")
        sys.exit(0)
    cv2.waitKey(1)
cap.release()

config["videoIndex"] += 1

if config["videoIndex"] > len(files):
    config["videoIndex"] = 0
config["nextFrame"] = 0
with open("config.json", "w") as newConf:
    json.dump(config, newConf)

execl(sys.executable, sys.executable, *sys.argv)


