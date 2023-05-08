// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

contract SecondBuyer {
    mapping(address => uint256) public addressToAmountFunded;
    address payable[] public funders;

    constructor() payable {}

    function fund() external payable {
        addressToAmountFunded[msg.sender] += msg.value;
        funders.push(payable(msg.sender));
    }

    function end() external payable {
        // destroys this contract and send all the ETH back to the first funder - for testing purposes.
        selfdestruct(funders[0]);
    }
}
