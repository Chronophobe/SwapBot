from Bot import Bot, Comment, Submission
from Tables import Swap, Inventory
from Post import Post
from Decorators import CountDecorator
from threading import Timer
from datetime import datetime
import re
import sqlite3
import logging 
import praw

class SwapBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.owner     = 'FlockOnFire'
        self.keywords  = ['thank', 'thanks']
        self.swap_subs = ['scotchswap']

        name = '@SwapBot'
        self.comment_triggers = [
           #add
           (re.compile(r'{name} (archive|add|swap complete)'.format(name=name), re.I),
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
            (re.compile(r'{name} (archive|add|swap complete)'.format(name=name), re.I),
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
        # Add new swaps to database first
        self.get_user_swaps(post.author)

        # Then get swaps from database
        swaps = Swap.get(str(post.author), self.db)
        if swaps:
            i = 0
            msg = '{}\'s latest swaps:\n\n'.format(post.author)
            for title, url in swaps:
                if i > 9:
                    break
                msg += '* [{}]({})'.format(title, url)
                i += 1
            self.build_reply(msg)
        else:
            self.build_reply('{}\'s has no completed swaps yet.'.format(post.author))

    @CountDecorator
    def add_swap(self, post):
        if isinstance(post.original, praw.objects.Submission):
            sub = post
        else:
            sub = post.original.submission
        if post.author == sub.author:
            Swap.add(
                submission_id = sub.id,
                title = bytes(sub.title, 'utf-8'),
                user = str(sub.author).lower(),
                url = sub.url,
                date = sub.date,
                db = self.db
            )
            logging.info('Manually added Swap ({})'.format(sub.id))
            msg = 'Swap successfully archived!'
        else:
            msg  = 'Hey buddy, you can\'t archive other people their swaps.'
        self.build_reply(msg)

    def get_inventory_link(self, user):
        logging.info('Getting link to {}\'s inventory'.format(str(user)))
        posts = user.get_submitted(limit=None)
        for post in posts:
            if post.subreddit.display_name.lower() in self.swap_subs:
                return post.permalink
        return None

    def get_user_swaps(self, user):
        logging.info('Adding {}\'s swaps to the database.'.format(str(user)))
        posts = user.get_submitted(limit=None, sort = 'new')
        for post in posts:
            post = Post(post)
            if post.subreddit.display_name.lower() != 'scotchswap':
                break
            if Swap.find(post.id, self.db):
                break
            if any(word in self.keywords for word in post.title.lower().split()):
                Swap.add(
                    submission_id = post.id,
                    title = bytes(post.title, 'utf-8'),
                    user = str(post.author).lower(),
                    url = post.url,
                    date = post.date,
                    db = self.db
                )    
                logging.debug('Added Swap ({}) to database'.format(post.id))        

if __name__ == "__main__":
    with sqlite3.connect('bot.db') as db:
        Swap.createTable(db)
        Inventory.createTable(db)
        bot = SwapBot(name='SwapBot by /u/FlockOnFire and /u/DustlessWalnut', log_file='review.log', from_file='login.cred', database=db)
        bot.run()
