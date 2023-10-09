import requests
import time
from pprint import pprint
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


def short_address(address):
    if not isinstance(address, str):
        raise ValueError("Expected a string Ethereum address")

    if len(address) < 8:
        raise ValueError("Address is too short")

    return address[:4] + "..." + address[-4:]


def get_lien_info(hours=1):

    # get records from past x hours (default 1 hour)
    current_timestamp = int(time.time())
    time_filter = current_timestamp - (hours * 60 * 60)


# grpahql query: get liens whose auction started recently according to time_filter
# only get the most recent loan on each lien
    graphql_query = f"""
    {{
      liens(where: {{auctionStarted_gt: {time_filter}}}, orderBy: auctionStarted) {{
        auctionStarted
        collection
        borrower
        tokenId
        timeStarted
        loans(first: 1, orderBy: startTime, orderDirection: desc) {{
          lender
          startTime
          loanAmount
          rate
        }}
      }}
    }}
    """

    # url="https://api.studio.thegraph.com/query/53192/blend/0.0.28"  ## v26 doesnt exist no more
    url = os.getenv("GRAPH_API")

    response = requests.post(url=url, json={"query": graphql_query})

    # pprint(response.json())

    liens = response.json()['data']['liens']

    return liens


if __name__ == '__main__':
    get_lien_info()


# ##graphql query:
# ## get liens whose auction has started recently according to time filter
# # ## . get ALL loans under each lien
#     graphql_query = f"""
#   {{
#     liens(
#       where: {{ auctionStarted_gt: {time_filter}}}
#       orderBy: auctionStarted
#     )
#     {{
#       auctionStarted
#       collection
#       borrower
#       tokenId
#       timeStarted
#           loans {{
#         lender
#         startTime
#         loanAmount
#         rate
#       }}
#     }}
#   }}
#   """
