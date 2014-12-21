import praw

class Post():
    def __init__(self, post):
        self.post   = post
        self.author = post.author
        self.url    = post.permalink
        
        if isinstance(self.post, praw.objects.Comment):
            self.text  = post.body
            self.reply = post.reply
        elif isinstance(self.post, praw.objects.Submission):
            self.text  = post.selftext
            self.reply = post.add_comment
