from decimal import Decimal
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field


class BlockSubtype(str, Enum):
    send = "send"
    receive = "receive"
    change = "change"
    epoch = "epoch"


class BlockType(str, Enum):
    send = "send"
    receive = "receive"
    state = "state"


class Block(BaseModel):
    type: BlockType
    account: str
    previous: str
    representative: str
    balance: int
    link: str
    link_as_account: Optional[str]
    signature: str
    work: str


class BlockInfo(BaseModel):
    block_account: str
    amount: int
    balance: int
    height: int
    local_timestamp: int
    successor: str
    confirmed: bool
    contents: Block
    subtype: BlockSubtype
    pending: Optional[bool]
    source_account: Optional[str]


class AccountBalance(BaseModel):
    balance: int
    pending: int
    receivable: int


class HistoricalBlock(Block):
    local_timestamp: int
    height: int
    hash: str
    confirmed: bool
    subtype: Optional[BlockSubtype]
    amount: int


class AccountHistory(BaseModel):
    account: str
    history: list[HistoricalBlock]
    previous: Optional[str]
    next: Optional[str]


class AccountInfo(BaseModel):
    frontier: str
    open_block: str
    representative_block: str
    balance: int
    confirmed_balance: Optional[int]
    modified_timestamp: int
    block_count: int
    account_version: int
    confirmation_height: int = Field(alias="confirmed_height")
    confirmation_height_frontier: str = Field(alias="confirmed_frontier")
    representative: Optional[str]
    confirmed_representative: Optional[str]
    weight: Optional[int]
    pending: Optional[int]
    receivable: Optional[int]
    confirmed_pending: Optional[int]
    confirmed_receivable: Optional[int]

    class Config:
        allow_population_by_field_name = True


class AccountPendingInfo(BaseModel):
    amount: int
    source: str


class BlockCount(BaseModel):
    count: int
    unchecked: int
    cemented: Optional[int]


class SignedBlock(BaseModel):
    hash: str
    difficulty: str
    block: Block


class BlocksInfo(BaseModel):
    blocks: dict[str, BlockInfo]
    blocks_not_found: Optional[list[str]]


class ActiveConfirmations(BaseModel):
    confirmations: list[str]
    unconfirmed: int
    confirmed: int


class Confirmation(BaseModel):
    tally: int
    contents: Block
    representatives: Optional[dict[str, int]]


class ConfirmationInfo(BaseModel):
    announcements: int
    last_winner: str
    total_tally: int
    blocks: dict[str, Confirmation]


class LazyBootstrapInfo(BaseModel):
    started: bool
    key_inserted: bool


class ConfirmationQuorumPeer(BaseModel):
    account: str
    ip: str
    weight: int


class ConfirmationQuorum(BaseModel):
    quorum_delta: int
    online_weight_quorum_percent: int
    online_weight_minimum: int
    online_stake_total: int
    peers_stake_total: int
    trended_stake_total: int
    peers: Optional[list[ConfirmationQuorumPeer]]


class DeterministicKeypair(BaseModel):
    private: str
    public: str
    account: str


class LedgerInfo(BaseModel):
    frontier: str
    open_block: str
    representative_block: str
    balance: int
    modified_timestamp: int
    block_count: int
    representative: Optional[str]
    weight: Optional[int]
    pending: Optional[int]
    receivable: Optional[int]


class PeerInfo(BaseModel):
    protocol_version: int
    node_id: str
    type: Literal["tcp"]


class Receivable(BaseModel):
    amount: int
    source: str


class Representative(BaseModel):
    weight: int


class Telemetry(BaseModel):
    block_count: int
    cemented_count: int
    unchecked_count: int
    account_count: int
    bandwidth_cap: int
    peer_count: int
    protocol_version: int
    uptime: int
    genesis_block: str
    major_version: int
    minor_version: int
    patch_version: int
    pre_release_version: int
    maker: int
    timestamp: int
    active_difficulty: str
    node_id: Optional[str]
    signature: Optional[str]
    address: Optional[str]
    port: Optional[str]


class VersionInfo(BaseModel):
    rpc_version: int
    store_version: int
    protocol_version: int
    node_vendor: str
    store_vendor: str
    network: str
    network_identifier: str
    build_info: str


class UncheckedBlock(BaseModel):
    key: str
    hash: str
    modified_timestamp: int
    contents: Block


class WorkInfo(BaseModel):
    work: str
    difficulty: str
    multiplier: Decimal
    hash: str


class ValidationInfo(BaseModel):
    valid: Optional[bool]
    valid_all: bool
    valid_receive: bool
    difficulty: str
    multiplier: Decimal
