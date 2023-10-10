from telegram import Bot
from telegram.ext import Updater, CommandHandler
from pprint import pprint
import sqlite3
from thegraph import get_lien_info
from datetime import datetime
import time
import os
from dotenv import load_dotenv

load_dotenv()


TOKEN = os.getenv("BOT_TOKEN")
HELP_TEXT = """
Here are the commands you can use with this bot:

/past_hour
    -see all auctions started in the past hour

/subsribe <borrower address>
    -subscribe to liquidation alerts for your wallet address. You'll be notified as soon as an auction is started on your collateral.
    eg:
    /subscribe 0x1234567890abcdef1234567890abcdef1234567

/help - show this help text

"""


def start(update, context):
    """Send a message when the command /start is issued and print user details."""
    chat_id = update.message.chat.id
    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    # Some users may not have a last name set.
    last_name = update.message.from_user.last_name or ''
    username = update.message.from_user.username
    display_name = f"{first_name} {last_name}"

    user_info = (
        f"Chat ID: {chat_id}\n"
        f"User ID: {user_id}\n"
        f"Display Name: {display_name}\n"
        f"Username: @{username}\n"
    )

    conn = sqlite3.connect('labs.sqlite')
    cursor = conn.cursor()

    # Check if user already exists in the database
    cursor.execute('SELECT userId FROM users WHERE userId = ?', (user_id,))
    if cursor.fetchone() is None:
        cursor.execute('INSERT INTO users (userId, displayname, handle) VALUES (?, ?, ?)',
                       (user_id, display_name, username))
        conn.commit()

    update.message.reply_text(f'Hello {first_name}!\n\n{HELP_TEXT}')

def help(update, context):
    """help text to guide user on how to use the bot"""
    update.message.reply_text(HELP_TEXT)




def send_chunks(update, data, chunk_size=5):
    for i in range(0, len(data), chunk_size):
        chunk = [str(item) for item in data[i:i+chunk_size]]
        update.message.reply_text("\n\n".join(chunk))
        time.sleep(1)


def format_liens(liens):

    output_list = []

    for lien in liens:

        # pprint(lien['loans'])

        # show lien info
        auction_start_time = ''
        if lien['auctionStarted'] is not None:
            auction_start_time = lien['auctionStarted']
            auction_start_time = datetime.fromtimestamp(
                int(auction_start_time))

            output = f"\n\
Auction started: {auction_start_time} \n\
lien Started:  {datetime.fromtimestamp(int(lien['timeStarted'])) } \n\
Collection: {lien['collection']})  \n\
tokenId: {lien['tokenId']} \n\
Borrower: {lien['borrower']}"

            # add loan details (if available)
            loans = lien['loans']
            if len(loans) > 0:
                loan = lien['loans'][0]
                rate = int(loan['rate'])/100
                loanAmount = int(loan['loanAmount']) / (10**18)
                startTime = datetime.fromtimestamp(int(loan['startTime']))
                output += f"\nloan info: {loanAmount:.2f} ETH loan at {rate}% APR from {loan['lender']} "

            output_list.append(output)

        loans = lien['loans']
        loans = sorted(loans, key=lambda x: x['startTime'])

        # display underlying loan info
        # if len(loans) > 0:
        #     # loan info
        #     for loan in loans:
        #         rate = int(loan['rate'])/100
        #         loanAmount = int(loan['loanAmount']) / (10**18)
        #         startTime = datetime.fromtimestamp(int(loan['startTime']))
        #         print(
        #             f"{startTime} | apr: {rate}%  loan: {loanAmount:.2f}   lender: {loan['lender']}")
    # end loop

    return output_list


def past_hour(update, context):
    """See all auctions started in the past hour"""
    update.message.reply_text(
        "Here are the auctions that were started in the past hour:")
    liens = get_lien_info()
    liens = format_liens(liens)
    send_chunks(update, liens)

    print("PAST_HOUR data sent to: ", update.message.from_user.id)


def add_subscription(userId, address):

    try:
        conn = sqlite3.connect('labs.sqlite')
        cursor = conn.cursor()

        cursor.execute('''
        INSERT INTO subscription (userId, address) VALUES (?, ?)
        ''', (userId, address))
        conn.commit()

        return True

    except sqlite3.IntegrityError:
        # This block will not usually be executed since we're using INSERT OR IGNORE
        print("Record already exists.")
        return False


def subscribe(update, context):
    """Subscribe to startAuction alerts from a specified address"""
    userId = update.message.from_user.id
    first_name = update.message.from_user.first_name
    last_name = update.message.from_user.last_name or ''
    display_name = f"{first_name} {last_name}"

    print(f"New subscription by {display_name}: ", userId)

    # print(update.message)
    command_args = update.message.text.split()
    if len(command_args) > 1:
        address = " ".join(command_args[1:])
        print(address)

        # add address to database. will receive
        result = add_subscription(userId, address)
        print(result)

        if result:
            update.message.reply_text(
                f"Subscribed to alerts for {address}.")
        else:
            update.message.reply_text(
                f"You are already subscribed to alerts for {address}.")

    else:
        update.message.reply_text(
            "Please provide an address that you want to monitor.")


def main():
    print("Running telegram bot...")

    updater = Updater(TOKEN)

    dp = updater.dispatcher

    # Register the command handler
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("subscribe", subscribe))
    dp.add_handler(CommandHandler("past_hour", past_hour))

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
