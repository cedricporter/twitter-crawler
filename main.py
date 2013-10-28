#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Hua Liang[Stupid ET] <et@everet.org>
#

import subprocess
import os
import sys

from twitter import follow, Twitter, OAuth, oauth_dance
from twitter.follow import CONSUMER_KEY, CONSUMER_SECRET
from twitter.follow import lookup
from twitter import read_token_file


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

    need_followers = True

    # obtain list of followers (or following) for every given user
    for user in ["Stupid_ET", ]:
        user_ids, users = [], {}
        user_ids = follow(twitter, user, need_followers)
        users = lookup(twitter, user_ids)

        for uid in user_ids:
            try:
                print(users[uid].encode("utf-8"))
            except KeyError:
                pass


if __name__ == '__main__':
    main()
