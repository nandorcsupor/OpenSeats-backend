from brownie import Ticket, config, network
from .scripts import get_account
from datetime import datetime

token_uri = "https://ipfs.io/ipfs/QmTH4yaeK5YrPADLmZQm3ne4GVb24HD42gNggKhRX6xBe6?filename=lfc.json"
OPENSEA_URL = "https://testnets.opensea.io/assets/{}/{}"

def deploy_match(max_tickets: int, token_name: str, token_symbol: str, venue_config: tuple, date: int ) -> str:
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


def convert_to_timestamp(date_string):
    date_obj = datetime.strptime(date_string, "%d/%m/%Y")
    timestamp = int(date_obj.timestamp())
    return timestamp