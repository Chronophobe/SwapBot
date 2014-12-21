import praw
from datetime import date

class Post():
    def __init__(self, post):
        self.post   = post
        self.author = post.author
        self.url    = post.permalink
        self.date   = date.fromtimestamp(post.created_utc).strftime('%Y%m%d')
        
        if isinstance(self.post, praw.objects.Comment):
            self.text  = post.body
            self.reply = post.reply
        elif isinstance(self.post, praw.objects.Submission):
            self.text  = post.selftext
            self.reply = post.add_comment
