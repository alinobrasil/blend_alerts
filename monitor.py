from telegram import Bot
import sqlite3
import time
import os
from dotenv import load_dotenv
from thegraph import get_lien_info
from pprint import pprint
from datetime import datetime

## set the wait time. eg 1 minute
wait_time = 1*60  

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)


def get_subscribed_addresses_from_db():
    conn = sqlite3.connect('labs.sqlite')
    cursor = conn.cursor()
    cursor.execute('SELECT userId, address FROM subscription')
    results = cursor.fetchall()
    conn.close()
    return [{'user_id': row[0], 'address': row[1]} for row in results]


def send_telegram_alert(user_id, lien):

    auctionStartTime =int(lien['auctionStarted'])
    
    loan_details=""
    if len(lien['loans']) > 0:
        loanAmount = int(lien['loans'][0]['loanAmount'])/10**18
        loan_details=f"\n\
            \nLoan amount: {loanAmount:.2f} ETH\
            \nInterest rate: {int(lien['loans'][0]['rate'])/100}%\
            \nLender: {lien['loans'][0]['lender']}"

    bot.send_message(
        chat_id=user_id, 
        text=f"WARNING!!!! A new auction was started for the collateral from your account {lien['borrower']} \
            \nGo make sure your collateral is safe or it may get seized in 30 hours! \
            \n\nHere's more info on your loan on blur:\
            \nCollection address: {lien['collection']}\
            \nToken ID: {lien['tokenId']}  \
            \n{loan_details} \
            \nAuction started: {datetime.fromtimestamp(auctionStartTime)}            "
    )





def alert_service():
    while True:
        print("checking for alerts... ", datetime.now())
        # list of users & addresses they subscribed to
        subscribed_addresses = get_subscribed_addresses_from_db()
        # print("subscribed addresses: ")
        # print(subscribed_addresses)

        # get liens whose auctoin has been started
        ##should be able to pass in the wait_time here, to get it passed into the graphql query
        liens = get_lien_info() 

        # print("last 3 liens from past hour")
        # pprint(liens[-3:])

        for lien in liens:
            # if there's a match in our subscription list, send them alert
            for user in subscribed_addresses:
                if lien['borrower'] == user['address']:
                    print("\n***** Found match: ", lien['borrower'])
                    send_telegram_alert(user['user_id'], lien)
                # end if
            # end loop
        # end for loop

        time.sleep(wait_time)


if __name__ == '__main__':
    print("running bot...")
    alert_service()
