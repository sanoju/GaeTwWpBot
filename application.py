# -*- coding: utf-8 -*-
import webapp2
import twwp
import logging

#logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().setLevel(logging.INFO)


class TwWpBotUpdater(webapp2.RequestHandler):
    def get(self):
        twwpbot = twwp.TwWpBot(consumer_key="your_consumer_key",
                               consumer_secret="your_consumer_secret",
                               access_token="your_access_token",
                               access_token_secret="your_access_token_secret",
                               wp_xmlrpc_url='your_wordpress_xmlrpc_url',
                               wp_username='your_wordpress_username',
                               wp_password='your_wordpress_password',
                               keyword='keyword_to_search_on_twitter')

        twwpbot.updateNews()

class TwWpBotTweeter(webapp2.RequestHandler):
    def get(self):
        twwpbot = twwp.TwWpBot(consumer_key="your_consumer_key",
                               consumer_secret="your_consumer_secret",
                               access_token="your_access_token",
                               access_token_secret="your_access_token_secret",
                               wp_xmlrpc_url='your_wordpress_xmlrpc_url',
                               wp_username='your_wordpress_username',
                               wp_password='your_wordpress_password',
                               keyword='keyword_to_search_on_twitter')

        twwpbot.tweetDailyNews()

app = webapp2.WSGIApplication([('/your/application/path/updater', TwWpBotUpdater),
                               ('/your/application/path/tweeter', TwWpBotTweeter)],
                              debug=True)