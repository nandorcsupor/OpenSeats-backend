from shutil import rmtree

from brownie import Ticket, accounts, FirstBuyer, SecondBuyer
from .scripts import get_account

# token_uri = "https://ipfs.io/ipfs/QmVBwKkVxeDLu6jB2A714rcD7b827Uc1JVYkLafTnrd8sp?filename=karl.json"
token_uri = "https://ipfs.io/ipfs/QmTTYmrKH3p7d2NpRpZvmPb5h5dcT6VXmdpvQ5o76aenTT?filename=lfc.json"
OPENSEA_URL = "https://testnets.opensea.io/assets/{}/{}"

def deploy_ticket():
    account = get_account()
    max_tickets = 10000
    ticket_prices = [100, 75, 65, 50]  # In USD
    gate_names = ["Gate A", "Gate B", "Gate C", "Gate D"]

    ticket_contract = Ticket.deploy(
        max_tickets,
        ticket_prices,
        gate_names,
        {"from": account}
    )

    print(f"FootballTicket deployed at address: {ticket_contract.address}")

    gates = ["Gate A", "Gate B", "Gate C", "Gate D"]
    sections = ["Section A", "Section B", "Section C"]
    numberOfRowsPerSection = [10, 10, 10]
    numberOfSeatsPerRow = [100, 100, 100]
    pricesPerSection = [100, 75, 65]  # In USD

    message = "MY MESSAGE ASD"
    ticket_contract.emitSomething(
        message,
        {"from": account}
    )
    '''
    ticket_contract.setTicketAvailability(
        gates,
        sections,
        numberOfRowsPerSection,
        numberOfSeatsPerRow,
        pricesPerSection,
        {"from": account, 'allow_revert':True, "gas_limit": 10000000}
    )
    '''
    print(f"SetTicketAvailability finished!")


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