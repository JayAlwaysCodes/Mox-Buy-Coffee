from eth_utils import to_wei
import boa
from tests.conftest import SEND_VALUE


RANDOM_USER = boa.env.generate_address("non-owner")
NUM_FUNDERS = 10

def test_price_feed_is_correct(coffee, eth_usd):
    assert coffee.PRICE_FEED() == eth_usd.address

def test_starting_values(coffee, account):
    assert coffee.MINIMUM_USD() == to_wei(5, "ether")
    assert coffee.OWNER() == account.address

def test_fund_fails_without_enough_eth(coffee):
    with boa.reverts():
        coffee.fund()

def test_fund_with_money(coffee_funded, account):
    
    #assert
    funder = coffee_funded.funders(0)
    assert funder == account.address
    assert coffee_funded.funder_to_amount_funded(funder) == SEND_VALUE


def test_non_owner_cannot_withdraw(coffee_funded):
   
    

    with boa.env.prank(RANDOM_USER):
        with boa.reverts():
            coffee_funded.withdraw()


def test_owner_can_withdraw(coffee_funded):
    with boa.env.prank(coffee_funded.OWNER()):
        
        coffee_funded.withdraw()
    assert boa.env.get_balance(coffee_funded.address) == 0


def test_multiple_funders_and_withdraw(coffee, account):
    # Arrange
    funders = [boa.env.generate_address(f"funder{i}") for i in range(NUM_FUNDERS)]
    total_value = SEND_VALUE * NUM_FUNDERS
    
    # Get initial owner balance
    initial_owner_balance = boa.env.get_balance(account.address)
    
    # Act: Fund from multiple accounts
    for funder in funders:
        boa.env.set_balance(funder, SEND_VALUE)
        with boa.env.prank(funder):
            coffee.fund(value=SEND_VALUE)
    
    # Verify all funders are recorded by checking each element
    # Since we can't get length directly, we'll:
    # 1. Check that first N elements match our funders
    # 2. Check that element N+1 reverts (indicating end of array)
    for i in range(NUM_FUNDERS):
        assert coffee.funders(i) == funders[i]
    
    # Verify there are no more funders by checking that accessing index num_funders reverts
    with boa.reverts():
        coffee.funders(NUM_FUNDERS)
    
    # Act: Owner withdraws
    with boa.env.prank(account.address):
        coffee.withdraw()
    
    # Assert
    # 1. Contract balance should be 0
    assert boa.env.get_balance(coffee.address) == 0
    
    # 2. Owner should have received all funds (with gas buffer)
    current_owner_balance = boa.env.get_balance(account.address)
    assert current_owner_balance >= initial_owner_balance + total_value - to_wei(0.1, "ether")
    
    # 3. Verify funders' amounts are reset
    for funder in funders:
        assert coffee.funder_to_amount_funded(funder) == 0
    
    # 4. Verify funders array is empty by checking index 0 reverts
    with boa.reverts():
        coffee.funders(0)


def test_get_rate(coffee):
    assert coffee.get_eth_to_usd_rate(SEND_VALUE) > 0

def test_fund_exact_minimum_value(coffee, account, eth_usd):
    """Test funding with exactly the minimum required USD value"""
    # Get current ETH price (returns price with 8 decimals)
    _, price, _, _, _ = eth_usd.latestRoundData()
    
    # Calculate exact ETH needed (MINIMUM_USD is in wei units)
    # Formula: (min_usd * 1e18) / (price * 1e10) since:
    # - MINIMUM_USD is in wei (1e18)
    # - price has 8 decimals (1e8)
    # - Need to convert to wei (1e18)
    min_eth_wei = (coffee.MINIMUM_USD() * 10**18) // (price * 10**10)
    
    # Ensure we have an integer value
    assert isinstance(min_eth_wei, int)
    
    boa.env.set_balance(account.address, min_eth_wei)
    with boa.env.prank(account.address):
        coffee.fund(value=min_eth_wei)
    
    assert coffee.funders(0) == account.address

def test_fund_just_below_minimum(coffee, account, eth_usd):
    """Test funding with value just below minimum"""
    _, price, _, _, _ = eth_usd.latestRoundData()
    
    # Calculate minimum ETH in wei
    min_eth_wei = (coffee.MINIMUM_USD() * 10**18) // (price * 10**10)
    
    # Calculate just below (99% of min)
    just_below = (min_eth_wei * 99) // 100
    
    # Ensure we have integer values
    assert isinstance(min_eth_wei, int)
    assert isinstance(just_below, int)
    
    boa.env.set_balance(account.address, just_below)
    with boa.env.prank(account.address):
        with boa.reverts("You need to spend more ETH"):
            coffee.fund(value=just_below)


