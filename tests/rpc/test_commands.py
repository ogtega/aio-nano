import asyncio

import pytest
from pytest import MonkeyPatch

from aio_nano import Client
from aio_nano.rpc.client import RPCException


class TestRPCClient:
    async def test_account_balance(
        self,
        rpc: Client,
        event_loop: asyncio.AbstractEventLoop,
        monkeypatch: MonkeyPatch,
    ):
        monkeypatch.setattr(
            rpc,
            "_post",
            lambda _: event_loop.run_in_executor(
                None,
                lambda: {
                    "balance": "10000",
                    "pending": "10000",
                    "receivable": "10000",
                },
            ),
        )

        account = await rpc.account_balance(
            account="nano_1c3jhrd3q8dn79op9ayawn45erczu11mfrhrgao7ahaxfrpcfuztoiog9bmz"
        )

        assert account.balance == 10000
        assert account.pending == 10000
        assert account.receivable == 10000

        monkeypatch.setattr(
            rpc,
            "_post",
            lambda _: event_loop.run_in_executor(
                None,
                lambda: {"error": "Bad account number"},
            ),
        )

        with pytest.raises(RPCException):
            await rpc.account_balance(
                account="nano_1c3jhrd3q8dn79op9ayawn45erczu11mfrhrgao7ahaxfrpcfuztoiog9bmz"
            )
