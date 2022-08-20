from typing import Any, Literal, Optional, overload
from urllib.parse import urlsplit, urlunsplit

import aiohttp
from pydantic import parse_obj_as

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
    Keypair,
    LazyBootstrapInfo,
    LedgerInfo,
    PeerInfo,
    Receivable,
    Representative,
    SignedBlock,
    Telemetry,
    UncheckedBlock,
    ValidationInfo,
    VersionInfo,
    WorkInfo,
)


class RPCException(Exception):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(kwargs.get("message"))


class Client:
    _base_path: str

    def __init__(
        self,
        uri: str = "http://localhost:7076",
        **args: Any,
    ) -> None:
        parsed = urlsplit(uri)
        self._base_path = parsed.path
        self.client = aiohttp.ClientSession(urlunsplit(parsed[:2] + ("",) * 3), **args)

    async def _post(self, data: Any) -> dict[str, Any]:
        async with self.client.post(f"{self._base_path}/", json=data) as res:
            return await res.json()

    async def call(self, action: str, **kwargs: Any) -> dict[str, Any]:
        res = await self._post({"action": action, **kwargs})

        if err := res.get("error"):
            raise RPCException(message=err)

        return res

    async def account_balance(self, account: str, **kwargs: Any) -> AccountBalances:
        """
        Returns how many RAW is owned and how many have not yet been received by account
        https://docs.nano.org/commands/rpc-protocol/#account_balance
        """

        kwargs["account"] = account

        res = await self.call("account_balance", **kwargs)
        return parse_obj_as(AccountBalances, res)

    async def account_block_count(self, account: str, **kwargs: Any) -> int:
        """
        Get number of blocks for a specific account
        https://docs.nano.org/commands/rpc-protocol/#account_block_count
        """

        kwargs["account"] = account

        res = await self.call("account_block_count", **kwargs)
        return int(res.get("block_count", 0))

    async def account_get(self, key: str, **kwargs: Any) -> str:
        """
        Get account number for the public key
        https://docs.nano.org/commands/rpc-protocol/#account_get
        """

        kwargs["key"] = key

        res = await self.call("account_get", **kwargs)
        return res.get("account", "")

    async def account_history(
        self, account: str, count: int = -1, **kwargs: Any
    ) -> AccountHistory:
        """
        Reports send/receive information for an account
        https://docs.nano.org/commands/rpc-protocol/#account_history
        """

        kwargs["account"] = account
        kwargs["count"] = count

        res = await self.call("account_history", **kwargs)
        return parse_obj_as(AccountHistory, res)

    async def account_info(self, account: str, **kwargs: Any) -> Optional[AccountInfo]:
        """
        Returns frontier, open block, change representative block, balance, last
        modified timestamp from local database & block count for account.
        https://docs.nano.org/commands/rpc-protocol/#account_info
        """

        kwargs["account"] = account

        try:
            res = await self.call("account_info", **kwargs)
            return parse_obj_as(AccountInfo, res)
        except RPCException:
            return None

    async def account_key(self, account: str, **kwargs: Any) -> str:
        """
        Get the public key for account
        https://docs.nano.org/commands/rpc-protocol/#account_key
        """

        kwargs["account"] = account

        res = await self.call("account_key", **kwargs)
        return res.get("key", "")

    async def account_representative(self, account: str, **kwargs: Any) -> str:
        """
        Returns the representative for account
        https://docs.nano.org/commands/rpc-protocol/#account_representative
        """

        kwargs["account"] = account

        res = await self.call("account_representative", **kwargs)
        return res.get("representative", "")

    async def account_weight(self, account: str, **kwargs: Any) -> int:
        """
        Returns the voting weight for account
        https://docs.nano.org/commands/rpc-protocol/#account_weight
        """

        kwargs["account"] = account

        res = await self.call("account_weight", **kwargs)
        return int(res.get("weight", 0))

    async def accounts_balances(
        self, accounts: list[str], **kwargs: Any
    ) -> dict[str, AccountBalances]:
        """
        Returns how many RAW is owned and how many have not yet been received by
        accounts list
        https://docs.nano.org/commands/rpc-protocol/#accounts_balances
        """

        kwargs["accounts"] = accounts

        res = await self.call("accounts_balances", **kwargs)

        return parse_obj_as(dict[str, AccountBalances], res.get("balances", {}))

    async def accounts_frontiers(
        self, accounts: list[str], **kwargs: Any
    ) -> dict[str, str]:
        """
        Returns a list of pairs of account and block hash representing the head block
        for accounts list
        https://docs.nano.org/commands/rpc-protocol/#accounts_frontiers
        """

        kwargs["accounts"] = accounts

        res = await self.call("accounts_frontiers", **kwargs)
        return res.get("frontiers", {})

    @overload
    async def accounts_pending(  # type: ignore[misc]
        self,
        accounts: list[str],
        *,
        threshold: Optional[Literal[0]] = None,
        source: Optional[Literal[False]] = None,
        **kwargs: Any,
    ) -> dict[str, list[str]]:
        ...

    @overload
    async def accounts_pending(
        self,
        accounts: list[str],
        *,
        threshold: int,
        source: Optional[Literal[False]] = None,
        **kwargs: Any,
    ) -> dict[str, dict[str, int]]:
        ...

    @overload
    async def accounts_pending(
        self,
        accounts: list[str],
        *,
        threshold: Optional[int] = None,
        source: Literal[True],
        **kwargs: Any,
    ) -> dict[str, dict[str, AccountPendingInfo]]:
        ...

    async def accounts_pending(
        self,
        accounts: list[str],
        *,
        threshold: Optional[int] = None,
        source: Optional[bool] = None,
        **kwargs: Any,
    ):
        """
        Returns a list of confirmed block hashes which have not yet been received by
        these accounts
        https://docs.nano.org/commands/rpc-protocol/#accounts_pending
        """

        kwargs["accounts"] = accounts
        if threshold:
            kwargs["threshold"] = threshold
        if source:
            kwargs["source"] = source

        res = await self.call("accounts_pending", **kwargs)
        blocks = dict[str, Any](res.get("blocks", {}))

        if source:
            return parse_obj_as(dict[str, dict[str, AccountPendingInfo]], blocks)
        if threshold:
            return parse_obj_as(dict[str, dict[str, int]], blocks)

        return parse_obj_as(dict[str, list[str]], blocks)

    async def accounts_representatives(
        self, accounts: list[str], **kwargs: Any
    ) -> dict[str, str]:
        """
        Returns the representatives for given accounts
        https://docs.nano.org/commands/rpc-protocol/#accounts_representatives
        """

        kwargs["accounts"] = accounts

        res = await self.call("accounts_representatives", **kwargs)
        return res.get("representatives", {})

    async def available_supply(self, **kwargs: Any) -> int:
        """
        Returns how many raw are in the public supply
        https://docs.nano.org/commands/rpc-protocol/#available_supply
        """

        res = await self.call("available_supply", **kwargs)
        return int(res.get("available", 0))

    async def block_account(self, hash: str, **kwargs: Any) -> str:
        """
        Returns the account containing block
        https://docs.nano.org/commands/rpc-protocol/#block_account
        """

        kwargs["hash"] = hash

        res = await self.call("block_account", **kwargs)
        return res.get("account", "")

    async def block_confirm(self, hash: str, **kwargs: Any) -> bool:
        """
        Request confirmation for block from known online representative nodes.
        Check results with [confirmation history](https://docs.nano.org/commands/rpc-protocol/#confirmation_history).
        https://docs.nano.org/commands/rpc-protocol/#block_confirm
        """

        kwargs["hash"] = hash

        res = await self.call("block_confirm", **kwargs)
        return bool(res.get("started"))

    async def block_count(self, **kwargs: Any) -> BlockCounts:
        """
        Reports the number of blocks in the ledger and unchecked synchronizing blocks
        https://docs.nano.org/commands/rpc-protocol/#block_count
        """

        kwargs["hash"] = hash

        res = await self.call("block_count", **kwargs)
        return parse_obj_as(BlockCounts, res)

    @overload
    async def block_create(
        self,
        balance: int,
        representative: str,
        previous: str,
        link: str,
        *,
        key: str,
        **kwargs: Any,
    ) -> SignedBlock:
        ...

    @overload
    async def block_create(
        self,
        balance: int,
        representative: str,
        previous: str,
        link: str,
        *,
        wallet: str,
        account: str,
        **kwargs: Any,
    ) -> SignedBlock:
        ...

    async def block_create(
        self, balance: int, representative: str, previous: str, link: str, **kwargs: Any
    ) -> SignedBlock:
        """
        Creates a json representations of new block based on input data & signed with
        private key or account in wallet. Use for offline signing.
        https://docs.nano.org/commands/rpc-protocol/#block_count
        """

        kwargs["balance"] = balance
        kwargs["representative"] = representative
        kwargs["previous"] = previous
        kwargs["link"] = link
        kwargs["json_block"] = True
        kwargs["type"] = "state"

        res = await self.call("block_create", **kwargs)
        return parse_obj_as(SignedBlock, res)

    async def block_hash(self, block: Any, **kwargs: Any) -> str:
        """
        Returning block hash for given block content.
        https://docs.nano.org/commands/rpc-protocol/#block_hash
        """

        kwargs["json_block"] = True
        kwargs["block"] = dict(block)

        res = await self.call("block_hash", **kwargs)
        return res.get("hash", "")

    async def block_info(self, hash: str, **kwargs: Any) -> BlockInfo:
        """
        Retrieves a json representation of the block in contents
        https://docs.nano.org/commands/rpc-protocol/#block_hash
        """

        kwargs["json_block"] = True
        kwargs["hash"] = hash

        res = await self.call("block_info", **kwargs)

        return parse_obj_as(BlockInfo, res)

    async def blocks(self, hashes: list[str], **kwargs: Any) -> dict[str, Block]:
        """
        Retrieves a json representations of blocks
        https://docs.nano.org/commands/rpc-protocol/#blocks
        """

        kwargs["json_block"] = True
        kwargs["hashes"] = hashes

        res = await self.call("blocks", **kwargs)
        blocks = res.get("blocks", {})

        return parse_obj_as(dict[str, Block], blocks)

    async def blocks_info(
        self, hashes: list[str], **kwargs: Any
    ) -> dict[str, BlockInfo]:
        """
        Retrieves a json representations of blocks in contents
        https://docs.nano.org/commands/rpc-protocol/#blocks_info
        """

        kwargs["json_block"] = True
        kwargs["include_not_found"] = False
        kwargs["hashes"] = hashes

        res = await self.call("blocks_info", **kwargs)
        blocks = res.get("blocks", {})

        return parse_obj_as(dict[str, BlockInfo], blocks)

    async def bootstrap(self, address: str, port: str, **kwargs: Any) -> bool:
        """
        Initialize bootstrap to specific IP address and port. Not compatible with launch
        flag [--disable_legacy_bootstrap](https://docs.nano.org/commands/command-line-interface/#-disable_legacy_bootstrap)
        https://docs.nano.org/commands/rpc-protocol/#bootstrap
        """

        kwargs["address"] = address
        kwargs["port"] = port

        res = await self.call("bootstrap", **kwargs)

        return "success" in res

    async def bootstrap_any(self, **kwargs: Any) -> bool:
        """
        Initialize multi-connection bootstrap to random peers. Not compatible with launch
        flag [--disable_legacy_bootstrap](https://docs.nano.org/commands/command-line-interface/#-disable_legacy_bootstrap)
        https://docs.nano.org/commands/rpc-protocol/#bootstrap_any
        """

        res = await self.call("bootstrap_any", **kwargs)

        return "success" in res

    async def boostrap_lazy(self, hash: str, **kwargs: Any) -> LazyBootstrapInfo:
        """
        Initialize lazy bootstrap with given block hash. Not compatible with launch flag
        [--disable_lazy_bootstrap](https://docs.nano.org/commands/command-line-interface/#-disable_lazy_bootstrap)
        https://docs.nano.org/commands/rpc-protocol/#bootstrap_lazy
        """

        kwargs["hash"] = hash

        res = await self.call("bootstrap_lazy", **kwargs)

        return parse_obj_as(LazyBootstrapInfo, res)

    async def chain(self, block: str, count: int = -1, **kwargs: Any) -> list[str]:
        """
        Returns a consecutive list of block hashes in the account chain starting at
        block back to count (direction from frontier back to open block, from newer
        blocks to older). Will list all blocks back to the open block of this chain when
        count is set to "-1". The requested block hash is included in the answer.
        https://docs.nano.org/commands/rpc-protocol/#chain
        """

        kwargs["block"] = block
        kwargs["count"] = count

        res = await self.call("chain", **kwargs)
        return res.get("blocks", [])

    async def confirmation_active(self, **kwargs: Any) -> ActiveConfirmationInfo:
        """
        Returns list of active elections qualified roots (excluding stopped & aborted
        elections); since V21, also includes the number of unconfirmed and confirmed
        active elections. Find info about specific qualified root with
        [confirmation_info](https://docs.nano.org/commands/rpc-protocol/#confirmation_info)
        https://docs.nano.org/commands/rpc-protocol/#confirmation_active
        """

        res = await self.call("confirmation_active", **kwargs)

        return parse_obj_as(ActiveConfirmationInfo, res)

    async def confirmation_info(self, root: str, **kwargs: Any) -> ConfirmationInfo:
        """
        Returns info about an unconfirmed active election by root.
        Including announcements count, last winner (initially local ledger block),
        total tally of voted representatives, concurrent blocks with tally & block
        contents for each.
        https://docs.nano.org/commands/rpc-protocol/#confirmation_info
        """

        kwargs["json_block"] = True
        kwargs["root"] = root

        res = await self.call("confirmation_info", **kwargs)
        return parse_obj_as(ConfirmationInfo, res)

    async def confirmation_quorum(self, **kwargs: Any) -> ConfirmationQuorum:
        """
        Returns information about node elections settings & observed network state
        https://docs.nano.org/commands/rpc-protocol/#confirmation_quorum
        """

        res = await self.call("confirmation_quorum", **kwargs)
        return parse_obj_as(ConfirmationQuorum, res)

    async def delegators(self, account: str, **kwargs: Any) -> dict[str, int]:
        """
        Returns a list of pairs of delegator accounts and balances given a
        representative account
        https://docs.nano.org/commands/rpc-protocol/#delegators
        """

        kwargs["account"] = account

        res = await self.call("delegators", **kwargs)
        delegators = res.get("delegators", {})

        return parse_obj_as(dict[str, int], delegators)

    async def delegators_count(self, account: str, **kwargs: Any) -> int:
        """
        Get number of delegators for a specific representative account
        https://docs.nano.org/commands/rpc-protocol/#delegators_count
        """

        kwargs["account"] = account

        res = await self.call("delegators_count", **kwargs)
        return int(res.get("count", 0))

    async def deterministic_key(self, seed: str, index: int, **kwargs) -> Keypair:
        """
        Derive deterministic keypair from seed based on index
        https://docs.nano.org/commands/rpc-protocol/#deterministic_key
        """

        kwargs["seed"] = seed
        kwargs["index"] = index

        res = await self.call("deterministic_key", **kwargs)
        return parse_obj_as(Keypair, res)

    async def frontier_count(self, **kwargs: Any) -> int:
        """
        Reports the number of accounts in the ledger
        https://docs.nano.org/commands/rpc-protocol/#frontier_count
        """

        res = await self.call("frontier_count", **kwargs)
        return int(res.get("count", 0))

    async def frontiers(
        self, account: str, count: int = 1, **kwargs: Any
    ) -> dict[str, str]:
        """
        Returns a list of pairs of account and block hash representing the head block
        starting at account up to count
        https://docs.nano.org/commands/rpc-protocol/#frontiers
        """

        kwargs["account"] = account
        kwargs["count"] = count

        res = await self.call("frontiers", **kwargs)
        return res.get("frontiers", {})

    async def keepalive(self, address: str, port: str | int, **kwargs: Any) -> bool:
        """
        Tells the node to send a keepalive packet to address:port
        https://docs.nano.org/commands/rpc-protocol/#keepalive
        """

        kwargs["address"] = address
        kwargs["port"] = port

        res = await self.call("keepalive", **kwargs)
        return bool(res.get("started"))

    async def key_create(self, **kwargs: Any) -> Keypair:
        """
        Derive deterministic keypair from seed based on index
        https://docs.nano.org/commands/rpc-protocol/#key_create
        """

        res = await self.call("key_create", **kwargs)
        return Keypair(**res)

    async def key_expand(self, key: str, **kwargs: Any) -> Keypair:
        """
        Derive public key and account number from private key
        https://docs.nano.org/commands/rpc-protocol/#key_expand
        """

        kwargs["key"] = key

        res = await self.call("key_expand", **kwargs)
        return Keypair(**res)

    async def ledger(
        self, account: str, count: int = 1, **kwargs
    ) -> dict[str, LedgerInfo]:
        """
        Returns frontier, open block, change representative block, balance,
        last modified timestamp from local database & block count starting at account up to count
        https://docs.nano.org/commands/rpc-protocol/#ledger
        """

        kwargs["account"] = account
        kwargs["count"] = count

        res = await self.call("ledger", **kwargs)
        accounts = res.get("accounts", {})

        return parse_obj_as(dict[str, LedgerInfo], accounts)

    @overload
    async def peers(
        self, peer_details: Literal[True], **kwargs: Any
    ) -> dict[str, PeerInfo]:
        ...

    @overload
    async def peers(
        self, peer_details: Optional[Literal[False]] = None, **kwargs
    ) -> dict[str, int]:
        ...

    async def peers(self, peer_details: Optional[bool] = None, **kwargs):
        """
        Returns a list of pairs of online peer IPv6:port and its node protocol network version
        https://docs.nano.org/commands/rpc-protocol/#peers
        """

        if peer_details:
            kwargs["peer_details"] = peer_details

        res = await self.call("peers", **kwargs)
        peers = dict[str, Any](res.get("peers", {}))

        if peer_details:
            return parse_obj_as(dict[str, PeerInfo], peers)

        return parse_obj_as(dict[str, int], peers)

    @overload
    async def process(
        self,
        block: Any,
        sync: Optional[Literal[True]] = True,
        *,
        subtype: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        ...

    @overload
    async def process(
        self,
        block: Any,
        sync: Literal[False],
        *,
        subtype: Optional[str] = None,
        **kwargs: Any,
    ) -> bool:
        ...

    async def process(
        self,
        block: Any,
        sync: Optional[bool] = True,
        *,
        subtype: Optional[str] = None,
        **kwargs: Any,
    ):
        """
        Publish block to the network.
        https://docs.nano.org/commands/rpc-protocol/#process
        """

        kwargs["json_block"] = True
        kwargs["block"] = dict(block)

        if not sync:
            kwargs["async"] = True
        if subtype:
            kwargs["subtype"] = subtype

        res = await self.call("process", **kwargs)

        if not sync:
            return bool(res.get("started"))
        return res.get("hash")

    @overload
    async def receivable(  # type: ignore[misc]
        self,
        account: str,
        *,
        threshold: Optional[Literal[0]] = None,
        source: Optional[Literal[False]] = None,
        **kwargs,
    ) -> list[str]:
        ...

    @overload
    async def receivable(
        self,
        account: str,
        *,
        threshold: Optional[int] = None,
        source: Literal[True],
        **kwargs,
    ) -> dict[str, Receivable]:
        ...

    @overload
    async def receivable(
        self,
        account: str,
        *,
        threshold: int,
        source: Optional[Literal[False]] = None,
        **kwargs,
    ) -> dict[str, int]:
        ...

    async def receivable(
        self,
        account: str,
        *,
        threshold: Optional[int] = None,
        source: Optional[bool] = None,
        **kwargs,
    ):
        """
        Returns a list of block hashes which have not yet been received by this account.
        https://docs.nano.org/commands/rpc-protocol/#receivable
        """

        kwargs["account"] = account
        if threshold:
            kwargs["threshold"] = threshold
        if source:
            kwargs["source"] = source

        res = await self.call("receivable", **kwargs)

        blocks = res.get("blocks")

        if source:
            return parse_obj_as(dict[str, Receivable], blocks or {})
        if threshold:
            return parse_obj_as(dict[str, int], blocks or {})

        return parse_obj_as(list[str], blocks or [])

    async def receivable_exists(self, hash: str, **kwargs: Any) -> bool:
        """
        Check whether block is receivable by hash
        https://docs.nano.org/commands/rpc-protocol/#receivable_exists
        """

        kwargs["hash"] = hash

        res = await self.call("receivable_exists", **kwargs)
        return bool(res.get("exists"))

    async def representatives(self, **kwargs: Any) -> dict[str, int]:
        """
        Returns a list of pairs of representative and its voting weight
        https://docs.nano.org/commands/rpc-protocol/#representatives
        """

        res = await self.call("representatives", **kwargs)
        return parse_obj_as(dict[str, int], res.get("representatives", {}))

    @overload
    async def representatives_online(
        self, weight: Literal[True], **kwargs: Any
    ) -> dict[str, Representative]:
        ...

    @overload
    async def representatives_online(
        self, weight: Optional[Literal[False]] = False, **kwargs: Any
    ) -> list[str]:
        ...

    async def representatives_online(
        self, weight: Optional[bool] = None, **kwargs: Any
    ):
        """
        Returns a list of online representative accounts that have voted recently
        https://docs.nano.org/commands/rpc-protocol/#representatives_online
        """

        if weight:
            kwargs["weight"] = weight

        res = await self.call("representatives_online", **kwargs)
        representatives = res.get("representatives")

        if weight and representatives:
            return parse_obj_as(dict[str, Representative], representatives or {})

        return parse_obj_as(list[str], representatives or [])

    async def republish(self, hash: str, **kwargs: Any) -> list[str]:
        """
        Rebroadcast blocks starting at hash to the network
        https://docs.nano.org/commands/rpc-protocol/#republish
        """

        kwargs["hash"] = hash

        res = await self.call("republish", **kwargs)
        blocks = res.get("blocks", [])

        return parse_obj_as(list[str], blocks)

    @overload
    async def sign(
        self,
        *,
        block: Any,
        hash: None = None,
        key: str,
        account: None = None,
        wallet: None = None,
        **kwargs: Any,
    ) -> Block:
        ...

    @overload
    async def sign(
        self,
        *,
        block: None = None,
        hash: str,
        key: str,
        account: None = None,
        wallet: None = None,
        **kwargs: Any,
    ) -> str:
        ...

    @overload
    async def sign(
        self,
        *,
        block: Any,
        hash: None = None,
        key: None = None,
        account: str,
        wallet: str,
        **kwargs: Any,
    ) -> Block:
        ...

    @overload
    async def sign(
        self,
        *,
        block: None = None,
        hash: str,
        key: None = None,
        account: str,
        wallet: str,
        **kwargs: Any,
    ) -> str:
        ...

    async def sign(
        self,
        *,
        block: Optional[Any] = None,
        hash: Optional[str] = None,
        key: Optional[str] = None,
        account: Optional[str] = None,
        wallet: Optional[str] = None,
        **kwargs: Any,
    ) -> str | Block:
        """
        Signing provided block with private key or key of account from wallet
        https://docs.nano.org/commands/rpc-protocol/#sign
        """

        if block:
            kwargs["json_block"] = True
            kwargs["block"] = dict(block)
        elif hash:
            kwargs["hash"] = hash
        else:
            raise RPCException

        if key:
            kwargs["key"] = key
        elif account and wallet:
            kwargs["account"] = account
            kwargs["wallet"] = wallet
        else:
            raise RPCException

        res = await self.call("sign", **kwargs)

        if block := res.get("block"):
            return parse_obj_as(Block, block)

        return str(res.get("signature", ""))

    async def stats_clear(self, **kwargs: Any) -> bool:
        """
        Clears all collected statistics. The "stat_duration_seconds" value in the
        "stats" action is also reset
        https://docs.nano.org/commands/rpc-protocol/#stats_clear
        """

        res = await self.call("stats_clear", **kwargs)
        return "success" in res

    async def stop(self, **kwargs: Any) -> bool:
        """
        Method to safely shutdown node
        https://docs.nano.org/commands/rpc-protocol/#stop
        """

        res = await self.call("stop", **kwargs)
        return "success" in res

    async def successors(self, block: str, count: int = -1, **kwargs: Any) -> list[str]:
        """
        Signing provided block with private key or key of account from wallet
        https://docs.nano.org/commands/rpc-protocol/#sign
        """

        kwargs["block"] = block
        kwargs["count"] = count

        res = await self.call("successors", **kwargs)
        return parse_obj_as(list[str], res.get("blocks", []))

    @overload
    async def telemetry(
        self,
        *,
        address: None = None,
        port: None = None,
        raw: Literal[True],
        **kwargs: Any,
    ) -> list[Telemetry]:
        ...

    @overload
    async def telemetry(
        self,
        *,
        address: str,
        port: str,
        raw: Optional[Literal[False]] = None,
        **kwargs: Any,
    ) -> Telemetry:
        ...

    @overload
    async def telemetry(
        self,
        *,
        address: None = None,
        port: None = None,
        raw: Optional[Literal[False]] = None,
        **kwargs: Any,
    ) -> Telemetry:
        ...

    async def telemetry(
        self,
        *,
        address: Optional[str] = None,
        port: Optional[str] = None,
        raw: Optional[bool] = None,
        **kwargs,
    ):
        """
        Return metrics from other nodes on the network. By default, returns a summarized
        view of the whole network. See below for details on obtaining local telemetry data.
        https://docs.nano.org/commands/rpc-protocol/#telemetry
        """

        if raw:
            kwargs["raw"] = raw
        if address and port:
            kwargs["address"] = address
            kwargs["port"] = port

        res = await self.call("telemetry", **kwargs)

        if not (address and port) and raw:
            return parse_obj_as(list[Telemetry], res.get("metrics", []))

        return parse_obj_as(Telemetry, res)

    async def validate_account_number(self, account: str, **kwargs: Any) -> bool:
        """
        Check whether account is a valid account number using checksum
        https://docs.nano.org/commands/rpc-protocol/#validate_account_number
        """

        kwargs["account"] = account

        res = await self.call("validate_account_number", **kwargs)

        return bool(res.get("valid"))

    async def version(self, **kwargs: Any) -> VersionInfo:
        """
        Returns version information for RPC, Store, Protocol (network),
        Node (Major & Minor version)
        https://docs.nano.org/commands/rpc-protocol/#version
        """

        res = await self.call("version", **kwargs)

        return parse_obj_as(VersionInfo, res)

    async def unchecked(self, count: Optional[int], **kwargs: Any) -> dict[str, Block]:
        """
        Returns a list of pairs of unchecked block hashes and their json representation
        up to count
        https://docs.nano.org/commands/rpc-protocol/#unchecked
        """

        kwargs["json_block"] = True

        if count:
            kwargs["count"] = count

        res = await self.call("unchecked", **kwargs)
        blocks = res.get("blocks")

        return parse_obj_as(dict[str, Block], blocks if blocks else [])

    async def unchecked_clear(self, **kwargs: Any) -> bool:
        """
        Clear unchecked synchronizing blocks
        https://docs.nano.org/commands/rpc-protocol/#unchecked_clear
        """

        res = await self.call("unchecked_clear", **kwargs)

        return "success" in res

    async def unchecked_get(self, hash: str, **kwargs: Any) -> Block:
        """
        Retrieves a json representation of unchecked synchronizing block by hash
        https://docs.nano.org/commands/rpc-protocol/#unchecked_get
        """

        kwargs["json_block"] = True
        kwargs["hash"] = hash

        res = await self.call("unchecked_get", **kwargs)

        return parse_obj_as(Block, res.get("contents"))

    async def unchecked_keys(
        self, key: str, count: Optional[int] = 1, **kwargs
    ) -> list[UncheckedBlock]:
        """
        Retrieves unchecked database keys, blocks hashes & a json representations of
        unchecked receivable blocks starting from key up to count
        https://docs.nano.org/commands/rpc-protocol/#unchecked_keys
        """

        kwargs["json_block"] = True
        kwargs["key"] = key

        if count:
            kwargs["count"] = count

        res = await self.call("unchecked_keys", **kwargs)
        unchecked = res.get("unchecked", [])

        return parse_obj_as(list[UncheckedBlock], unchecked)

    async def unopened(
        self, account: Optional[str] = None, count: Optional[int] = -1, **kwargs
    ) -> dict[str, int]:
        """
        Returns the total receivable balance for unopened accounts in the local database,
        starting at account (optional) up to count (optional), sorted by account number
        https://docs.nano.org/commands/rpc-protocol/#unopened
        """

        kwargs["json_block"] = True

        if account:
            kwargs["account"] = account

        if count:
            kwargs["count"] = count

        res = await self.call("unopened", **kwargs)
        accounts = res.get("accounts")

        return parse_obj_as(dict[str, int], accounts)

    async def uptime(self, **kwargs: Any) -> int:
        """
        Return node uptime in seconds
        https://docs.nano.org/commands/rpc-protocol/#uptime
        """

        res = await self.call("unopened", **kwargs)

        return int(res.get("seconds", 0))

    async def work_cancel(self, hash: str, **kwargs: Any) -> bool:
        """
        Stop generating work for block
        https://docs.nano.org/commands/rpc-protocol/#work_cancel
        """

        kwargs["hash"] = hash

        res = await self.call("work_cancel", **kwargs)

        return "success" in res

    async def work_generate(self, hash: str, **kwargs: Any) -> WorkInfo:
        """
        Generates work for block. hash is the frontier of the account or in the case of
        an open block, the public key representation of the account which can be found
        with [account_key](https://docs.nano.org/commands/rpc-protocol/#account_key)
        https://docs.nano.org/commands/rpc-protocol/#work_generate
        """

        kwargs["hash"] = hash

        res = await self.call("work_generate", **kwargs)

        return parse_obj_as(WorkInfo, res)

    async def work_peer_add(self, address: str, port: str | int, **kwargs: Any) -> bool:
        """
        Add specific IP address and port as work peer for node until restart
        https://docs.nano.org/commands/rpc-protocol/#work_peer_add
        """

        kwargs["address"] = address
        kwargs["port"] = port

        res = await self.call("work_peer_add", **kwargs)

        return "success" in res

    async def work_peers(self, **kwargs: Any) -> list[str]:
        """
        https://docs.nano.org/commands/rpc-protocol/#work_peers
        """

        res = await self.call("work_peers", **kwargs)

        peers = res.get("work_peers") or []

        return parse_obj_as(list[str], peers)

    async def work_peers_clear(self, **kwargs: Any) -> bool:
        """
        Clear work peers node list until restart
        https://docs.nano.org/commands/rpc-protocol/#work_peers_clear
        """

        res = await self.call("work_peers_clear", **kwargs)
        return "success" in res

    async def work_validate(
        self, work: str, hash: str, **kwargs: Any
    ) -> ValidationInfo:
        """
        Check whether work is valid for block
        https://docs.nano.org/commands/rpc-protocol/#work_validate
        """

        kwargs["work"] = work
        kwargs["hash"] = hash

        res = await self.call("work_validate", **kwargs)
        return ValidationInfo(**res)

    async def nano_to_raw(self, amount: int):
        """
        Convert nano amount (10^30 raw) into raw (10^0)
        https://docs.nano.org/commands/rpc-protocol/#nano_to_raw
        """

        res = await self.call("nano_to_raw", amount=amount)
        return int(res.get("amount", 0))

    async def raw_to_nano(self, amount: int):
        """
        Convert raw amount (10^0) into nano (10^30 raw)
        https://docs.nano.org/commands/rpc-protocol/#raw_to_nano
        """

        res = await self.call("raw_to_nano", amount=amount)
        return int(res.get("amount", 0))
