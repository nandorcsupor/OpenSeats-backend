from brownie import Ticket, accounts

def test_ticket_resale_limit():
    # Deploy the Ticket contract
    ticket_contract = Ticket.deploy(
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

    # Mint a ticket from the first account
    ticket_contract.mintTicket(
        accounts_list[0],
        "Gate A",
        "Section A",
        5,
        69,
        2,
        "https://ipfs.io/ipfs/QmTH4yaeK5YrPADLmZQm3ne4GVb24HD42gNggKhRX6xBe6?filename=lfc.json",
        {"from": accounts_list[0]}  # Adjust the value based on the actual price
    )

    # Resell the ticket from the first account to the second account
    ticket_contract.transferFrom(accounts_list[0], accounts_list[1], 1, {"from": accounts_list[0]})  # Adjust the value based on the actual resale price

    # Attempt to resell the ticket again from the second account
    try:
        ticket_contract.transferFrom(accounts_list[1], accounts_list[2], 1, {"from": accounts_list[1]})  # Adjust the value based on the actual resale price
        assert False, "Resale should have failed"
    except Exception as e:
        assert "Ticket can only be resold once" in str(e)

    # Check if the resale flag is set for the ticket
    ticket_data = ticket_contract.tickets(1)
    assert ticket_data['isResold'] == True


