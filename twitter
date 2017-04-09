import sys
import os
import tweepy
import twittertoken as tt

auth = tweepy.AppAuthHandler(tt.Consumer_Key, tt.Consumer_Secret)

api = tweepy.API(auth, wait_on_rate_limit=True,
				   wait_on_rate_limit_notify=True)

if (not api):
	print ("Can't Authenticate")
	sys.exit(-1)
searchQuery = '공유'  # this is what we're searching for
maxTweets = 10000000 # Some arbitrary large number
tweetsPerQry = 100  # this is the max the API permits
fName = 'tweets.txt' # We'll store the tweets in a text file.

sinceId = None

max_id = -1

tweetCount = 0
print("Downloading max {0} tweets".format(maxTweets))
def unicode_normalize(text):
	return text.translate({ 0x2018:0x27, 0x2019:0x27, 0x201C:0x22, 0x201D:0x22,
							0xa0:0x20 })
with open(fName, 'w',encoding='utf8') as f:
	while tweetCount < maxTweets:
		try:
			if (max_id <= 0):
				if (not sinceId):
					new_tweets = api.search(q=searchQuery, count=tweetsPerQry)
				else:
					new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
											since_id=sinceId)
			else:
				if (not sinceId):
					new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
											max_id=str(max_id - 1))
				else:
					new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
											max_id=str(max_id - 1),
											since_id=sinceId)
			if not new_tweets:
				print("No more tweets found")
				break
			for tweet in new_tweets:
				print(tweet)
				json = tweet._json['text']
				f.write(json+'\n')
			tweetCount += len(new_tweets)
			print("Downloaded {0} tweets".format(tweetCount))
			max_id = new_tweets[-1].id
		except tweepy.TweepError as e:
			print("some error : " + str(e))
			break

print ("Downloaded {0} tweets, Saved to {1}".format(tweetCount, fName))
