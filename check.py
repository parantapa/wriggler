"""  
Module for checking twitter.py
"""
import twitter

def main():

    """
    Main for checking the various calls
    """
    #Tokens for authentication
    client_key = ''
    client_secret = ''
    resource_owner_key = ''
    resource_owner_secret = ''
    user_id = '10778222'
    token = {
        "client_key": client_key, 
        "client_secret": client_secret,
        "resource_owner_key": resource_owner_key, 
        "resource_owner_secret": resource_owner_secret
    } 
    #testing user_show
    user = []
    user.append(user_id)
    #user.append(user_id2)
    content = twitter.users_show(user_id, token)

    fp3 = open("out3.txt", "w")
    fp3.write(str(content))
    fp3.close()
    #testing user_timeline
    content = twitter.user_timeline(user_id, token)

    fp1 = open("out1.txt", "w")
    for i in content:
        fp1.write(str(i))
    fp1.close()
    #testing user_lookup
    content = twitter.users_lookup(user, token )
    fp2 = open("out2.txt", "w")
    for i in content:
        fp2.write(str(i))
    fp2.close()
    
   
if __name__ == "__main__":
    main()

