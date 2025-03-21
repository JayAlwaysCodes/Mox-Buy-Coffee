from interfaces import AggregatorV3Interface

PRECISION: constant(uint256) = 1 * (10 ** 18)


@internal
@view
def _get_eth_to_usd_rate(price_feed: AggregatorV3Interface, eth_amount: uint256) -> uint256:
    """Converts the amount of ETH to USD"""
    price: int256 = staticcall price_feed.latestAnswer()
    eth_price: uint256 = (convert(price, uint256)) * (10**10)
    eth_amount_in_usd: uint256 = (eth_price * eth_amount) // PRECISION
    return eth_amount_in_usd