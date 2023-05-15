from brownie import Ticket, accounts, config, network
from web3 import Web3
from logging import Logger

logger = Logger(name='loggerke')

def test_ticket_resale_limit():
    # Deploy the Ticket contract
    # TODO - Make tokenId 
    ticket_contract = Ticket.deploy(
        config["networks"][network.show_active()]["eth_usd_price_feed"],
        10000,
        "Ticket",
        "TK",
        (
            ["Gate A", "Gate B", "Gate C", "Gate D"],
            ["Section A", "Section B", "Section C", "Section D"],
            [10, 10, 10, 10],
            [100, 100, 100, 100],
            [4, 3, 2, 1]
        ),
        {"from": accounts[0]}
    )

    # Create 3 accounts
    accounts_list = accounts[0:3]
    eth_usd_price = ticket_contract.getETHUSDPrice.call()
    # eth_usd_price = Web3.fromWei(eth_usd_price, 'ether')
    
    # Mint a ticket from the first account
    ticket_contract.mintTicket(
        accounts_list[0],
        "Gate A",
        "Section A",
        5,
        69,
        2,
        "https://ipfs.io/ipfs/QmTH4yaeK5YrPADLmZQm3ne4GVb24HD42gNggKhRX6xBe6?filename=lfc.json",
        {"from": accounts_list[0], "value": eth_usd_price}  # Adjust the value based on the actual price
    )
    
    # Approve account
    approve(ticket_contract, accounts_list[0], accounts_list[1], 1)

    # Resell the ticket from the first account to the second account
    tx = ticket_contract.transferFrom(accounts_list[0], accounts_list[1], 1)
    tx.wait(1)
    
    # Try reselling again - should fail
    try:
        ticket_contract.transferFrom(ticket_contract.ownerOf(1), accounts_list[2], 1, {"from": ticket_contract.ownerOf(1)})
        assert False, "Resale should have failed"
    except Exception as e:
        assert "Ticket can only be resold once" in str(e)
    
    # Check if the resale flag is set for the ticket
    ticket_data = ticket_contract.tickets(1)
    assert ticket_data['isResold'] == True

def get_approved(contract, token_id: int) -> list:
    # Get list of approved accounts for a specific tokenId
    approved_addresses = contract.getApproved(token_id)
    return approved_addresses

def approve(contract, _from, _to, token_id) -> None:
    # Approve an account to hold that NFT
    return contract.approve(_to, token_id, {'from': _from})
    


