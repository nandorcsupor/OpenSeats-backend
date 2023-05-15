// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/utils/Strings.sol";

contract Ticket is ERC721URIStorage {
    using Counters for Counters.Counter;
    Counters.Counter public _tokenIdCounter;

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
    mapping(uint256 => TicketData) public tickets;

    mapping(bytes32 => bool) public mintedTickets;

    AggregatorV3Interface internal priceFeed;

    uint256 public maxTickets;
    uint256[4] public ticketPrices;
    string[] public gateNames;

    string[] public _gates;
    string[] public _sections;
    uint256[] public _numberOfRowsPerSection;
    uint256[] public _numberOfSeatsPerRow;
    uint256[] public _pricesPerSection;

    // Event
    event TicketMinted(
        address indexed buyer,
        uint256 indexed tokenId,
        string gate,
        string section,
        uint256 row,
        uint256 seat
    );

    struct TicketParams {
        string[] gates;
        string[] sections;
        uint256[] numberOfRowsPerSection;
        uint256[] numberOfSeatsPerRow;
        uint256[] pricesPerSection;
    }

    struct VenueConfiguration {
        string[] gates;
        string[] sections;
        uint256[] numberOfRowsPerSection;
        uint256[] numberOfSeatsPerRow;
        uint256[] pricesPerSection;
    }

    event requirementsPassed(string passed);

    constructor(
        address _priceFeedAddress,
        uint256 _maxTickets,
        string memory tokenName,
        string memory tokenSymbol,
        VenueConfiguration memory config
    ) ERC721(tokenName, tokenSymbol) {
        // Set the address of the Chainlink ETH/USD price feed (on Sepolia testnet)
        // priceFeed = AggregatorV3Interface(
        // 0x694AA1769357215DE4FAC081bf1f309aDC325306
        //);

        priceFeed = AggregatorV3Interface(_priceFeedAddress);

        require(config.gates.length > 0, "Gates cannot be empty");
        require(config.sections.length > 0, "Sections cannot be empty");
        require(
            config.numberOfRowsPerSection.length == config.sections.length,
            "Number of rows should be equal to the number of sections"
        );
        require(
            config.numberOfSeatsPerRow.length ==
                config.numberOfRowsPerSection.length,
            "Number of seats should be equal to the number of rows"
        );
        require(
            config.pricesPerSection.length == config.sections.length,
            "Prices should be equal to the number of sections"
        );

        maxTickets = _maxTickets;
        _gates = config.gates;
        _sections = config.sections;
        _numberOfRowsPerSection = config.numberOfRowsPerSection;
        _numberOfSeatsPerRow = config.numberOfSeatsPerRow;
        _pricesPerSection = config.pricesPerSection;
    }

    function mintTicket(
        address to,
        string memory gate,
        string memory section,
        uint256 row,
        uint256 seat,
        uint8 category,
        string memory tokenURI_
    ) public payable {
        // Validate gate and section inputs
        require(isValidGate(_gates, gate), "Invalid gate");
        require(isValidSection(_sections, section), "Invalid section");

        // Validate row and seat inputs
        require(
            row > 0 && row <= _numberOfRowsPerSection[category - 1],
            "Invalid row"
        );
        require(
            seat > 0 && seat <= _numberOfSeatsPerRow[category - 1],
            "Invalid seat"
        );

        // Validate category input
        require(category >= 1 && category <= 4, "Invalid category");

        // Check if the ticket with the given seating info is available
        bytes32 ticketKey = keccak256(
            abi.encodePacked(gate, section, row, seat)
        );
        require(!mintedTickets[ticketKey], "Ticket not available");

        // Calculate the price in ETH using the current ETH/USD price
        uint256 priceInETH = (_pricesPerSection[category - 1] * 1e18) /
            getETHUSDPrice();
        require(msg.value >= priceInETH, "Not enough ETH sent");

        _tokenIdCounter.increment();
        uint256 tokenId = _tokenIdCounter.current();

        // Update mintedTickets mapping
        mintedTickets[ticketKey] = true;

        // Pass SeatingInfo struct to TicketData
        tickets[tokenId] = TicketData(
            SeatingInfo(section, row, seat, false),
            gate,
            priceInETH,
            false
        );

        _safeMint(to, tokenId);
        _setTokenURI(tokenId, tokenURI_);

        // Emit event
        emit TicketMinted(to, tokenId, gate, section, row, seat);
    }

    // Helper function to validate gate input
    function isValidGate(
        string[] memory _gates,
        string memory gate
    ) public view returns (bool) {
        for (uint256 i = 0; i < _gates.length; i++) {
            if (
                keccak256(abi.encodePacked(_gates[i])) ==
                keccak256(abi.encodePacked(gate))
            ) {
                return true;
            }
        }
        return false;
    }

    // Helper function to validate section input
    function isValidSection(
        string[] memory _sections,
        string memory section
    ) public view returns (bool) {
        for (uint256 i = 0; i < _sections.length; i++) {
            if (
                keccak256(abi.encodePacked(_sections[i])) ==
                keccak256(abi.encodePacked(section))
            ) {
                return true;
            }
        }
        return false;
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
                msg.value <= maxResalePrice,
                string(
                    abi.encodePacked(
                        "Resale price is too high (> 5%). Max Resale Price: ",
                        Strings.toString(maxResalePrice),
                        ". Current Value: ",
                        Strings.toString(msg.value)
                    )
                )
            );

            ticket.isResold = true;
        }
    }
}
