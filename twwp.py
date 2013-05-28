# -*- coding: utf-8 -*-
'''
Created on 2013/02/18

@author: jr
'''

import logging
import time
import urllib2
import util
import tweepy
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost, EditPost
from datetime import date
from datetime import timedelta
from datetime import datetime
import re

#logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().setLevel(logging.INFO)

class TwWpBot(object):
    '''
    Search tweets by some keyword, posts news to WordPress,
    and posts daily news to Twitter.
    '''
    
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret, wp_xmlrpc_url, wp_username, wp_password, keyword):
        '''
        Constructor
        '''
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.wp_xmlrpc_url = wp_xmlrpc_url
        self.wp_username = wp_username
        self.wp_password = wp_password
        self.keyword = keyword
        
        return
    
    def tweet(self, status):
        logging.info(status)
        
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        oauth_api = tweepy.API(auth)
        
        oauth_api.update_status(status)

        time.sleep(30)

        return

    def getNews(self):
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        oauth_api = tweepy.API(auth)
        
        tweets = []
        
        for page in tweepy.Cursor(oauth_api.home_timeline, count=200).pages(1):
            for status in page:
                tweets.append(status)
        
        return tweets
    
    def postNews(self, tweets):
        wp = Client(self.wp_xmlrpc_url, self.wp_username, self.wp_password)
        
        posts = wp.call(GetPosts())
        post = posts[0]
        post_date = post.title[10:]
        
        # Assuming Asia/Tokyo.
        now_tokyo = datetime.now() + timedelta(hours=9)
        today_date = now_tokyo.isoformat().decode('utf-8')[10:]

        if (post_date != today_date):
            post = WordPressPost()
            post.title = u'Tweets on ' + today_date
            post.content = '<script type="text/javascript" src="//platform.twitter.com/widgets.js"></script>'
            post.id = wp.call(NewPost(post))
        
        logging.info(post.id)
    
        htmls = post.content.split('<hr class="tweetboxdelimiter" />')
#        logging.debug(htmls)
        
        tweet_ids = []
        
        for html in htmls:
            match = re.search(r'/status/(\d+)', html)
            if match:
                tweet_ids.append(int(match.group(1)))
        
        logging.info(tweet_ids)
        
        tmpl = u'''
<div class="tweetbox">
<div class="tweetheaderbox">
<a href="https://twitter.com/intent/user?user_id=%s" class="tweetauthorprofile"><img src="%s" /></a>
<a href="https://twitter.com/intent/user?user_id=%s" class="tweetauthorname">%s</a>
<a href="https://twitter.com/intent/user?user_id=%s" class="tweetauthorscreenname">@%s</a>
<a href="https://twitter.com/intent/user?user_id=%s" class="tweetfollow"><img src="/wp-content/themes/slight/images/twitter/bird_gray_16.png" alt="Follow" title="Follow" /></a>
</div>
<div class="tweetcenterbox">%s</div>
<div class="tweetfooterbox">
<a href="https://twitter.com/%s/status/%s" class="tweettimestamp">%s</a>
<div class="tweetactionbox">
<a href="https://twitter.com/intent/tweet?in_reply_to=%s" class="tweetreply"><img src="/wp-content/themes/slight/images/twitter/reply.png" alt="Reply" title="Reply" /></a>
<a href="https://twitter.com/intent/retweet?tweet_id=%s" class="tweetretweet"><img src="/wp-content/themes/slight/images/twitter/retweet.png" alt="Retweet" title="Retweet" /></a>
<a href="https://twitter.com/intent/favorite?tweet_id=%s" class="tweetfavorite"><img src="/wp-content/themes/slight/images/twitter/favorite.png" alt="Favorite" title="Favorite" /></a>
</div>
</div>
</div>
'''.replace("\n", "")

        new_htmls = []
        
        for tweet in tweets:
            if tweet.author.screen_name != u'your_twitter_username':
                if not tweet.id in tweet_ids:
                    if re.match(r'.*' + self.keyword + '.*', tweet.text):
                        logging.info(tweet.text)
                        html = tmpl % (tweet.author.id,
                                       tweet.author.profile_image_url,
                                       tweet.author.id,
                                       tweet.author.name,
                                       tweet.author.id,
                                       tweet.author.screen_name,
                                       tweet.author.id,
                                       tweet.text,
                                       tweet.author.screen_name,
                                       tweet.id,
                                       tweet.created_at + timedelta(hours=9),
                                       tweet.id,
                                       tweet.id,
                                       tweet.id)
            
                        new_htmls.append(html)
        
        if new_htmls:
            htmls = htmls + new_htmls
            html = '<hr class="tweetboxdelimiter" />'.join(htmls)
#            logging.debug(html)
        
            post.content = html
            post.post_status = 'publish'
            wp.call(EditPost(post.id, post))
        
        return
    
    def updateNews(self):
        tweets = self.getNews()
        self.postNews(tweets)
        
        return
    
    def tweetDailyNews(self):
        wp = Client(self.wp_xmlrpc_url, self.wp_username, self.wp_password)
        
        posts = wp.call(GetPosts())
        post = posts[0]
        post_date = post.title[10:]
        
        match = re.search(r'<div class="tweetcenterbox">(.+)</div>', post.content)

        if match:
            text = match.group(1)
            logging.debug(text)
            lead = text[:50]
            logging.debug(lead)
            status = u'Tweets about [' + self.keyword + '] on ' + post_date + ' "' + lead + u'..." ' + post.link
            logging.info(status)
            self.tweet(status)

        return