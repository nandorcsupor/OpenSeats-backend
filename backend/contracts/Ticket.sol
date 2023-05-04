// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract Ticket is ERC721URIStorage {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIdCounter;

    uint256 private constant MAX_TICKETS = 10000;
    uint256[4] private ticketPrices = [100, 75, 65, 50]; // In USD

    struct TicketData {
        string seatingInfo;
        string gate;
        uint256 price;
        bool isResold;
    }

    mapping(uint256 => TicketData) public tickets;

    AggregatorV3Interface internal priceFeed;

    constructor() ERC721("Ticket", "TK") {
        // Set the address of the Chainlink ETH/USD price feed (on Sepolia testnet)
        priceFeed = AggregatorV3Interface(
            0x694AA1769357215DE4FAC081bf1f309aDC325306
        );
    }

    function mintTicket(
        address to,
        string memory seatingInfo,
        string memory gate,
        uint8 category,
        string memory tokenURI_
    ) public payable {
        require(category >= 1 && category <= 4, "Invalid category");
        require(_tokenIdCounter.current() < MAX_TICKETS, "Max tickets reached");

        // Calculate the price in ETH using the current ETH/USD price
        uint256 priceInETH = (ticketPrices[category - 1] * 1e18) /
            getETHUSDPrice();

        require(msg.value >= priceInETH, "Not enough ETH sent");

        _tokenIdCounter.increment();
        uint256 tokenId = _tokenIdCounter.current();

        tickets[tokenId] = TicketData(seatingInfo, gate, priceInETH, false);

        _safeMint(to, tokenId);
        _setTokenURI(tokenId, tokenURI_);
    }

    function getETHUSDPrice() public view returns (uint256) {
        (, int256 price, , , ) = priceFeed.latestRoundData();
        return uint256(price);
    }

    function tokenURI(
        uint256 tokenId
    ) public view virtual override returns (string memory) {
        return ERC721URIStorage.tokenURI(tokenId);
    }

    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 tokenId
    ) internal virtual override {
        super._beforeTokenTransfer(from, to, tokenId);

        // Check if this is a resale attempt
        if (from != address(0)) {
            TicketData storage ticket = tickets[tokenId];
            require(!ticket.isResold, "Ticket can only be resold once");

            uint256 maxResalePrice = ticket.price + ((ticket.price * 5) / 100);
            require(
                msg.value >= maxResalePrice,
                "Resale price is too high (> 5%)"
            );

            ticket.isResold = true;
        }
    }
}
