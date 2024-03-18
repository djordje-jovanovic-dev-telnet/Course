from app.calculations import add, divide, multiply, substract, BankAccount
import pytest


@pytest.fixture
def zero_bank_account():
    return BankAccount()


@pytest.fixture
def bank_account():
    return BankAccount(500)


@pytest.mark.parametrize("x, y, expected", [(3, 2, 5), (5, 5, 10), (200, 120, 320)])
def test_add(x, y, expected):
    assert add(x, y) == expected


def test_divide():
    assert divide(6, 3) == 2


def test_mulitply():
    assert multiply(5, 3) == 15


def test_substract():
    assert substract(5, 3) == 2


def test_bank_set_inital_amount(bank_account):
    assert bank_account.balance == 500


def test_bank_default_amount(zero_bank_account):
    assert zero_bank_account.balance == 0


def test_bank_withdraw(bank_account):
    bank_account.withdraw(80)
    assert bank_account.balance == 420


def test_deposit(bank_account):
    bank_account.deposit(80)
    assert bank_account.balance == 580


def test_collect_interest(bank_account):
    bank_account.collect_interest()
    assert int(bank_account.balance) == 550


@pytest.mark.parametrize(
    "depo, wit, expected", [(400, 100, 300), (20, 7, 13), (7000, 200, 6800)]
)
def test_bank_transaction(zero_bank_account, depo, wit, expected):
    zero_bank_account.deposit(depo)
    zero_bank_account.withdraw(wit)
    assert zero_bank_account.balance == expected


def test_insufficient_funds(bank_account):
    with pytest.raises(Exception):
        bank_account.withdraw(2000)
