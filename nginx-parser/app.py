import os
import sys
import re
import requests
import json
import time
import logging

root = logging.getLogger()
root.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

URL = "http://localhost:8080"
INPUT_LOG = "/var/log/nginx/access.log"
INTERVAL=5
LOGREGFORMAT ='(?P<ipaddress>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - \[(?P<dateandtime>\d{2}\/[a-z]{3}\/\d{4}:\d{2}:\d{2}:\d{2} (\+|\-)\d{4})\] ((\"(GET|POST) )(?P<url>.+)(http\/1\.1")) (?P<statuscode>\d{3}) (?P<bytessent>\d+) (["](?P<refferer>(\-)|(.+))["]) (["](?P<useragent>.+)["]) (["](?P<host>.+)["])'


LOGREGFORMAT = re.compile(LOGREGFORMAT, re.IGNORECASE)
def readFile():
    with open(INPUT_LOG, "r") as f:
        SMRF1 = f.readlines()
    return SMRF1

def send(json_data,URL):
    headers = {'content-type': 'application/json'}
    requests.post(URL, data=json.dumps(json_data),headers=headers)

initial = readFile()
root.debug("parser started")
while True:
    current = readFile()
    if initial != current:
        for line in current:
            if line not in initial:
                data = re.search(LOGREGFORMAT, line)
                try:
                    datadict = data.groupdict()
                except:
                    root.debug("Invalid log format (None type)")
                send(datadict,URL)
                root.debug(datadict)
        initial = current
    time.sleep(int(INTERVAL))
