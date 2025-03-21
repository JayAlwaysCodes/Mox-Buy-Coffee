# pragma version 0.4.0

"""
@license MIT
@title Buy Me A Coffee
@dev A simple contract that allows users to donate to the contract owner.
@author Johnson
@notice This contract is for educational purposes only.
"""

interface AggregatorV3Interface:
    def decimals() -> uint8: view
    def description() -> String[1000]: view
    def version() -> uint256: view
    def latestAnswer() -> int256: view

#constants and Immutables
MINIMUM_USD: public(constant(uint256)) = as_wei_value(5, "ether")
PRICE_FEED: public(immutable(AggregatorV3Interface))
OWNER: public(immutable(address))
PRECISION: constant(uint256) = 1 * (10 ** 18)

# Storage
funders: public(DynArray[address, 1000])
funder_to_amount_funded: public(HashMap[address, uint256])

#with constants: 262, 853
@deploy
def __init__(price_feed: address):
    PRICE_FEED = AggregatorV3Interface(price_feed)
    OWNER = msg.sender

@external
@payable
def fund():
    self._fund()

@internal
@payable
def _fund():
    """Allows users to send money to this contract, Have a minimum amount to send"""

    usd_value_of_eth: uint256 = self._get_eth_to_usd_rate(msg.value)
    assert usd_value_of_eth >= MINIMUM_USD, "You need to spend more ETH"
    self.funders.append(msg.sender)
    self.funder_to_amount_funded[msg.sender] += msg.value

@external
def withdraw():
    """Allows the owner to withdraw funds from the contract"""
    assert msg.sender == OWNER, "You are not the owner"
    raw_call(OWNER, b"", value = self.balance)
    #send(OWNER, self.balance)
    # resetting the funders array
    for funder: address in self.funders:
        self.funder_to_amount_funded[funder] = 0
    self.funders = []

@internal
@view
def _get_eth_to_usd_rate(eth_amount: uint256) -> uint256:
    """Converts the amount of ETH to USD"""
    price: int256 = staticcall PRICE_FEED.latestAnswer()
    eth_price: uint256 = (convert(price, uint256)) * (10**10)
    eth_amount_in_usd: uint256 = (eth_price * eth_amount) // PRECISION
    return eth_amount_in_usd

@external
@view
def get_eth_to_usd_rate(eth_amount: uint256) -> uint256:
    return self._get_eth_to_usd_rate(eth_amount)

@external
@payable
def __default__():
    self._fund()
    

    
