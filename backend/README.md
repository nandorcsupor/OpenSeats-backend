# OpenSeats
where true fans get their tickets![facebook_profile_image](https://user-images.githubusercontent.com/79459355/235314704-4431ddaf-066c-494e-8e58-d79da18bc951.png)


# Run test
- We use `mainnet-fork` network to test locally
    - because we need the pricefeed when testing the smart contract
    so we fork mainnet then deploy our own V3Aggregator.

- To add it to your local networks run this command:
`brownie networks add development mainnet-fork cmd=ganache-cli host=http://127.0.0.1 fork=https://eth-mainnet.g.alchemy.com/v2/QT-UxbxTXnvcZKt0WbOgFb5BHhUJRl5N accounts=10 mnemonic=brownie port=8545`

- To run
brownie test --network mainnet-fork

# Run on Seplia
- brownie run scripts/deploy.py --network sepolia

# Run Server
- brownie run scripts/api.py --network sepolia



# TODO - 
    - Now the venue config is hard-coded so no matter what the frontend passes in - fix that
    - Everything is running locally - deploy somewhere
        - Currently using a local postgresql database.

    - Update the fetching of available matches - use a new method - currently we do an api call every second.


# TODO NOW
    - Buy NFT - endpoint + FE - DONE
        - Add notification - DONE
    - Add "How it works" section to first page. - IN PROGRESS LATER
    - Bind NFT - Solidity contract change + endpoint  + FE - DONE



# Tables
ticket_nfts:
CREATE TABLE ticket_nfts (
    transaction_hash TEXT,
    gate TEXT,
    section TEXT,
    row TEXT,
    seat TEXT,
    category TEXT,
    token_id TEXT,
    email TEXT,
    full_name TEXT
);


# TODO - Add my tickets page which displays your tickets. currently just display all of them !
# TODO - Maybe when someone buys a ticket they would have to immediately BIND THEM at the same time ? 
    - Because this way scalpers would just sell their wallets to people - it would probably be harder - but still doable


# Icons
- are from flaticon

