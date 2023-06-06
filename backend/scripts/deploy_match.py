from brownie import Ticket, config, network
from .scripts import get_account
from datetime import datetime

token_uri = "https://ipfs.io/ipfs/QmTH4yaeK5YrPADLmZQm3ne4GVb24HD42gNggKhRX6xBe6?filename=lfc.json"
OPENSEA_URL = "https://testnets.opensea.io/assets/{}/{}"

def deploy_match(max_tickets: int, token_name: str, token_symbol: str, venue_config: tuple, date: int ) -> str:
    # For now - everything is bought with this account - later use the user's own account
    account = get_account()
    
    ticket_contract = Ticket.deploy(
        config["networks"][network.show_active()]["eth_usd_price_feed"],
        max_tickets,
        token_name,
        token_symbol,
        venue_config,
        date,
        {"from": account}
    )

    ticket_address = ticket_contract.address
    print(f"FootballTicket deployed at address: {ticket_address}")

    return ticket_address


def get_eth_usd_price(ticket_contract_address):
    ticket_contract = Ticket.at(ticket_contract_address)
    eth_usd_price = ticket_contract.getETHUSDPrice.call()
    return eth_usd_price


def mint_ticket(ticket_contract_address, gate: str, section: str, row: int, seat: int, category:int):
    # For now - everything is bought with this account - later use the user's own account
    account = get_account()

    # ISSUE HERE - SOMEHOW NEED THE CONTRACT INSTANCE ITSELF!!!
    eth_usd_price = get_eth_usd_price(ticket_contract_address)

    ticket_contract = Ticket.at(ticket_contract_address)
    ticket_receipt = ticket_contract.mintTicket(
        account,
        gate,
        section,
        row,
        seat,
        category,
        "https://ipfs.io/ipfs/QmTH4yaeK5YrPADLmZQm3ne4GVb24HD42gNggKhRX6xBe6?filename=lfc.json",
        {"from": account, "value": eth_usd_price}
    )

    ticket_events = ticket_receipt.events

    transaction_hash_str = str(ticket_receipt)

    start_index = transaction_hash_str.find("0;m") + len("0;m")
    end_index = transaction_hash_str.find("\\", start_index)

    transaction_hash = transaction_hash_str[start_index:end_index]
    transaction_hash = transaction_hash.split('\\')[0]
    transaction_hash = str(transaction_hash)

    print('TRANSACTION HASH >>>>>>>>>>>>>>>>,', transaction_hash)

    # Extract the required fields and store them in a dictionary
    extracted_info = {
        'token_id': ticket_events['Transfer'][0]['tokenId'],
        'transaction_hash': transaction_hash
    }
    print('Extraced info:', extracted_info)

    return extracted_info


def convert_to_timestamp(date_string):
    date_obj = datetime.strptime(date_string, "%d/%m/%Y")
    timestamp = int(date_obj.timestamp())
    return timestamp