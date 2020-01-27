import module.util.got as got
import copy

'''
username (str): An optional specific username from a twitter account. Without "@".
start_date (str. "yyyy-mm-dd"): A lower bound date to restrict search.
end_date (str. "yyyy-mm-dd"): An upper bound date to restrict search.
query (str): A query text to be matched.
max_number_of_tweets (int): The maximum number of tweets to be retrieved. If this number is unsetted or lower than 1 all
'''
def get_tweets(username, start_date, end_date, query, max_number_of_tweets):

    tweet_criteria = got.manager.TweetCriteria()

    if username:
        tweet_criteria.setUsername(username)

    if start_date:
        tweet_criteria.setSince(start_date)

    if end_date:
        tweet_criteria.setUntil(end_date)

    if query:
        tweet_criteria.setQuerySearch(query)

    if max_number_of_tweets:
        tweet_criteria.setMaxTweets(max_number_of_tweets)

    tweets = got.manager.TweetManager.getTweets(tweet_criteria)

    result = []

    for t in tweets:
        result.append({'metadata': {'id': t.id,
                                    'permalink': t.permalink,
                                    'date': str(t.date),
                                    'username': t.username,
                                    'retweets': t.retweets,
                                    'favorites': t.favorites,
                                    'mentions': t.mentions,
                                    'hashtags': t.hashtags,
                                    'geo': t.geo},
                       'text': t.text})

    return result
