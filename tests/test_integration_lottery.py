from brownie import network
import pytest
from scripts.help_scripts import LOCAL_BLOCKCHAIN_ENV, fund_with_link, get_account
from scripts.deploy_lottery import deploy_lottery
import time


# Integration testing is done on testnet e.g rinkeby, alchemy
def test_can_pick_winner_correctly():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enterLottery({"from": account, "value": lottery.getEntranceFee()})
    lottery.enterLottery(
        {"from": get_account(index=1), "value": lottery.getEntranceFee()}
    )
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    time.sleep(90)  # in unit test, i assumed a node but not for integration test
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
