// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract Ticket is ERC721URIStorage {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIdCounter;

    struct SeatingInfo {
        string section;
        uint256 row;
        uint256 seat;
        bool isAvailable;
    }

    struct TicketData {
        SeatingInfo seatingInfo;
        string gate;
        uint256 price;
        bool isResold;
    }

    // keep track of available tickets
    mapping(bytes32 => SeatingInfo) public availableTickets;

    mapping(uint256 => TicketData) public tickets;

    AggregatorV3Interface internal priceFeed;

    uint256 public maxTickets;
    uint256[4] public ticketPrices;
    string[] public gateNames;

    // Event
    event TicketMinted(
        address indexed buyer,
        uint256 indexed tokenId,
        string gate,
        string section,
        uint256 row,
        uint256 seat
    );

    event TicketAvailabilityChanged(
        string gate,
        string section,
        uint256 row,
        uint256 seat,
        bool isAvailable
    );

    event requirementsPassed(string passed);

    constructor(
        uint256 _maxTickets,
        uint256[4] memory _ticketPrices,
        string[] memory _gateNames
    ) ERC721("Ticket", "TK") {
        // Set the address of the Chainlink ETH/USD price feed (on Sepolia testnet)
        priceFeed = AggregatorV3Interface(
            0x694AA1769357215DE4FAC081bf1f309aDC325306
        );

        maxTickets = _maxTickets;
        ticketPrices = _ticketPrices;
        gateNames = _gateNames;
    }

    function emitSomething(string memory message) public {
        emit requirementsPassed(message);
    }

    function setTicketAvailability(
        string[] memory gates,
        string[] memory sections,
        uint256[] memory numberOfRowsPerSection,
        uint256[] memory numberOfSeatsPerRow,
        uint256[] memory pricesPerSection
    ) public {
        // Emit event
        emit requirementsPassed("BEFORE PASSEDDDD!!!!!");
        require(gates.length > 0, "Gates cannot be empty");
        require(sections.length > 0, "Sections cannot be empty");
        require(
            numberOfRowsPerSection.length == sections.length,
            "Number of rows should be equal to the number of sections"
        );
        require(
            numberOfSeatsPerRow.length == numberOfRowsPerSection.length,
            "Number of seats should be equal to the number of rows"
        );
        require(
            pricesPerSection.length == sections.length,
            "Prices should be equal to the number of sections"
        );

        // Emit event
        emit requirementsPassed("passed");

        for (uint256 g = 0; g < gates.length; g++) {
            for (uint256 s = 0; s < sections.length; s++) {
                for (uint256 r = 1; r <= numberOfRowsPerSection[s]; r++) {
                    for (
                        uint256 seat = 1;
                        seat <= numberOfSeatsPerRow[r - 1];
                        seat++
                    ) {
                        bytes32 key = keccak256(
                            abi.encodePacked(gates[g], sections[s], r, seat)
                        );

                        availableTickets[key] = SeatingInfo(
                            sections[s],
                            r,
                            seat,
                            true
                        );

                        // Emit event
                        emit TicketAvailabilityChanged(
                            gates[g],
                            sections[s],
                            r,
                            seat,
                            true
                        );
                    }
                }
            }
        }
    }

    function mintTicket(
        address to,
        string memory seatingInfo,
        string memory gate,
        uint8 category,
        string memory tokenURI_
    ) public payable {
        require(category >= 1 && category <= 4, "Invalid category");
        require(_tokenIdCounter.current() < maxTickets, "Max tickets reached");

        // Check if the ticket with the given seating info is available
        bytes32 ticketKey = keccak256(abi.encodePacked(seatingInfo, gate));
        require(
            availableTickets[ticketKey].isAvailable,
            "Ticket not available"
        );

        // Parse seatingInfo
        (string memory section, uint256 row, uint256 seat) = parseSeatingInfo(
            seatingInfo
        );

        // Calculate the price in ETH using the current ETH/USD price
        uint256 priceInETH = (ticketPrices[category - 1] * 1e18) /
            getETHUSDPrice();

        require(msg.value >= priceInETH, "Not enough ETH sent");

        _tokenIdCounter.increment();
        uint256 tokenId = _tokenIdCounter.current();

        // Pass SeatingInfo struct to TicketData
        tickets[tokenId] = TicketData(
            SeatingInfo(section, row, seat, false),
            gate,
            priceInETH,
            false
        );

        // Decrease the availability of the ticket with the given seating info
        availableTickets[ticketKey].isAvailable = false;

        _safeMint(to, tokenId);
        _setTokenURI(tokenId, tokenURI_);

        // Emit event
        emit TicketMinted(to, tokenId, gate, section, row, seat);
    }

    function parseSeatingInfo(
        string memory seatingInfo
    ) internal pure returns (string memory section, uint256 row, uint256 seat) {
        bytes memory seatingInfoBytes = bytes(seatingInfo);
        uint256 delimiter1;
        uint256 delimiter2;
        for (uint256 i = 0; i < seatingInfoBytes.length; i++) {
            if (seatingInfoBytes[i] == "-") {
                if (delimiter1 == 0) {
                    delimiter1 = i;
                } else {
                    delimiter2 = i;
                    break;
                }
            }
        }

        bytes memory sectionBytes = new bytes(delimiter1);
        bytes memory rowBytes = new bytes(delimiter2 - delimiter1 - 1);
        bytes memory seatBytes = new bytes(
            seatingInfoBytes.length - delimiter2 - 1
        );

        for (uint256 i = 0; i < delimiter1; i++) {
            sectionBytes[i] = seatingInfoBytes[i];
        }
        for (uint256 i = delimiter1 + 1; i < delimiter2; i++) {
            rowBytes[i - (delimiter1 + 1)] = seatingInfoBytes[i];
        }
        for (uint256 i = delimiter2 + 1; i < seatingInfoBytes.length; i++) {
            seatBytes[i - (delimiter2 + 1)] = seatingInfoBytes[i];
        }

        section = string(sectionBytes);
        row = _bytesToUint(rowBytes);
        seat = _bytesToUint(seatBytes);
    }

    function _bytesToUint(bytes memory b) internal pure returns (uint256) {
        uint256 number;
        for (uint256 i = 0; i < b.length; i++) {
            number = number * 10 + (uint8(b[i]) - 48); // ASCII '0' is 48
        }
        return number;
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
