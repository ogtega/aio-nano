import asyncio
from ensurepip import bootstrap

import pytest
from pytest import MonkeyPatch

from aio_nano import Client
from aio_nano.rpc.client import RPCException
from aio_nano.rpc.models import (
    AccountBalances,
    AccountHistory,
    AccountInfo,
    AccountPendingInfo,
    ActiveConfirmationInfo,
    Block,
    BlockCounts,
    BlockInfo,
    ConfirmationInfo,
    ConfirmationQuorum,
    DeterministicKeypair,
    LazyBootstrapInfo,
    SignedBlock,
)


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

    async def test_account_representative(
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
                    "representative": "nano_16u1uufyoig8777y6r8iqjtrw8sg8maqrm36zzcm95jmbd9i9aj5i8abr8u5"
                },
            ),
        )

        representative = await rpc.account_representative(
            account="nano_39a73oy5ungrhxy5z5oao1xso4zo7dmgpjd4u74xcrx3r1w6rtazuouw6qfi"
        )

        assert (
            representative
            == "nano_16u1uufyoig8777y6r8iqjtrw8sg8maqrm36zzcm95jmbd9i9aj5i8abr8u5"
        )
        assert type(representative) == str

    async def test_account_weight(
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
                lambda: {"weight": "10000"},
            ),
        )

        weight = await rpc.account_weight(
            account="nano_3e3j5tkog48pnny9dmfzj1r16pg8t1e76dz5tmac6iq689wyjfpi00000000"
        )

        assert weight == 10000
        assert type(weight) == int

    async def test_accounts_balances(
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
                    "balances": {
                        "nano_3t6k35gi95xu6tergt6p69ck76ogmitsa8mnijtpxm9fkcm736xtoncuohr3": {
                            "balance": "325586539664609129644855132177",
                            "pending": "2309372032769300000000000000000000",
                            "receivable": "2309372032769300000000000000000000",
                        },
                        "nano_3i1aq1cchnmbn9x5rsbap8b15akfh7wj7pwskuzi7ahz8oq6cobd99d4r3b7": {
                            "balance": "10000000",
                            "pending": "0",
                            "receivable": "0",
                        },
                    }
                },
            ),
        )

        balances = await rpc.accounts_balances(
            accounts=[
                "nano_3t6k35gi95xu6tergt6p69ck76ogmitsa8mnijtpxm9fkcm736xtoncuohr3",
                "nano_3i1aq1cchnmbn9x5rsbap8b15akfh7wj7pwskuzi7ahz8oq6cobd99d4r3b7",
            ]
        )

        assert type(balances) == dict

        for _, balance in balances.items():
            assert type(balance) == AccountBalances

        assert len(balances) == 2

    async def test_accounts_frontiers(
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
                    "frontiers": {
                        "nano_3t6k35gi95xu6tergt6p69ck76ogmitsa8mnijtpxm9fkcm736xtoncuohr3": "791AF413173EEE674A6FCF633B5DFC0F3C33F397F0DA08E987D9E0741D40D81A",
                        "nano_3i1aq1cchnmbn9x5rsbap8b15akfh7wj7pwskuzi7ahz8oq6cobd99d4r3b7": "6A32397F4E95AF025DE29D9BF1ACE864D5404362258E06489FABDBA9DCCC046F",
                    }
                },
            ),
        )

        frontiers = await rpc.accounts_frontiers(
            accounts=[
                "nano_3t6k35gi95xu6tergt6p69ck76ogmitsa8mnijtpxm9fkcm736xtoncuohr3",
                "nano_3i1aq1cchnmbn9x5rsbap8b15akfh7wj7pwskuzi7ahz8oq6cobd99d4r3b7",
            ]
        )

        assert type(frontiers) == dict

        for _, frontier in frontiers.items():
            assert type(frontier) == str

    async def test_accounts_pending(
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
                    "blocks": {
                        "nano_1111111111111111111111111111111111111111111111111117353trpda": [
                            "142A538F36833D1CC78B94E11C766F75818F8B940771335C6C1B8AB880C5BB1D"
                        ],
                        "nano_3t6k35gi95xu6tergt6p69ck76ogmitsa8mnijtpxm9fkcm736xtoncuohr3": [
                            "4C1FEEF0BEA7F50BE35489A1233FE002B212DEA554B55B1B470D78BD8F210C74"
                        ],
                    }
                },
            ),
        )

        pending = await rpc.accounts_pending(
            accounts=[
                "nano_1111111111111111111111111111111111111111111111111117353trpda",
                "nano_3t6k35gi95xu6tergt6p69ck76ogmitsa8mnijtpxm9fkcm736xtoncuohr3",
            ],
            count=1,
        )

        assert type(pending) == dict

        for _, pending_blocks in pending.items():
            assert type(pending_blocks) == list
            for hash in pending_blocks:
                assert type(hash) == str

        monkeypatch.setattr(
            rpc,
            "_post",
            lambda _: event_loop.run_in_executor(
                None,
                lambda: {
                    "blocks": {
                        "nano_1111111111111111111111111111111111111111111111111117353trpda": {
                            "142A538F36833D1CC78B94E11C766F75818F8B940771335C6C1B8AB880C5BB1D": "6000000000000000000000000000000"
                        },
                        "nano_3t6k35gi95xu6tergt6p69ck76ogmitsa8mnijtpxm9fkcm736xtoncuohr3": {
                            "4C1FEEF0BEA7F50BE35489A1233FE002B212DEA554B55B1B470D78BD8F210C74": "106370018000000000000000000000000"
                        },
                    }
                },
            ),
        )

        threshold_pending = await rpc.accounts_pending(
            accounts=[
                "nano_1111111111111111111111111111111111111111111111111117353trpda",
                "nano_3t6k35gi95xu6tergt6p69ck76ogmitsa8mnijtpxm9fkcm736xtoncuohr3",
            ],
            count=1,
            threshold=1000000000000000000000000,
        )

        assert type(threshold_pending) == dict

        for _, threshold_blocks in threshold_pending.items():
            assert type(threshold_blocks) == dict
            for _, amount in threshold_blocks.items():
                assert type(amount) == int

        monkeypatch.setattr(
            rpc,
            "_post",
            lambda _: event_loop.run_in_executor(
                None,
                lambda: {
                    "blocks": {
                        "nano_1111111111111111111111111111111111111111111111111117353trpda": {
                            "142A538F36833D1CC78B94E11C766F75818F8B940771335C6C1B8AB880C5BB1D": {
                                "amount": "6000000000000000000000000000000",
                                "source": "nano_3dcfozsmekr1tr9skf1oa5wbgmxt81qepfdnt7zicq5x3hk65fg4fqj58mbr",
                            }
                        },
                        "nano_3t6k35gi95xu6tergt6p69ck76ogmitsa8mnijtpxm9fkcm736xtoncuohr3": {
                            "4C1FEEF0BEA7F50BE35489A1233FE002B212DEA554B55B1B470D78BD8F210C74": {
                                "amount": "106370018000000000000000000000000",
                                "source": "nano_13ezf4od79h1tgj9aiu4djzcmmguendtjfuhwfukhuucboua8cpoihmh8byo",
                            }
                        },
                    }
                },
            ),
        )

        source_pending = await rpc.accounts_pending(
            accounts=[
                "nano_1111111111111111111111111111111111111111111111111117353trpda",
                "nano_3t6k35gi95xu6tergt6p69ck76ogmitsa8mnijtpxm9fkcm736xtoncuohr3",
            ],
            count=1,
            source=True,
        )

        assert type(source_pending) == dict

        for _, source_blocks in source_pending.items():
            assert type(source_blocks) == dict
            for _, info in source_blocks.items():
                assert type(info) == AccountPendingInfo

    async def test_accounts_representatives(
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
                    "representatives": {
                        "nano_16u1uufyoig8777y6r8iqjtrw8sg8maqrm36zzcm95jmbd9i9aj5i8abr8u5": "nano_3hd4ezdgsp15iemx7h81in7xz5tpxi43b6b41zn3qmwiuypankocw3awes5k",
                        "nano_3t6k35gi95xu6tergt6p69ck76ogmitsa8mnijtpxm9fkcm736xtoncuohr3": "nano_3t6k35gi95xu6tergt6p69ck76ogmitsa8mnijtpxm9fkcm736xtoncuohr3",
                    }
                },
            ),
        )

        reps = await rpc.accounts_representatives(
            accounts=[
                "nano_16u1uufyoig8777y6r8iqjtrw8sg8maqrm36zzcm95jmbd9i9aj5i8abr8u5",
                "nano_3t6k35gi95xu6tergt6p69ck76ogmitsa8mnijtpxm9fkcm736xtoncuohr3",
            ]
        )

        assert type(reps) == dict
        for _, rep in reps.items():
            assert type(rep) == str

    async def test_available_supply(
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
                lambda: {"available": "133248061996216572282917317807824970865"},
            ),
        )

        supply = await rpc.available_supply()
        assert type(supply) == int

    async def test_block_account(
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
                    "account": "nano_3t6k35gi95xu6tergt6p69ck76ogmitsa8mnijtpxm9fkcm736xtoncuohr3"
                },
            ),
        )

        account = await rpc.block_account(
            hash="023B94B7D27B311666C8636954FE17F1FD2EAA97A8BAC27DE5084FBBD5C6B02C"
        )

        assert type(account) == str

    async def test_block_confirm(
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
                lambda: {"started": "1"},
            ),
        )

        started = await rpc.block_confirm(
            hash="000D1BAEC8EC208142C99059B393051BAC8380F9B5A2E6B2489A277D81789F3F"
        )

        assert type(started) == bool
        assert started

    async def test_block_count(
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
                lambda: {"count": "1000", "unchecked": "10", "cemented": "25"},
            ),
        )

        counts = await rpc.block_count()

        assert type(counts) == BlockCounts

        monkeypatch.setattr(
            rpc,
            "_post",
            lambda _: event_loop.run_in_executor(
                None,
                lambda: {"count": "1000", "unchecked": "10"},
            ),
        )

        uncemented_counts = await rpc.block_count(include_cemented=False)

        assert type(uncemented_counts) == BlockCounts

    async def test_block_create(
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
                    "hash": "FF0144381CFF0B2C079A115E7ADA7E96F43FD219446E7524C48D1CC9900C4F17",
                    "difficulty": "ffffffe1278b3dc6",
                    "block": {
                        "type": "state",
                        "account": "nano_3qgmh14nwztqw4wmcdzy4xpqeejey68chx6nciczwn9abji7ihhum9qtpmdr",
                        "previous": "F47B23107E5F34B2CE06F562B5C435DF72A533251CB414C51B2B62A8F63A00E4",
                        "representative": "nano_1hza3f7wiiqa7ig3jczyxj5yo86yegcmqk3criaz838j91sxcckpfhbhhra1",
                        "balance": "1000000000000000000000",
                        "link": "19D3D919475DEED4696B5D13018151D1AF88B2BD3BCFF048B45031C1F36D1858",
                        "link_as_account": "nano_18gmu6engqhgtjnppqam181o5nfhj4sdtgyhy36dan3jr9spt84rzwmktafc",
                        "signature": "3BFBA64A775550E6D49DF1EB8EEC2136DCD74F090E2ED658FBD9E80F17CB1C9F9F7BDE2B93D95558EC2F277FFF15FD11E6E2162A1714731B743D1E941FA4560A",
                        "work": "cab7404f0b5449d0",
                    },
                },
            ),
        )

        block = await rpc.block_create(
            json_block="true",
            type="state",
            balance=1000000000000000000000,
            key="0000000000000000000000000000000000000000000000000000000000000002",
            representative="nano_1hza3f7wiiqa7ig3jczyxj5yo86yegcmqk3criaz838j91sxcckpfhbhhra1",
            link="19D3D919475DEED4696B5D13018151D1AF88B2BD3BCFF048B45031C1F36D1858",
            previous="F47B23107E5F34B2CE06F562B5C435DF72A533251CB414C51B2B62A8F63A00E4",
        )

        assert type(block) == SignedBlock

    async def test_block_hash(
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
                    "hash": "FF0144381CFF0B2C079A115E7ADA7E96F43FD219446E7524C48D1CC9900C4F17"
                },
            ),
        )

        hash = await rpc.block_hash(
            {
                "type": "state",
                "account": "nano_3qgmh14nwztqw4wmcdzy4xpqeejey68chx6nciczwn9abji7ihhum9qtpmdr",
                "previous": "F47B23107E5F34B2CE06F562B5C435DF72A533251CB414C51B2B62A8F63A00E4",
                "representative": "nano_1hza3f7wiiqa7ig3jczyxj5yo86yegcmqk3criaz838j91sxcckpfhbhhra1",
                "balance": "1000000000000000000000",
                "link": "19D3D919475DEED4696B5D13018151D1AF88B2BD3BCFF048B45031C1F36D1858",
                "link_as_account": "nano_18gmu6engqhgtjnppqam181o5nfhj4sdtgyhy36dan3jr9spt84rzwmktafc",
                "signature": "3BFBA64A775550E6D49DF1EB8EEC2136DCD74F090E2ED658FBD9E80F17CB1C9F9F7BDE2B93D95558EC2F277FFF15FD11E6E2162A1714731B743D1E941FA4560A",
                "work": "cab7404f0b5449d0",
            }
        )

        assert type(hash) == str

    async def test_block_info(
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
                    "block_account": "nano_1ipx847tk8o46pwxt5qjdbncjqcbwcc1rrmqnkztrfjy5k7z4imsrata9est",
                    "amount": "30000000000000000000000000000000000",
                    "balance": "5606157000000000000000000000000000000",
                    "height": "58",
                    "local_timestamp": "0",
                    "successor": "8D3AB98B301224253750D448B4BD997132400CEDD0A8432F775724F2D9821C72",
                    "confirmed": "true",
                    "contents": {
                        "type": "state",
                        "account": "nano_1ipx847tk8o46pwxt5qjdbncjqcbwcc1rrmqnkztrfjy5k7z4imsrata9est",
                        "previous": "CE898C131AAEE25E05362F247760F8A3ACF34A9796A5AE0D9204E86B0637965E",
                        "representative": "nano_1stofnrxuz3cai7ze75o174bpm7scwj9jn3nxsn8ntzg784jf1gzn1jjdkou",
                        "balance": "5606157000000000000000000000000000000",
                        "link": "5D1AA8A45F8736519D707FCB375976A7F9AF795091021D7E9C7548D6F45DD8D5",
                        "link_as_account": "nano_1qato4k7z3spc8gq1zyd8xeqfbzsoxwo36a45ozbrxcatut7up8ohyardu1z",
                        "signature": "82D41BC16F313E4B2243D14DFFA2FB04679C540C2095FEE7EAE0F2F26880AD56DD48D87A7CC5DD760C5B2D76EE2C205506AA557BF00B60D8DEE312EC7343A501",
                        "work": "8a142e07a10996d5",
                    },
                    "subtype": "send",
                },
            ),
        )

        info = await rpc.block_info(
            hash="87434F8041869A01C8F6F263B87972D7BA443A72E0A97D7A3FD0CCC2358FD6F9"
        )

        assert type(info) == BlockInfo

    async def test_blocks(
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
                    "blocks": {
                        "87434F8041869A01C8F6F263B87972D7BA443A72E0A97D7A3FD0CCC2358FD6F9": {
                            "type": "state",
                            "account": "nano_1ipx847tk8o46pwxt5qjdbncjqcbwcc1rrmqnkztrfjy5k7z4imsrata9est",
                            "previous": "CE898C131AAEE25E05362F247760F8A3ACF34A9796A5AE0D9204E86B0637965E",
                            "representative": "nano_1stofnrxuz3cai7ze75o174bpm7scwj9jn3nxsn8ntzg784jf1gzn1jjdkou",
                            "balance": "5606157000000000000000000000000000000",
                            "link": "5D1AA8A45F8736519D707FCB375976A7F9AF795091021D7E9C7548D6F45DD8D5",
                            "link_as_account": "nano_1qato4k7z3spc8gq1zyd8xeqfbzsoxwo36a45ozbrxcatut7up8ohyardu1z",
                            "signature": "82D41BC16F313E4B2243D14DFFA2FB04679C540C2095FEE7EAE0F2F26880AD56DD48D87A7CC5DD760C5B2D76EE2C205506AA557BF00B60D8DEE312EC7343A501",
                            "work": "8a142e07a10996d5",
                        }
                    }
                },
            ),
        )

        blocks = await rpc.blocks(
            hashes=["87434F8041869A01C8F6F263B87972D7BA443A72E0A97D7A3FD0CCC2358FD6F9"]
        )

        assert type(blocks) == dict
        for _, block in blocks.items():
            assert type(block) == Block

    async def test_blocks_info(
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
                    "blocks": {
                        "87434F8041869A01C8F6F263B87972D7BA443A72E0A97D7A3FD0CCC2358FD6F9": {
                            "block_account": "nano_1ipx847tk8o46pwxt5qjdbncjqcbwcc1rrmqnkztrfjy5k7z4imsrata9est",
                            "amount": "30000000000000000000000000000000000",
                            "balance": "5606157000000000000000000000000000000",
                            "height": "58",
                            "local_timestamp": "0",
                            "successor": "8D3AB98B301224253750D448B4BD997132400CEDD0A8432F775724F2D9821C72",
                            "confirmed": "true",
                            "contents": {
                                "type": "state",
                                "account": "nano_1ipx847tk8o46pwxt5qjdbncjqcbwcc1rrmqnkztrfjy5k7z4imsrata9est",
                                "previous": "CE898C131AAEE25E05362F247760F8A3ACF34A9796A5AE0D9204E86B0637965E",
                                "representative": "nano_1stofnrxuz3cai7ze75o174bpm7scwj9jn3nxsn8ntzg784jf1gzn1jjdkou",
                                "balance": "5606157000000000000000000000000000000",
                                "link": "5D1AA8A45F8736519D707FCB375976A7F9AF795091021D7E9C7548D6F45DD8D5",
                                "link_as_account": "nano_1qato4k7z3spc8gq1zyd8xeqfbzsoxwo36a45ozbrxcatut7up8ohyardu1z",
                                "signature": "82D41BC16F313E4B2243D14DFFA2FB04679C540C2095FEE7EAE0F2F26880AD56DD48D87A7CC5DD760C5B2D76EE2C205506AA557BF00B60D8DEE312EC7343A501",
                                "work": "8a142e07a10996d5",
                            },
                            "subtype": "send",
                        }
                    }
                },
            ),
        )

        blocks = await rpc.blocks_info(
            hashes=["87434F8041869A01C8F6F263B87972D7BA443A72E0A97D7A3FD0CCC2358FD6F9"]
        )

        assert type(blocks) == dict
        for _, info in blocks.items():
            assert type(info) == BlockInfo

        monkeypatch.setattr(
            rpc,
            "_post",
            lambda _: event_loop.run_in_executor(
                None,
                lambda: {
                    "blocks": {
                        "E2FB233EF4554077A7BF1AA85851D5BF0B36965D2B0FB504B2BC778AB89917D3": {
                            "block_account": "nano_1qato4k7z3spc8gq1zyd8xeqfbzsoxwo36a45ozbrxcatut7up8ohyardu1z",
                            "amount": "30000000000000000000000000000000000",
                            "balance": "40200000001000000000000000000000000",
                            "height": "74",
                            "local_timestamp": "0",
                            "successor": "678B9357455396B228325CA5A5CA7237DCC42362693DCAEFA840DEE171596349",
                            "confirmed": "true",
                            "contents": {
                                "type": "state",
                                "account": "nano_1qato4k7z3spc8gq1zyd8xeqfbzsoxwo36a45ozbrxcatut7up8ohyardu1z",
                                "previous": "6CDDA48608C7843A0AC1122BDD46D9E20E21190986B19EAC23E7F33F2E6A6766",
                                "representative": "nano_3pczxuorp48td8645bs3m6c3xotxd3idskrenmi65rbrga5zmkemzhwkaznh",
                                "balance": "40200000001000000000000000000000000",
                                "link": "87434F8041869A01C8F6F263B87972D7BA443A72E0A97D7A3FD0CCC2358FD6F9",
                                "link_as_account": "nano_33t5by1653nt196hfwm5q3wq7oxtaix97r7bhox5zn8eratrzoqsny49ftsd",
                                "signature": "A5DB164F6B81648F914E49CAB533900C389FAAD64FBB24F6902F9261312B29F730D07E9BCCD21D918301419B4E05B181637CF8419ED4DCBF8EF2539EB2467F07",
                                "work": "000bc55b014e807d",
                            },
                            "subtype": "receive",
                            "pending": "0",
                            "source_account": "nano_1ipx847tk8o46pwxt5qjdbncjqcbwcc1rrmqnkztrfjy5k7z4imsrata9est",
                        }
                    }
                },
            ),
        )

        blocks_optional = await rpc.blocks_info(
            hashes=["E2FB233EF4554077A7BF1AA85851D5BF0B36965D2B0FB504B2BC778AB89917D3"],
            pending=True,
            source=True,
        )

        assert type(blocks_optional) == dict
        for _, info_optional in blocks.items():
            assert type(info_optional) == BlockInfo

    async def test_bootstrap(
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
                lambda: {"success": ""},
            ),
        )

        success = await rpc.bootstrap(address="::ffff:138.201.94.249", port="7075")
        assert type(success) == bool
        assert success

    async def test_bootstrap_any(
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
                lambda: {"success": ""},
            ),
        )

        success = await rpc.bootstrap_any()
        assert type(success) == bool
        assert success

    async def test_bootstrap_lazy(
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
                lambda: {"started": "1", "key_inserted": "0"},
            ),
        )

        bootstrap = await rpc.boostrap_lazy(
            hash="FF0144381CFF0B2C079A115E7ADA7E96F43FD219446E7524C48D1CC9900C4F17"
        )

        assert type(bootstrap) == LazyBootstrapInfo

    async def test_chain(
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
                    "blocks": [
                        "000D1BAEC8EC208142C99059B393051BAC8380F9B5A2E6B2489A277D81789F3F"
                    ]
                },
            ),
        )

        chain = await rpc.chain(
            block="000D1BAEC8EC208142C99059B393051BAC8380F9B5A2E6B2489A277D81789F3F",
            count=1,
        )

        assert type(chain) == list
        assert len(chain) == 1

    async def test_confirmation_active(
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
                    "confirmations": [
                        "8031B600827C5CC05FDC911C28BBAC12A0E096CCB30FA8324F56C123676281B28031B600827C5CC05FDC911C28BBAC12A0E096CCB30FA8324F56C123676281B2"
                    ],
                    "unconfirmed": "133",
                    "confirmed": "5",
                },
            ),
        )

        active = await rpc.confirmation_active()

        assert type(active) == ActiveConfirmationInfo

    async def test_confirmation_info(
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
                    "announcements": "2",
                    "voters": "29",
                    "last_winner": "B94C505029F04BC057A0486ADA8BD07981B4A8736AE6581F2E98C6D18498146F",
                    "total_tally": "51145880360832646375807054724596663794",
                    "blocks": {
                        "B94C505029F04BC057A0486ADA8BD07981B4A8736AE6581F2E98C6D18498146F": {
                            "tally": "51145880360832646375807054724596663794",
                            "contents": {
                                "type": "state",
                                "account": "nano_3fihmbtuod33s4nrbqfczhk9zy9ddqimwjshzg4c3857es8c9631i5rg6h9p",
                                "previous": "EE125B1B1D85D3C24636B3590E1642D9F21B166C0C6CD99C9C6087A1224A0C44",
                                "representative": "nano_3o7uzba8b9e1wqu5ziwpruteyrs3scyqr761x7ke6w1xctohxfh5du75qgaj",
                                "balance": "218195000000000000000000000000",
                                "link": "0000000000000000000000000000000000000000000000000000000000000000",
                                "link_as_account": "nano_1111111111111111111111111111111111111111111111111111hifc8npp",
                                "signature": "B1BD285235C612C5A141FA61793D7C6C762D3F104A85102DED5FBD6B4514971C4D044ACD3EC8C06A9495D8E83B6941B54F8DABA825ADF799412ED9E2C86D7A0C",
                                "work": "05bb28cd8acbe71d",
                            },
                        }
                    },
                },
            ),
        )

        info = await rpc.confirmation_info(
            root="EE125B1B1D85D3C24636B3590E1642D9F21B166C0C6CD99C9C6087A1224A0C44EE125B1B1D85D3C24636B3590E1642D9F21B166C0C6CD99C9C6087A1224A0C44"
        )

        assert type(info) == ConfirmationInfo

        monkeypatch.setattr(
            rpc,
            "_post",
            lambda _: event_loop.run_in_executor(
                None,
                lambda: {
                    "announcements": "5",
                    "last_winner": "B94C505029F04BC057A0486ADA8BD07981B4A8736AE6581F2E98C6D18498146F",
                    "total_tally": "51145880360792646375807054724596663794",
                    "blocks": {
                        "B94C505029F04BC057A0486ADA8BD07981B4A8736AE6581F2E98C6D18498146F": {
                            "tally": "51145880360792646375807054724596663794",
                            "contents": {
                                "type": "state",
                                "account": "nano_3fihmbtuod33s4nrbqfczhk9zy9ddqimwjshzg4c3857es8c9631i5rg6h9p",
                                "previous": "EE125B1B1D85D3C24636B3590E1642D9F21B166C0C6CD99C9C6087A1224A0C44",
                                "representative": "nano_3o7uzba8b9e1wqu5ziwpruteyrs3scyqr761x7ke6w1xctohxfh5du75qgaj",
                                "balance": "218195000000000000000000000000",
                                "link": "0000000000000000000000000000000000000000000000000000000000000000",
                                "link_as_account": "nano_1111111111111111111111111111111111111111111111111111hifc8npp",
                                "signature": "B1BD285235C612C5A141FA61793D7C6C762D3F104A85102DED5FBD6B4514971C4D044ACD3EC8C06A9495D8E83B6941B54F8DABA825ADF799412ED9E2C86D7A0C",
                                "work": "05bb28cd8acbe71d",
                            },
                            "representatives": {
                                "nano_3pczxuorp48td8645bs3m6c3xotxd3idskrenmi65rbrga5zmkemzhwkaznh": "12617828599372664613607727105312358589",
                                "nano_1stofnrxuz3cai7ze75o174bpm7scwj9jn3nxsn8ntzg784jf1gzn1jjdkou": "5953738757270291536911559258663615240",
                                "nano_3i4n5n6c6xssapbdtkdoutm88c5zjmatc5tc77xyzdkpef8akid9errcpjnx": "0",
                            },
                        }
                    },
                },
            ),
        )

        info_reps = await rpc.confirmation_info(
            root="EE125B1B1D85D3C24636B3590E1642D9F21B166C0C6CD99C9C6087A1224A0C44EE125B1B1D85D3C24636B3590E1642D9F21B166C0C6CD99C9C6087A1224A0C44",
            representatives=True,
        )

        assert type(info_reps) == ConfirmationInfo

    async def test_confirmation_quorum(
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
                    "quorum_delta": "41469707173777717318245825935516662250",
                    "online_weight_quorum_percent": "50",
                    "online_weight_minimum": "60000000000000000000000000000000000000",
                    "online_stake_total": "82939414347555434636491651871033324568",
                    "peers_stake_total": "69026910610720098597176027400951402360",
                    "trended_stake_total": "81939414347555434636491651871033324568",
                },
            ),
        )

        quorum = await rpc.confirmation_quorum()

        assert type(quorum) == ConfirmationQuorum

        monkeypatch.setattr(
            rpc,
            "_post",
            lambda _: event_loop.run_in_executor(
                None,
                lambda: {
                    "quorum_delta": "72883202941089350521211987478946026772",
                    "online_weight_quorum_percent": "67",
                    "online_weight_minimum": "60000000000000000000000000000000000000",
                    "online_stake_total": "108780899912073657494346249968576159362",
                    "trended_stake_total": "107711392161873952087484850350074070174",
                    "peers_stake_total": "91140318106484507609300652139423401228",
                    "peers": [
                        {
                            "account": "nano_1b9wguhh39at8qtm93oghd6r4f4ubk7zmqc9oi5ape6yyz4s1gamuwn3jjit",
                            "ip": "[::ffff:77.68.124.26]:7075",
                            "weight": "16061261113176471788638724125600000000",
                        },
                    ],
                },
            ),
        )

        quorum_peers = await rpc.confirmation_quorum(peer_details=True)
        assert type(quorum_peers) == ConfirmationQuorum

    async def test_delegators(
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
                    "delegators": {
                        "nano_13bqhi1cdqq8yb9szneoc38qk899d58i5rcrgdk5mkdm86hekpoez3zxw5sd": "500000000000000000000000000000000000",
                        "nano_17k6ug685154an8gri9whhe5kb5z1mf5w6y39gokc1657sh95fegm8ht1zpn": "961647970820730000000000000000000000",
                    }
                },
            ),
        )

        delegators = await rpc.delegators(
            account="nano_1111111111111111111111111111111111111111111111111117353trpda"
        )

        assert type(delegators) == dict

        for account, balance in delegators.items():
            assert type(account) == str
            assert type(balance) == int

    async def test_delegators_count(
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
                lambda: {"count": "2"},
            ),
        )

        count = await rpc.delegators_count(
            account="nano_1111111111111111111111111111111111111111111111111117353trpda"
        )

        assert type(count) == int
        assert count == 2

    async def test_deterministic_key(
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
                    "private": "9F0E444C69F77A49BD0BE89DB92C38FE713E0963165CCA12FAF5712D7657120F",
                    "public": "C008B814A7D269A1FA3C6528B19201A24D797912DB9996FF02A1FF356E45552B",
                    "account": "nano_3i1aq1cchnmbn9x5rsbap8b15akfh7wj7pwskuzi7ahz8oq6cobd99d4r3b7",
                },
            ),
        )

        keypair = await rpc.deterministic_key(
            seed="0000000000000000000000000000000000000000000000000000000000000000",
            index=0,
        )

        assert type(keypair) == DeterministicKeypair

    async def test_frontier_count(
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
                lambda: {"count": "920471"},
            ),
        )

        count = await rpc.frontier_count()

        assert type(count) == int
        assert count == 920471

    async def test_frontiers(
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
                    "frontiers": {
                        "nano_3e3j5tkog48pnny9dmfzj1r16pg8t1e76dz5tmac6iq689wyjfpi00000000": "000D1BAEC8EC208142C99059B393051BAC8380F9B5A2E6B2489A277D81789F3F"
                    }
                },
            ),
        )

        frontiers = await rpc.frontiers(
            account="nano_1111111111111111111111111111111111111111111111111111hifc8npp",
            count=1,
        )

        assert type(frontiers) == dict
        for _, hash in frontiers.items():
            assert type(hash) == str

    async def test_keepalive(
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
                lambda: {"started": "1"},
            ),
        )

        keepalive = await rpc.keepalive(address="::ffff:192.169.0.1", port="1024")

        assert type(keepalive) == bool
        assert keepalive
