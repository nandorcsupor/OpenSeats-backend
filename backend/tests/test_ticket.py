import pytest
from brownie import accounts, Ticket, reverts

def test_ticket_resale_limit(ticket_contract):
    # Use pre-defined accounts
    account_a = accounts[1]
    account_b = accounts[2]
    account_c = accounts[3]

    # Mint a ticket using Account A
    ticket_contract.mintTicket(
        account_a,
        # Fill in the required parameters for the mintTicket function
        {"from": account_a, "value": appropriate_value}
    )

    # Get the minted ticket ID
    ticket_id = 1  # Assumes that this is the first ticket minted

    # Approve the ticket transfer
    ticket_contract.approve(account_b, ticket_id, {"from": account_a})

    # Resell the ticket from Account A to Account B
    ticket_contract.transferFrom(
        account_a,
        account_b,
        ticket_id,
        {"from": account_b, "value": appropriate_resale_value}
    )

    # Approve the ticket transfer from Account B
    ticket_contract.approve(account_c, ticket_id, {"from": account_b})

    # Attempt to resell the ticket from Account B to Account C and expect it to fail
    with reverts("Ticket can only be resold once"):
        ticket_contract.transferFrom(
            account_b,
            account_c,
            ticket_id,
            {"from": account_c, "value": appropriate_resale_value}
        )


@pytest.fixture(scope="module")
def ticket_contract():
    return deploy_ticket()

