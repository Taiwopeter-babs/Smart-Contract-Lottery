from brownie import (
    Lottery,
    config,
    accounts,
    network,
    MockV3Aggregator,
    VRFCoordinatorMock,
    LinkToken,
    interface,
    Contract,
)
from web3 import Web3


DECIMALS = 8
INITIAL_VALUE = 296000000000

LOCAL_BLOCKCHAIN_ENV = ["development", "ganache-local"]
FORKED_BLOCKCHAIN_ENV = ["mainnet-fork", "mainnet-fork-dev"]


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENV
        or network.show_active() in FORKED_BLOCKCHAIN_ENV
    ):
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])


"""
    The get_contract function gets a defined contract addresses from the config if 
    defined, else a mock is deployed and returned.
     
     Argument: contract_name

     Returns: either a mock or a live contract of the most recently deployed contract. 
"""

contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_contract(contract_name):
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENV:
        if len(contract_type) <= 0:  # MockV3Aggregator.length
            deploy_mocks()
        contract = contract_type[-1]  # MockV3Aggregator[-1]
    else:
        contract_address = config["networks"][network.show_active()][
            contract_name
        ]  # the last parameter is a string
        # You need the contract name, address and abi
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract


def deploy_mocks(Decimals=DECIMALS, Initial_value=INITIAL_VALUE):
    account = get_account()
    MockV3Aggregator.deploy(Decimals, Initial_value, {"from": get_account()})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print(f"The active network is {network.show_active()}")
    print("Deployed!")


def fund_with_link(
    contract_address, account=None, link_token=None, amount=1 * 10 ** 17
):
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    txn = link_token.transfer(contract_address, amount, {"from": account})
    # using interface
    """link_token_contract = interface.LinkTokenInteface(link_token.address)
    txn = link_token_contract.transfer(contract_address, amount, {"from": account})"""
    txn.wait(1)
    print(f"Fund your contract with at least {amount}")
