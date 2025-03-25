from moccasin.config import get_active_network
from src import buy_me_a_coffee
from script.deploy_mocks import deploy_feed
from moccasin.boa_tools import VyperContract

def deploy_coffee(price_feed: VyperContract) -> VyperContract:
    print("Deploying Contract...")
    coffee: VyperContract = buy_me_a_coffee.deploy(price_feed)

    active_network = get_active_network()
    if active_network.has_explorer():
        result = active_network.moccasin_verify(coffee)
        result.wait_for_verification()
    return coffee

def moccasin_main() -> VyperContract:
    active_network = get_active_network()
    price_feed: VyperContract = active_network.manifest_named("price_feed")
    print(f"On network {active_network.name}, using price feed at {price_feed}")
    return deploy_coffee(price_feed)


    # price_feed: VyperContract = deploy_feed()
    # coffee = buy_me_a_coffee.deploy(price_feed)
    # print("Coffee deployed at", coffee.address)