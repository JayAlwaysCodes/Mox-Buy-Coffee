from eth_utils import to_wei
import boa

SEND_VALUE = to_wei(1, "ether")
RANDOM_USER = boa.env.generate_address("non-owner")

def test_price_feed_is_correct(coffee, eth_usd):
    assert coffee.PRICE_FEED() == eth_usd.address

def test_starting_values(coffee, account):
    assert coffee.MINIMUM_USD() == to_wei(5, "ether")
    assert coffee.OWNER() == account.address

def test_fund_fails_without_enough_eth(coffee):
    with boa.reverts():
        coffee.fund()

def test_fund_with_money(coffee, account):
    #arrange
    boa.env.set_balance(account.address, SEND_VALUE)
    #act
    coffee.fund(value=SEND_VALUE)
    #assert
    funder = coffee.funders(0)
    assert funder == account.address
    assert coffee.funder_to_amount_funded(funder) == SEND_VALUE


def test_non_owner_cannot_withdraw(coffee, account):
    #arrange
    boa.env.set_balance(account.address, SEND_VALUE)
    coffee.fund(value=SEND_VALUE)

    with boa.env.prank(RANDOM_USER):
        with boa.reverts():
            coffee.withdraw()
