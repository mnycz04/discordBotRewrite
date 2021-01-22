"""
Handles all interfacing with the praw API.
"""

import praw

r = praw.Reddit(client_id='X0VJq7wE00FEYQ',
                client_secret='oQ09GcBauKxPxN2su0o18Xb_EqC6vw',
                user_agent='windows:mnycz04.discord:v1.5.3 (by /u/mnycz04; mnycz04@gmail.com)')


async def get_reddit_post(subreddit):
    """
    Gets a random submission in a given subreddit
    :param subreddit: The subreddit's name to search for
    :returns object: Returns a post object.
    """
    subs = r.subreddits.search_by_name(subreddit)
    if not subs:
        raise LookupError
    else:
        pass

    post = subs[0].random()
    if post is None:
        raise ConnectionRefusedError
    else:
        return post

