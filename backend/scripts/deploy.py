from brownie import Ticket, accounts
from scripts.scripts import get_account

# token_uri = "https://ipfs.io/ipfs/QmVBwKkVxeDLu6jB2A714rcD7b827Uc1JVYkLafTnrd8sp?filename=karl.json"
token_uri = "https://ipfs.io/ipfs/QmTTYmrKH3p7d2NpRpZvmPb5h5dcT6VXmdpvQ5o76aenTT?filename=lfc.json"
OPENSEA_URL = "https://testnets.opensea.io/assets/{}/{}"

def main():
    account = get_account()
    ticket = Ticket.deploy({'from': account})
    print(f"FootballTicket deployed at address: {ticket.address}")