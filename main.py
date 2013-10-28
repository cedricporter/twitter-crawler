#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Hua Liang[Stupid ET] <et@everet.org>
#

import urllib
import os
import sys
import time
import pickle
from collections import deque

from pyquery import PyQuery as pq
from twitter import Twitter, OAuth, oauth_dance
from twitter.follow import CONSUMER_KEY, CONSUMER_SECRET
from twitter.follow import lookup, follow, rate_limit_status
from twitter import read_token_file
import redis


db = redis.StrictRedis(db=3)
TODO_USER_LIST = deque()


def set_value(redis, key, value):
    redis.set(key, pickle.dumps(value))


def get_value(redis, key):
    pickled_value = redis.get(key)
    if pickled_value is None:
        return None
    return pickle.loads(pickled_value)


def get_user_followers(twitter, user_id, need_follower=True):
    followers = []
    user_ids, users = [], {}
    user_ids = follow(twitter, user_id, need_follower)
    users = lookup(twitter, user_ids)

    for uid in user_ids:
        try:
            followers.append(users[uid])
        except KeyError:
            pass

    return followers


def get_user_followings(twitter, user_id):
    return get_user_followers(twitter, user_id, False)


def get_user_info(user_id):
    url = "https://twitter.com/" + user_id

    try:
        html = urllib.urlopen(url).read()
    except Exception, e:
        return False, e

    html = pq(html)

    info = {}

    # blog
    link = html("span.profile-field a")
    if link:
        blog = link[0].get("title")
        if blog:
            info["blog"] = blog

    # intro
    intro = html(".bio.profile-field").text()
    if intro:
        info["intro"] = intro

    return True, info


def start_crawler(twitter):
    while TODO_USER_LIST:
        set_value(db, "TODO_USER_LIST", TODO_USER_LIST)

        user = TODO_USER_LIST.popleft()
        issuc, info = get_user_info(user)
        if not issuc:
            TODO_USER_LIST.append(user)

        print "[info] info: %s" % info
        print "[Handle] user: %s" % user
        set_value(db, "user:" + user, info)

        TODO_USER_LIST.extend(get_user_followers(twitter, user))
        time.sleep(30)


def main(args=sys.argv[1:]):
    oauth_filename = (os.getenv("HOME", "") + os.sep
                      + ".twitter-follow_oauth")
    if not os.path.exists(oauth_filename):
        oauth_dance("Twitter-Follow", CONSUMER_KEY, CONSUMER_SECRET,
                    oauth_filename)
    oauth_token, oauth_token_secret = read_token_file(oauth_filename)
    auth = OAuth(oauth_token, oauth_token_secret, CONSUMER_KEY,
                 CONSUMER_SECRET)

    twitter = Twitter(auth=auth, api_version='1.1', domain='api.twitter.com')

    # rate_limit_status(twitter)

    TODO_USER_LIST.append("Stupid_ET")
    start_crawler(twitter)


if __name__ == '__main__':
    main()
