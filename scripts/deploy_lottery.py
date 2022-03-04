from webbrowser import get
from scripts.help_scripts import get_account, get_contract, fund_with_link
from brownie import Lottery, config, accounts, network
import time


def deploy_lottery():
    account = get_account()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()]["verify"],
    )
    print("Lottery Deployed!")
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    start_lottery_txn = lottery.startLottery({"from": account})
    start_lottery_txn.wait(1)
    print("Lottery has started")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 1000000  # This is the entrance fee required
    enter_lottery_txn = lottery.enterLottery({"from": account, "value": value})
    enter_lottery_txn.wait(1)
    print("You have entered the lottery")


# fund contract
# then end lottery
def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    txn = fund_with_link(lottery.address)
    # txn.wait(1)
    end_lottery = lottery.endLottery({"from": account})
    end_lottery.wait(1)  # wait for callback
    time.sleep(90)
    print(f"Lottery has ended and {lottery.recentWinner()} is new winner")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
