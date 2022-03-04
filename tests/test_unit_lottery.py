from urllib import request
from brownie import Lottery, network, config, accounts, exceptions
from scripts.deploy_lottery import deploy_lottery
from scripts.help_scripts import LOCAL_BLOCKCHAIN_ENV, fund_with_link, get_account, get_contract
from web3 import Web3
import pytest


# testing that entrance fee is concordant with the price feed
def test_getentrancefee():
    # arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()
    lottery = deploy_lottery()
    # act
    # if 1 eth == 2960 usd
    # and usdEntryFee == 50
    # expected eth == 50/2960 == 0.0169
    expected_entrance_fee = Web3.toWei(0.0169, "ether")
    entrance_fee = lottery.getEntranceFee()
    # assert
    assert expected_entrance_fee >= entrance_fee


def test_cant_enter_unless_started():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()
    deploy_lottery()
    lottery = Lottery[-1]
    # account = get_account()
    # act / assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enterLottery({"from": get_account(), "value": lottery.getEntranceFee()})


# only admin can start lottery
def test_can_start_and_enter_lottery():
    # arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    # act
    lottery.enterLottery({"from": account, "value": lottery.getEntranceFee()})
    # assert that admin is in the lottery as first player
    assert lottery.players(0) == account

def test_can_end_lottery():
    # arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({'from': account})
    lottery.enterLottery({"from": account, "value": lottery.getEntranceFee()})
    # act
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    # assert that lottery state is calculating_winner,
    # @ index = 2
    assert lottery.lottery_state() == 2


def test_can_pick_winner_correctly():
     # arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({'from': account})
    lottery.enterLottery({"from": account, "value": lottery.getEntranceFee()})
    lottery.enterLottery({"from": get_account(index=1), "value": lottery.getEntranceFee()})
    lottery.enterLottery({"from": get_account(index=2), "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    txn = lottery.endLottery({"from": account})
    # Call the requestid from the RequestRandomness event
    request_Id = txn.events["RequestedRandomness"]["requestId"]
    STATIC_RANDOM_NUM = 603.3
    # call the callBackWithRandomness function from vrfcoordinator
    get_contract("vrf_coordinator").callBackWithRandomness(request_Id, STATIC_RANDOM_NUM,
     lottery.address, {"from": account})
    # assert that winner has been paid and
    # lottery.balance has been emptied
    balance_of_account = account.balance()
    starting_balance_of_lottery = lottery.balance()
    assert lottery.recentWinner() == get_account(0)
    assert lottery.balance() == 0
    assert account.balance() == starting_balance_of_lottery + balance_of_account

    
