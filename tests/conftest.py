import pytest
from script.deploy import deploy_coffee
from script.deploy_mocks import deploy_feed
from moccasin.config import get_active_network
from eth_utils import to_wei
import boa

SEND_VALUE = to_wei(1, "ether")

@pytest.fixture(scope="session")
def account():
    return get_active_network().get_default_account()

@pytest.fixture(scope="session")
def eth_usd():
    return deploy_feed()

@pytest.fixture(scope="function")
def coffee(eth_usd):
    return deploy_coffee(eth_usd)

@pytest.fixture(scope="function")
def coffee_funded(coffee, account):
    boa.env.set_balance(account.address, SEND_VALUE)
    with boa.env.prank(account.address):
        coffee.fund(value=SEND_VALUE)
    return coffee