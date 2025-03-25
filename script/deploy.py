from moccasin.config import get_active_network
from src import buy_me_a_coffee

def deploy_coffee():
    print("Deploying Contract...")
    buy_me_a_coffee.deploy(price_feed)


def moccasin_main():
    active_network = get_active_network()