from brownie import Ticket, accounts, FirstBuyer, SecondBuyer, config, network
from .scripts import get_account

# token_uri = "https://ipfs.io/ipfs/QmVBwKkVxeDLu6jB2A714rcD7b827Uc1JVYkLafTnrd8sp?filename=karl.json"
token_uri = "https://ipfs.io/ipfs/QmTH4yaeK5YrPADLmZQm3ne4GVb24HD42gNggKhRX6xBe6?filename=lfc.json"
OPENSEA_URL = "https://testnets.opensea.io/assets/{}/{}"

def deploy_ticket():
    account = get_account()
    max_tickets = 10000
    tokenName = "Ticket"
    tokenSymbol = "TK"
    address = account.address
    gate = "Gate A"
    section = "Section A"
    row = 5
    seat = 69
    category = 2

    venue_config = (
        ["Gate A", "Gate B", "Gate C", "Gate D"],
        ["Section A", "Section B", "Section C", "Section D"],
        [10, 10, 10, 10],
        [100, 100, 100, 100],
        [4, 3, 2, 1]  # In USD
    )

    date_timestamp = 1717350459

    ticket_contract = Ticket.deploy(
        config["networks"][network.show_active()]["eth_usd_price_feed"],
        max_tickets,
        tokenName,
        tokenSymbol,
        venue_config,
        date_timestamp,
        {"from": account}
    )

    print(f"FootballTicket deployed at address: {ticket_contract.address}")

    # Calculate the price in ETH using the current ETH/USD price
    price_in_usd = venue_config[4][category - 1]
    eth_usd_price = ticket_contract.getETHUSDPrice.call()
    price_in_eth = (price_in_usd * 1e18) // eth_usd_price

    ticket_contract.mintTicket(
        address,
        gate,
        section,
        row,
        seat,
        category,
        token_uri,
        {"from": account, "value": price_in_eth}
    )

    # Check if the ticket was minted successfully
    ticket_id = 1  # Assumes that this is the first ticket minted
    ticket_data = ticket_contract.tickets(ticket_id)
    print('TICKET DATA:', ticket_data)
    print('Counter:', ticket_contract._tokenIdCounter())
    print(f"View your NFT at {OPENSEA_URL.format(ticket_contract.address, ticket_contract._tokenIdCounter() -1)}")

    return ticket_contract


# TODO - Generate a new JSON file - with attributes full of seating info and auto upload it to IPFS ?
# TODO - Maybe Generate a QR code with the seating info instead ? This way we could make sure that
# TODO - admission to a match is sorted. - or maybe generate that on the frontend ?
# TODO - or we can check the holders and maybe use that during admission somehow ? - Some built in
# TODO - Function in a wallet - 
# TODO - LOOK 

def deploy_buyers():
    account = get_account()
    # Deploy and fund first test customer
    first_buyer = FirstBuyer.deploy({'from': account})
    tx = first_buyer.fund({"from": account, "value": 100000000000000000})  #0.1 ETH
    tx.wait(1)
    # Deploy and fund second test customer
    second_buyer = SecondBuyer.deploy({'from': account})
    tx = second_buyer.fund({"from": account, "value": 100000000000000000})  #0.1 ETH
    tx.wait(1)
    print(f'Buyers:{first_buyer.address}, {second_buyer.address}')

    # Self-destruct both
    tx = first_buyer.end({"from": account})
    tx.wait(1)
    tx = second_buyer.end({"from": account})
    tx.wait(1)

def main():
    deploy_ticket()
    # deploy_buyers()