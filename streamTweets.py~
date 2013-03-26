"""
Module for checking twitter.py
"""
import twitter
def main():
    """
    Testing public_stream()
    The method collects 1000 tweets from the public stream and then closes the connection
    """
    #Tokens for authentication
    client_key = ''
    client_secret = ''
    resource_owner_key = ''
    resource_owner_secret = ''
    token = {
          "client_key": client_key, 
          "client_secret": client_secret,
          "resource_owner_key": resource_owner_key, 
          "resource_owner_secret": resource_owner_secret
           } 
    i = 0
    tweets = twitter.public_stream(token)
    fp1 = open("Streamtweets.txt","w")
    while True:
        for tweet in tweets:
            print "writing"
            fp1.write(tweet)
            fp1.write("\n\n")
            i = i + 1
            if i == 1000: 
                break
        if i == 1000:
            break
    fp1.close()
    print "Exiting!!!"
    raise SystemExit()

if __name__ == "__main__":
    main()

        
