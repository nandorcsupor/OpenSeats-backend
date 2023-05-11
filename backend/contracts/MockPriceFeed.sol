// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MockPriceFeed {
    int256 private ethUsdPrice;

    function setEthUsdPrice(int256 price) public {
        ethUsdPrice = price;
    }

    function getEthUsdPrice() public view returns (int256) {
        return ethUsdPrice;
    }
}
