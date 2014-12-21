from Bot import Bot, Comment, Submission
from Tables import Swap, Inventory
from Post import Post
from Decorators import CountDecorator
from threading import Timer
from datetime import datetime
import re
import sqlite3
import logging 

class SwapBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.owner = 'FlockOnFire'

        name = '@SwapBot'
        self.comment_triggers = [
           #add
           (re.compile(r'{name} (add|swap complete)'.format(name=name), re.I),
            self.add_swap),
           #inventory
           (re.compile(r'{name} inv'.format(name=name), re.I),
            self.get_inventory),
           #list
           (re.compile(r'{name} (swaps|trades)'.format(name=name), re.I), 
            self.get_swaps),
        ]
        self.submission_triggers =  [
            #add
            (re.compile(r'{name} (add|swap complete)'.format(name=name), re.I),
             self.add_swap),
            #inventory
            (re.compile(r'{name} inv'.format(name=name), re.I),
             self.get_inventory),
            #list
            (re.compile(r'{name} (swaps|trades)'.format(name=name), re.I), 
             self.get_swaps),
        ]
        self.message_triggers = {}

        now = datetime.now()
        day = now.replace(day=now.day + 1, hour=0, minute=0, second=0, microsecond=0)
        self.logTimer = Timer( (day - now).seconds, self.live_log)
        self.logTimer.start()

    def run(self):
        while True:
            self.loop()

    # check comments for triggers
    def check_comments(self, subreddit):
        logging.debug('checking latest comments on {0}'.format(subreddit))
        comments = self.reddit.get_comments(subreddit)
        for comment in comments:
            if not Comment.is_parsed(comment.id, self.db):
                post = Post(comment)
                for regex, process in self.comment_triggers:
                    if(regex.search(post.text)): process(self, post)
                self.reply(post)
                Comment.add(comment.id, self.db)

    # check submissions for triggers
    def check_submissions(self, subreddit):
        logging.debug('checking latest submissions on {0}'.format(subreddit))
        submissions = self.reddit.get_subreddit(subreddit).get_new(limit=100)
        for submission in submissions:
            if not Submission.is_parsed(submission.id, self.db):
                post = Post(submission)
                for regex, process in self.submission_triggers:
                    if regex.search(post.text): process(self, post)
                self.reply(post)
                Submission.add(submission.id, self.db)

    # check messages for triggers
    def check_messages(self):
        pass

    # sent the owner a message each week with some statistics
    def live_log(self):
        msg  = 'Swaps added: {added}  \n'.format(added=CountDecorator.getCount(self.addSwap))
        msg += 'Swaps listed: {listed}  \n'.format(added=CountDecorator.getCount(self.getSwap))
        msg += 'Inventories listed: {inv}  \n'.format(added=CountDecorator.getCount(self.getInventory))
        self.reddit.send_message(self.owner, 'SwapBot Log', msg)
        now = datetime.now()
        day = now.replace(day=now.day + 1, hour=0, minute=0, second=0, microsecond=0)
        self.logTimer = Timer( (day - now).seconds, self.live_log)
        self.logTimer.start()

    @CountDecorator
    def get_inventory(self, post):
        url = Inventory.get(str(post.author), self.db)
        if not url:
            logging.debug('get_inv: no inv in db')
            url = self.get_inventory_link(post.author)
        if not url:
            text = "No inventory found. :("
        else:
            text = '[{user}\'s Inventory]({permalink})'.format(user=str(post.author), permalink=url)
        self.build_reply(text)

    @CountDecorator
    def get_swaps(self, post):
        swaps = Swap.get(str(post.author), self.db)
        if swaps:
            self.build_reply(len(swaps) + ' swaps')
        else:
            logging.debug('get_swap: no swaps')

    @CountDecorator
    def add_swap(self, post):
        logging.debug('add_swap')
        self.build_reply('Dummy added this submission to swap db')

    def get_inventory_link(self, user):
        logging.info('Getting link to {}\'s inventory'.format(str(user)))
        posts = user.get_submitted(limit=None)
        for post in posts:
            if post.subreddit.display_name.lower() == 'whiskyinventory':
                return post.permalink
        return None

if __name__ == "__main__":
    with sqlite3.connect('bot.db') as db:
        Swap.createTable(db)
        Inventory.createTable(db)
        bot = SwapBot(name='SwapBot by /u/FlockOnFire and /u/DustlessWalnut', log_file='review.log', from_file='login.cred', database=db)
        bot.run()
