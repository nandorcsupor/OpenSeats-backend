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



# To RUN API
    - docker-compose up

