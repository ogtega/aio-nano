import asyncio

import pytest
from pytest import MonkeyPatch

from aio_nano import Client
from aio_nano.rpc.client import RPCException
from aio_nano.rpc.models import AccountBalances, AccountHistory, AccountInfo


class TestRPCClient:
    async def test_exception(
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
                lambda: {"error": "Bad account number"},
            ),
        )

        with pytest.raises(RPCException):
            await rpc.available_supply()

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

        balances = await rpc.account_balance(
            account="nano_3e3j5tkog48pnny9dmfzj1r16pg8t1e76dz5tmac6iq689wyjfpi00000000"
        )

        assert type(balances) == AccountBalances

    async def test_account_block_count(
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
                lambda: {"block_count": "19"},
            ),
        )

        block_count = await rpc.account_block_count(
            account="nano_3t6k35gi95xu6tergt6p69ck76ogmitsa8mnijtpxm9fkcm736xtoncuohr3"
        )

        assert block_count == 19
        assert type(block_count) == int

    async def test_account_get(
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
                    "account": "nano_1e5aqegc1jb7qe964u4adzmcezyo6o146zb8hm6dft8tkp79za3sxwjym5rx"
                },
            ),
        )

        account = await rpc.account_get(
            key="3068BB1CA04525BB0E416C485FE6A67FD52540227D267CC8B6E8DA958A7FA039"
        )

        assert (
            account
            == "nano_1e5aqegc1jb7qe964u4adzmcezyo6o146zb8hm6dft8tkp79za3sxwjym5rx"
        )

        assert type(account) == str

    async def test_account_history(
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
                    "account": "nano_1ipx847tk8o46pwxt5qjdbncjqcbwcc1rrmqnkztrfjy5k7z4imsrata9est",
                    "history": [
                        {
                            "type": "send",
                            "account": "nano_38ztgpejb7yrm7rr586nenkn597s3a1sqiy3m3uyqjicht7kzuhnihdk6zpz",
                            "amount": "80000000000000000000000000000000000",
                            "local_timestamp": "1551532723",
                            "height": "60",
                            "hash": "80392607E85E73CC3E94B4126F24488EBDFEB174944B890C97E8F36D89591DC5",
                            "confirmed": "true",
                        }
                    ],
                    "previous": "8D3AB98B301224253750D448B4BD997132400CEDD0A8432F775724F2D9821C72",
                },
            ),
        )

        account_history = await rpc.account_history(
            account="nano_1ipx847tk8o46pwxt5qjdbncjqcbwcc1rrmqnkztrfjy5k7z4imsrata9est",
            count=1,
        )

        assert len(account_history.history) == 1
        assert type(account_history) == AccountHistory

        monkeypatch.setattr(
            rpc,
            "_post",
            lambda _: event_loop.run_in_executor(
                None,
                lambda: {
                    "account": "nano_1ipx847tk8o46pwxt5qjdbncjqcbwcc1rrmqnkztrfjy5k7z4imsrata9est",
                    "history": [
                        {
                            "type": "state",
                            "representative": "nano_1stofnrxuz3cai7ze75o174bpm7scwj9jn3nxsn8ntzg784jf1gzn1jjdkou",
                            "link": "65706F636820763220626C6F636B000000000000000000000000000000000000",
                            "balance": "116024995745747584010554620134",
                            "previous": "F8F83276ACCBFCCD13783309861EEE81E5FAF97BD28F84ED1DA62C7D4460E531",
                            "subtype": "epoch",
                            "account": "nano_3qb6o6i1tkzr6jwr5s7eehfxwg9x6eemitdinbpi7u8bjjwsgqfj4wzser3x",
                            "local_timestamp": "1598397125",
                            "height": "281",
                            "hash": "BFD5D5214A93E614D64A7C05624F69E6CFD4F1CED3C5926562F282DF135B15CF",
                            "confirmed": "true",
                            "work": "894045458d590e7c",
                            "signature": "3D45D616545D5CCE9766E3F6268C9AE88C0DCA61A6B034AE4804D46C9F75EA94BCA7E7AEBA46EA98117120FB491FE2F7D0664675EF36D8BFD9818DAE62209F06",
                        }
                    ],
                    "previous": "F8F83276ACCBFCCD13783309861EEE81E5FAF97BD28F84ED1DA62C7D4460E531",
                },
            ),
        )

        raw_account_history = await rpc.account_history(
            account="nano_1ipx847tk8o46pwxt5qjdbncjqcbwcc1rrmqnkztrfjy5k7z4imsrata9est",
            count=1,
            raw=True,
        )

        assert len(raw_account_history.history) == 1
        assert type(raw_account_history) == AccountHistory

    async def test_account_info(
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
                    "frontier": "FF84533A571D953A596EA401FD41743AC85D04F406E76FDE4408EAED50B473C5",
                    "open_block": "991CF190094C00F0B68E2E5F75F6BEE95A2E0BD93CEAA4A6734DB9F19B728948",
                    "representative_block": "991CF190094C00F0B68E2E5F75F6BEE95A2E0BD93CEAA4A6734DB9F19B728948",
                    "balance": "235580100176034320859259343606608761791",
                    "modified_timestamp": "1501793775",
                    "block_count": "33",
                    "account_version": "1",
                    "confirmation_height": "28",
                    "confirmation_height_frontier": "34C70FCA0952E29ADC7BEE6F20381466AE42BD1CFBA4B7DFFE8BD69DF95449EB",
                },
            ),
        )

        account = await rpc.account_info(
            account="nano_3t6k35gi95xu6tergt6p69ck76ogmitsa8mnijtpxm9fkcm736xtoncuohr3"
        )

        assert type(account) == AccountInfo

        monkeypatch.setattr(
            rpc,
            "_post",
            lambda _: event_loop.run_in_executor(
                None,
                lambda: {
                    "frontier": "80A6745762493FA21A22718ABFA4F635656A707B48B3324198AC7F3938DE6D4F",
                    "open_block": "0E3F07F7F2B8AEDEA4A984E29BFE1E3933BA473DD3E27C662EC041F6EA3917A0",
                    "representative_block": "80A6745762493FA21A22718ABFA4F635656A707B48B3324198AC7F3938DE6D4F",
                    "balance": "11999999999999999918751838129509869131",
                    "confirmed_balance": "11999999999999999918751838129509869131",
                    "modified_timestamp": "1606934662",
                    "block_count": "22966",
                    "account_version": "1",
                    "confirmed_height": "22966",
                    "confirmed_frontier": "80A6745762493FA21A22718ABFA4F635656A707B48B3324198AC7F3938DE6D4F",
                    "representative": "nano_1gyeqc6u5j3oaxbe5qy1hyz3q745a318kh8h9ocnpan7fuxnq85cxqboapu5",
                    "confirmed_representative": "nano_1gyeqc6u5j3oaxbe5qy1hyz3q745a318kh8h9ocnpan7fuxnq85cxqboapu5",
                    "weight": "11999999999999999918751838129509869131",
                    "pending": "0",
                    "receivable": "0",
                    "confirmed_pending": "0",
                    "confirmed_receivable": "0",
                },
            ),
        )

        confirmed_account = await rpc.account_info(
            account="nano_1gyeqc6u5j3oaxbe5qy1hyz3q745a318kh8h9ocnpan7fuxnq85cxqboapu5",
            representative=True,
            weight=True,
            receivable=True,
            include_confirmed=True,
        )

        assert type(confirmed_account) == AccountInfo

        monkeypatch.setattr(
            rpc,
            "_post",
            lambda _: event_loop.run_in_executor(
                None,
                lambda: {
                    "frontier": "80A6745762493FA21A22718ABFA4F635656A707B48B3324198AC7F3938DE6D4F",
                    "open_block": "0E3F07F7F2B8AEDEA4A984E29BFE1E3933BA473DD3E27C662EC041F6EA3917A0",
                    "representative_block": "80A6745762493FA21A22718ABFA4F635656A707B48B3324198AC7F3938DE6D4F",
                    "balance": "11999999999999999918751838129509869131",
                    "confirmed_balance": "11999999999999999918751838129509869131",
                    "modified_timestamp": "1606934662",
                    "block_count": "22966",
                    "account_version": "1",
                    "confirmed_height": "22966",
                    "confirmed_frontier": "80A6745762493FA21A22718ABFA4F635656A707B48B3324198AC7F3938DE6D4F",
                    "representative": "nano_1gyeqc6u5j3oaxbe5qy1hyz3q745a318kh8h9ocnpan7fuxnq85cxqboapu5",
                    "confirmed_representative": "nano_1gyeqc6u5j3oaxbe5qy1hyz3q745a318kh8h9ocnpan7fuxnq85cxqboapu5",
                    "weight": "11999999999999999918751838129509869131",
                    "pending": "0",
                    "receivable": "0",
                    "confirmed_pending": "0",
                    "confirmed_receivable": "0",
                },
            ),
        )

        unconfirmed_account = await rpc.account_info(
            account="nano_1gyeqc6u5j3oaxbe5qy1hyz3q745a318kh8h9ocnpan7fuxnq85cxqboapu5",
            representative=True,
            weight=True,
            receivable=True,
        )

        assert type(unconfirmed_account) == AccountInfo

    async def test_account_key(
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
                    "key": "3068BB1CA04525BB0E416C485FE6A67FD52540227D267CC8B6E8DA958A7FA039"
                },
            ),
        )

        key = await rpc.account_key(
            account="nano_1e5aqegc1jb7qe964u4adzmcezyo6o146zb8hm6dft8tkp79za3sxwjym5rx"
        )

        assert key == "3068BB1CA04525BB0E416C485FE6A67FD52540227D267CC8B6E8DA958A7FA039"
        assert type(key) == str
