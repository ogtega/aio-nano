from typing import Any, Literal, Optional, overload
from urllib.parse import urlsplit, urlunsplit

import aiohttp
from pydantic import parse_obj_as

from aio_nano.rpc.models import (
    AccountBalance,
    AccountHistory,
    AccountInfo,
    AccountPendingInfo,
    ActiveConfirmations,
    Block,
    BlockCount,
    BlockInfo,
    BlocksInfo,
    ConfirmationInfo,
    ConfirmationQuorum,
    DeterministicKeypair,
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

        if res.get("error"):
            raise

        return res

    async def account_balance(self, account: str, **kwargs: Any) -> AccountBalance:
        """
        Returns how many RAW is owned and how many have not yet been received by account
        https://docs.nano.org/commands/rpc-protocol/#account_balance
        """

        kwargs["account"] = account

        res = await self.call("account_balance", **kwargs)
        return AccountBalance(**res)

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
        return AccountHistory(**res)

    async def account_info(self, account: str, **kwargs: Any) -> AccountInfo:
        """
        Returns frontier, open block, change representative block, balance, last
        modified timestamp from local database & block count for account.
        https://docs.nano.org/commands/rpc-protocol/#account_info
        """

        kwargs["account"] = account

        res = await self.call("account_info", **kwargs)
        return AccountInfo(**res)

    async def account_key(self, account: str, **kwargs) -> str:
        """
        Get the public key for account
        https://docs.nano.org/commands/rpc-protocol/#account_key
        """

        kwargs["account"] = account

        res = await self.call("account_key", **kwargs)
        return res.get("key", "")

    async def account_representative(self, account: str, **kwargs) -> str:
        """
        Returns the representative for account
        https://docs.nano.org/commands/rpc-protocol/#account_representative
        """

        kwargs["account"] = account

        res = await self.call("account_representative", **kwargs)
        return res.get("representative", "")

    async def account_weight(self, account: str, **kwargs) -> int:
        """
        Returns the voting weight for account
        https://docs.nano.org/commands/rpc-protocol/#account_weight
        """

        kwargs["account"] = account

        res = await self.call("account_weight", **kwargs)
        return int(res.get("weight", 0))

    async def accounts_balances(
        self, accounts: list[str], **kwargs
    ) -> dict[str, AccountBalance]:
        """
        Returns how many RAW is owned and how many have not yet been received by
        accounts list
        https://docs.nano.org/commands/rpc-protocol/#accounts_balances
        """

        kwargs["accounts"] = accounts

        res = await self.call("accounts_balances", **kwargs)
        return {
            k: AccountBalance(**v) for (k, v) in dict(res.get("balances", {})).items()
        }

    async def accounts_frontiers(self, accounts: list[str], **kwargs) -> dict[str, str]:
        """
        Returns a list of pairs of account and block hash representing the head block
        for accounts list
        https://docs.nano.org/commands/rpc-protocol/#accounts_frontiers
        """

        kwargs["accounts"] = accounts

        res = await self.call("accounts_frontiers", **kwargs)
        return res.get("frontiers", {})

    @overload
    async def accounts_pending(
        self,
        accounts: list[str],
        threshold: None,
        source: Optional[Literal[False]],
        **kwargs,
    ) -> dict[str, list[str]]:
        ...

    @overload
    async def accounts_pending(
        self,
        accounts: list[str],
        threshold: int,
        source: Optional[Literal[False]],
        **kwargs,
    ) -> dict[str, dict[str, int]]:
        ...

    @overload
    async def accounts_pending(
        self,
        accounts: list[str],
        threshold: Optional[int],
        source: Literal[True],
        **kwargs,
    ) -> dict[str, dict[str, AccountPendingInfo]]:
        ...

    async def accounts_pending(
        self,
        accounts: list[str],
        threshold: Optional[int] = None,
        source: Optional[bool] = None,
        **kwargs,
    ):  # TODO: Fix return type hint for cases where threshold is a 0 literal
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
            return {
                k: {
                    str(block): AccountPendingInfo(**item)
                    for block, item in dict(v).items()
                }
                for k, v in blocks.items()
            }
        if threshold:
            return {
                k: {str(block): int(amount) for block, amount in dict(v).items()}
                for k, v in blocks.items()
            }

        return dict[str, list[str]](blocks)

    async def accounts_representatives(
        self, accounts: list[str], **kwargs
    ) -> dict[str, str]:
        """
        Returns the representatives for given accounts
        https://docs.nano.org/commands/rpc-protocol/#accounts_representatives
        """

        kwargs["accounts"] = accounts

        res = await self.call("accounts_representatives", **kwargs)
        return res.get("representatives", {})

    async def available_supply(self, **kwargs) -> int:
        """
        Returns how many raw are in the public supply
        https://docs.nano.org/commands/rpc-protocol/#available_supply
        """

        res = await self.call("available_supply", **kwargs)
        return int(res.get("available", 0))

    async def block_account(self, hash: str, **kwargs) -> str:
        """
        Returns the account containing block
        https://docs.nano.org/commands/rpc-protocol/#block_account
        """

        kwargs["hash"] = hash

        res = await self.call("block_account", **kwargs)
        return res.get("account", "")

    async def block_confirm(self, hash: str, **kwargs) -> bool:
        """
        Request confirmation for block from known online representative nodes.
        Check results with [confirmation history](https://docs.nano.org/commands/rpc-protocol/#confirmation_history).
        https://docs.nano.org/commands/rpc-protocol/#block_confirm
        """

        kwargs["hash"] = hash

        res = await self.call("block_confirm", **kwargs)
        return bool(res.get("started"))

    async def block_count(self, **kwargs) -> BlockCount:
        """
        Reports the number of blocks in the ledger and unchecked synchronizing blocks
        https://docs.nano.org/commands/rpc-protocol/#block_count
        """

        kwargs["hash"] = hash

        res = await self.call("block_count", **kwargs)
        return BlockCount(**res)

    async def block_create(
        self, balance: int, representative: str, previous: str, **kwargs
    ) -> SignedBlock:
        """
        Creates a json representations of new block based on input data & signed with
        private key or account in wallet. Use for offline signing.
        https://docs.nano.org/commands/rpc-protocol/#block_count
        """

        kwargs["balance"] = balance
        kwargs["representative"] = representative
        kwargs["previous"] = previous
        kwargs["json_block"] = True
        kwargs["type"] = "state"

        res = await self.call("block_create", **kwargs)
        return SignedBlock(**res)

    async def block_hash(self, block: Any, **kwargs) -> str:
        """
        Returning block hash for given block content.
        https://docs.nano.org/commands/rpc-protocol/#block_hash
        """

        kwargs["json_block"] = True
        kwargs["block"] = dict(block)

        res = await self.call("block_hash", **kwargs)
        return res.get("hash", "")

    async def block_info(self, hash: str, **kwargs) -> BlockInfo:
        """
        Retrieves a json representation of the block in contents
        https://docs.nano.org/commands/rpc-protocol/#block_hash
        """

        kwargs["json_block"] = True
        kwargs["hash"] = hash

        res = await self.call("block_info", **kwargs)

        return BlockInfo(**res)

    async def blocks(self, hashes: list[str], **kwargs) -> dict[str, Block]:
        """
        Retrieves a json representations of blocks
        https://docs.nano.org/commands/rpc-protocol/#blocks
        """

        kwargs["json_block"] = True
        kwargs["hashes"] = hashes

        res = await self.call("blocks", **kwargs)
        blocks = res.get("blocks", {})

        return {k: Block(**v) for k, v in dict(blocks).items()}

    async def blocks_info(self, hashes: list[str], **kwargs) -> BlocksInfo:
        """
        Retrieves a json representations of blocks in contents
        https://docs.nano.org/commands/rpc-protocol/#blocks_info
        """

        kwargs["json_block"] = True
        kwargs["hashes"] = hashes

        res = await self.call("blocks_info", **kwargs)

        if not res.get("blocks_not_found"):
            res["blocks_not_found"] = []

        return BlocksInfo(**res)

    async def bootstrap(self, address: str, port: str, **kwargs) -> bool:
        """
        Initialize bootstrap to specific IP address and port. Not compatible with launch
        flag [--disable_legacy_bootstrap](https://docs.nano.org/commands/command-line-interface/#-disable_legacy_bootstrap)
        https://docs.nano.org/commands/rpc-protocol/#bootstrap
        """

        kwargs["address"] = address
        kwargs["port"] = port

        res = await self.call("bootstrap", **kwargs)

        return "success" in res

    async def boostrap_lazy(self, hash: str, **kwargs) -> LazyBootstrapInfo:
        """
        Initialize lazy bootstrap with given block hash. Not compatible with launch flag
        [--disable_lazy_bootstrap](https://docs.nano.org/commands/command-line-interface/#-disable_lazy_bootstrap)
        https://docs.nano.org/commands/rpc-protocol/#bootstrap_lazy
        """

        kwargs["hash"] = hash

        res = await self.call("bootstrap_lazy", **kwargs)

        return LazyBootstrapInfo(**res)

    async def chain(self, block: str, count: int = -1, **kwargs) -> list[str]:
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

    async def confirmation_active(self, **kwargs):
        """
        Returns list of active elections qualified roots (excluding stopped & aborted
        elections); since V21, also includes the number of unconfirmed and confirmed
        active elections. Find info about specific qualified root with
        [confirmation_info](https://docs.nano.org/commands/rpc-protocol/#confirmation_info)
        https://docs.nano.org/commands/rpc-protocol/#confirmation_active
        """

        res = await self.call("confirmation_active", **kwargs)

        if not res.get("confirmations"):
            res["confirmations"] = []

        return ActiveConfirmations(**res)

    async def confirmation_info(self, root: str, **kwargs) -> ConfirmationInfo:
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
        return ConfirmationInfo(**res)

    async def confirmation_quorum(self, **kwargs) -> ConfirmationQuorum:
        """
        Returns information about node elections settings & observed network state
        https://docs.nano.org/commands/rpc-protocol/#confirmation_quorum
        """

        res = await self.call("confirmation_quorum", **kwargs)
        return ConfirmationQuorum(**res)

    async def delegators(self, account: str, **kwargs) -> dict[str, int]:
        """
        Returns a list of pairs of delegator accounts and balances given a
        representative account
        https://docs.nano.org/commands/rpc-protocol/#delegators
        """

        kwargs["account"] = account

        res = await self.call("delegators", **kwargs)
        delegators = dict[str, Any](res.get("delegators", {}))

        return {k: int(v) for k, v in delegators.items()}

    async def delegators_count(self, account: str, **kwargs) -> int:
        """
        Get number of delegators for a specific representative account
        https://docs.nano.org/commands/rpc-protocol/#delegators_count
        """

        kwargs["account"] = account

        res = await self.call("delegators_count", **kwargs)
        return int(res.get("count", 0))

    async def deterministic_key(
        self, seed: str, index: int, **kwargs
    ) -> DeterministicKeypair:
        """
        Derive deterministic keypair from seed based on index
        https://docs.nano.org/commands/rpc-protocol/#deterministic_key
        """

        kwargs["seed"] = seed
        kwargs["index"] = index

        res = await self.call("deterministic_key", **kwargs)
        return DeterministicKeypair(**res)

    async def frontier_count(self, **kwargs) -> int:
        """
        Reports the number of accounts in the ledger
        https://docs.nano.org/commands/rpc-protocol/#frontier_count
        """

        res = await self.call("frontier_count", **kwargs)
        return int(res.get("count", 0))

    async def frontiers(self, account: str, count: int = 1, **kwargs) -> dict[str, str]:
        """
        Returns a list of pairs of account and block hash representing the head block
        starting at account up to count
        https://docs.nano.org/commands/rpc-protocol/#frontiers
        """

        kwargs["account"] = account
        kwargs["count"] = count

        res = await self.call("frontiers", **kwargs)
        return res.get("frontiers", {})

    async def keepalive(self, address: str, port: str | int, **kwargs) -> bool:
        """
        Tells the node to send a keepalive packet to address:port
        https://docs.nano.org/commands/rpc-protocol/#keepalive
        """

        kwargs["address"] = address
        kwargs["port"] = port

        res = await self.call("keepalive", **kwargs)
        return bool(res.get("started"))

    async def key_create(self, **kwargs) -> DeterministicKeypair:
        """
        Derive deterministic keypair from seed based on index
        https://docs.nano.org/commands/rpc-protocol/#key_create
        """

        res = await self.call("key_create", **kwargs)
        return DeterministicKeypair(**res)

    async def key_expand(self, key: str, **kwargs) -> DeterministicKeypair:
        """
        Derive public key and account number from private key
        https://docs.nano.org/commands/rpc-protocol/#key_expand
        """

        kwargs["key"] = key

        res = await self.call("key_expand", **kwargs)
        return DeterministicKeypair(**res)

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
        accounts = dict[str, Any](res.get("accounts", {}))

        return {k: LedgerInfo(**v) for k, v in accounts.items()}

    @overload
    async def peers(self, peer_details: Literal[True], **kwargs) -> dict[str, PeerInfo]:
        ...

    @overload
    async def peers(
        self, peer_details: Optional[Literal[False]], **kwargs
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
            return {k: PeerInfo(**v) for k, v in peers.items()}

        return {k: int(v) for k, v in peers.items()}

    @overload
    async def process(
        self, subtype: str, block: Any, sync: Optional[Literal[True]], **kwargs
    ) -> str:
        ...

    @overload
    async def process(
        self, subtype: str, block: Any, sync: Literal[False], **kwargs
    ) -> bool:
        ...

    async def process(
        self, subtype: str, block: Any, sync: Optional[bool] = True, **kwargs
    ):
        """
        Publish block to the network.
        https://docs.nano.org/commands/rpc-protocol/#process
        """

        kwargs["json_block"] = True
        kwargs["subtype"] = subtype
        kwargs["block"] = dict(block)

        if not sync:
            kwargs["async"] = True

        res = await self.call("process", **kwargs)

        if not sync:
            return bool(res.get("started"))
        return str(res.get("hash"))

    @overload
    async def receivable(
        self, account: str, threshold: None, source: Optional[Literal[False]], **kwargs
    ) -> list[str]:
        ...

    @overload
    async def receivable(
        self,
        account: str,
        threshold: Optional[int],
        source: Literal[True] = True,
        **kwargs,
    ) -> dict[str, Receivable]:
        ...

    @overload
    async def receivable(
        self, account: str, threshold: int, source: Optional[Literal[False]], **kwargs
    ) -> dict[str, int]:
        ...

    async def receivable(
        self,
        account: str,
        threshold: Optional[int] = None,
        source: Optional[bool] = None,
        **kwargs,
    ):  # TODO: Fix return type hint for cases where threshold is a 0 literal
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

        if source and blocks:
            return {k: Receivable(**v) for k, v in dict[str, Any](blocks).items()}
        if threshold and blocks:
            return {k: int(v) for k, v in dict[str, Any](blocks).items()}

        return blocks

    async def receivable_exists(self, hash: str, **kwargs) -> bool:
        """
        Check whether block is receivable by hash
        https://docs.nano.org/commands/rpc-protocol/#receivable_exists
        """

        kwargs["hash"] = hash

        res = await self.call("receivable_exists", **kwargs)
        return bool(res.get("exists"))

    async def representatives(self, **kwargs) -> dict[str, int]:
        """
        Returns a list of pairs of representative and its voting weight
        https://docs.nano.org/commands/rpc-protocol/#representatives
        """

        res = await self.call("representatives", **kwargs)
        return {str(k): int(v) for k, v in res.get("representatives", {}).items()}

    @overload
    async def representatives_online(
        self, weight: Optional[Literal[False]], **kwargs
    ) -> list[str]:
        ...

    @overload
    async def representatives_online(
        self, weight: Literal[True] = True, **kwargs
    ) -> dict[str, Representative]:
        ...

    async def representatives_online(self, weight: Optional[bool] = None, **kwargs):
        """
        Returns a list of online representative accounts that have voted recently
        https://docs.nano.org/commands/rpc-protocol/#representatives_online
        """

        if weight:
            kwargs["weight"] = weight

        res = await self.call("representatives_online", **kwargs)
        representatives = res.get("representatives")

        if weight and representatives:
            return {
                str(k): Representative(**v) for k, v in dict(representatives).items()
            }

        return list[str](representatives or [])

    async def republish(self, **kwargs) -> list[str]:
        """
        Rebroadcast blocks starting at hash to the network
        https://docs.nano.org/commands/rpc-protocol/#republish
        """

        res = await self.call("republish", **kwargs)
        return list(res.get("blocks", []))

    async def sign(self, block: Optional[Any], hash: Optional[str], **kwargs) -> str:
        """
        Signing provided block with private key or key of account from wallet
        https://docs.nano.org/commands/rpc-protocol/#sign
        """

        kwargs["json_block"] = True
        if block:
            kwargs["block"] = dict(block)
        if hash:
            kwargs["hash"] = hash

        res = await self.call("sign", **kwargs)
        return str(res.get("signature", ""))

    async def stats_clear(self, **kwargs) -> bool:
        """
        Clears all collected statistics. The "stat_duration_seconds" value in the
        "stats" action is also reset
        https://docs.nano.org/commands/rpc-protocol/#stats_clear
        """

        res = await self.call("stats_clear", **kwargs)
        return "success" in res

    async def stop(self, **kwargs) -> bool:
        """
        Method to safely shutdown node
        https://docs.nano.org/commands/rpc-protocol/#stop
        """

        res = await self.call("stop", **kwargs)
        return "success" in res

    async def successors(self, block: str, count: int = -1, **kwargs) -> list[str]:
        """
        Signing provided block with private key or key of account from wallet
        https://docs.nano.org/commands/rpc-protocol/#sign
        """

        kwargs["block"] = block
        kwargs["count"] = count

        res = await self.call("successors", **kwargs)
        return list(res.get("blocks", []))

    @overload
    async def telemetry(self, raw: Literal[True], **kwargs) -> list[Telemetry]:
        ...

    @overload
    async def telemetry(self, raw: Literal[False], **kwargs) -> Telemetry:
        ...

    async def telemetry(self, raw: bool = False, **kwargs):
        """
        Return metrics from other nodes on the network. By default, returns a summarized
        view of the whole network. See below for details on obtaining local telemetry data.
        https://docs.nano.org/commands/rpc-protocol/#telemetry
        """

        if raw:
            kwargs["raw"] = raw

        res = await self.call("telemetry", **kwargs)

        return (
            parse_obj_as(list[Telemetry], res) if raw else parse_obj_as(Telemetry, res)
        )

    async def validate_account_number(self, account: str, **kwargs) -> bool:
        """
        Check whether account is a valid account number using checksum
        https://docs.nano.org/commands/rpc-protocol/#validate_account_number
        """

        kwargs["account"] = account

        res = await self.call("validate_account_number", **kwargs)

        return bool(res.get("valid"))

    async def version(self, **kwargs) -> VersionInfo:
        """
        Returns version information for RPC, Store, Protocol (network),
        Node (Major & Minor version)
        https://docs.nano.org/commands/rpc-protocol/#version
        """

        res = await self.call("version", **kwargs)

        return VersionInfo(**res)

    async def unchecked(self, count: Optional[int], **kwargs) -> list[Block]:
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

        return parse_obj_as(list[Block], blocks if blocks else [])

    async def unchecked_clear(self, **kwargs) -> bool:
        """
        Clear unchecked synchronizing blocks
        https://docs.nano.org/commands/rpc-protocol/#unchecked_clear
        """

        res = await self.call("unchecked_clear", **kwargs)

        return "success" in res

    async def unchecked_get(self, hash: str, **kwargs) -> Block:
        """
        Retrieves a json representation of unchecked synchronizing block by hash
        https://docs.nano.org/commands/rpc-protocol/#unchecked_get
        """

        kwargs["hash"] = hash

        res = await self.call("unchecked_get", **kwargs)

        return Block(**res)

    async def unchecked_keys(
        self, key: str, count: Optional[int], **kwargs
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
        unchecked = res.get("unchecked")

        return parse_obj_as(list[UncheckedBlock], unchecked)

    async def unopened(
        self, account: Optional[str], count: Optional[int], **kwargs
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

    async def uptime(self, **kwargs) -> int:
        """
        Return node uptime in seconds
        https://docs.nano.org/commands/rpc-protocol/#uptime
        """

        res = await self.call("unopened", **kwargs)

        return int(res.get("seconds", 0))

    async def work_cancel(self, hash: str, **kwargs) -> bool:
        """
        Stop generating work for block
        https://docs.nano.org/commands/rpc-protocol/#work_cancel
        """

        kwargs["hash"] = hash

        res = await self.call("work_cancel", **kwargs)

        return "success" in res

    async def work_generate(self, hash: str, **kwargs) -> WorkInfo:
        """
        Stop generating work for block
        https://docs.nano.org/commands/rpc-protocol/#work_generate
        """

        kwargs["hash"] = hash

        res = await self.call("work_generate", **kwargs)

        return WorkInfo(**res)

    async def work_peer_add(self, address: str, port: str, **kwargs) -> bool:
        """
        Add specific IP address and port as work peer for node until restart
        https://docs.nano.org/commands/rpc-protocol/#work_peer_add
        """

        kwargs["address"] = address
        kwargs["port"] = port

        res = await self.call("work_peer_add", **kwargs)

        return "success" in res

    async def work_peers(self, **kwargs) -> list[str]:
        """
        https://docs.nano.org/commands/rpc-protocol/#work_peers
        """

        res = await self.call("work_peers", **kwargs)

        peers = res.get("work_peers") or []

        return parse_obj_as(list[str], peers)

    async def work_peers_clear(self, **kwargs) -> bool:
        """
        Clear work peers node list until restart
        https://docs.nano.org/commands/rpc-protocol/#work_peers_clear
        """

        res = await self.call("work_peers_clear", **kwargs)
        return "success" in res

    async def work_validate(self, work: str, hash: str, **kwargs) -> ValidationInfo:
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
