#!/usr/bin/env python3

import hug
import hashlib
import time
import json

users = {"admin": {}}
tokens = {}
channels = {}

class Message(object):
    def __init__(self, user, message, files):
        self.user = user
        self.ts = time.time()
        self.message = message
        self.files = files

def valid_user(username: str):
    """ Existing username """
    if username in users:
        return username
    raise Exception("User not found")

def valid_token(token: str):
    """ Valid token obtained from get_token """
    if token in tokens:
        return token
    raise Exception("Invalid token")

def valid_admin_token(token: str):
    """ Valid admin token obtained from get_token """
    if valid_token(token) and tokens[token] == 'admin':
        return token
    raise Exception("Invalid admin token")

def valid_channel(channel: str):
    """ Existing channel """
    if channel in channels:
        return channel
    raise Exception("Channel does not exist")

@hug.get(examples='username=admin&password=admin')
def get_token(username: valid_user, password: hug.types.text):
    """ Get user token for all API operations. Each call will generate a unique token. """
    user_token = hashlib.sha224((username+password).encode("raw_unicode_escape")).hexdigest()
    users[username]["token"] = user_token
    tokens[user_token] = username
    return {"token": user_token}

@hug.get(examples='token=<token>&username=carmack')
def add_user(token: valid_admin_token, username: hug.types.text):
    """ Add a new user to the system. Only works with admin user token. Will raise a 404 error if user already exists """
    if username in users:
        return {"errors": {"username": "Username already exists"}}
    users[username] = {}
    return {"username": username}

@hug.get(examples='token=<token>&channel=linuxusers')
def add_channel(token: valid_admin_token, channel: hug.types.text):
    """ Add a new channel to the system. Only works with admin user token. Will raise an error if channel already exists """
    channels[channel] = []
    return {"channel": channel}

@hug.post(examples='')
def send_message(token: valid_token, channel: valid_channel, message:hug.types.text, files):
    """ Send a message to the given channel. Message can be up to 1024 characters, attachments can be .jpg images up to 2MB size """
    m = Message(tokens[token], message,files)
    channels[channel].append(m)
    return {"timestamp": m.ts, "user": m.user, "message": m.message}

@hug.get(examples='token=<token>&channel=linuxusers&from_timestamp=0')
def read_channel(token: valid_token, channel: valid_channel, from_timestamp: hug.types.float_number):
    """ Return a list of messages in the given channel, starting from the specified time. Each message is a dictionary
        containing the following fields: user, message, ts, files. """
    return {"messages": [json.dumps(m.__dict__) for m in channels[channel] if m.ts >= from_timestamp]}

@hug.get(examples='token=<token>')
def clean_db(token: valid_admin_token):
    """ Remove all created entities - channels, users, messages"""
    global users, tokens, channels
    users = {"admin": {}}
    tokens = {}
    channels = {}
