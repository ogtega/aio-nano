from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, validator


class Block(BaseModel):
    type: Literal["state"]
    account: str
    previous: str
    representative: str
    balance: int
    link: str
    link_as_account: str
    signature: str
    work: str
    subtype: str


class ElectionInfo(BaseModel):
    duration: int
    time: int
    tally: int
    request_count: int
    blocks: int
    voters: int


class Confirmation(BaseModel):
    account: str
    amount: int
    hash: str
    confirmation_type: str
    election_info: Optional[ElectionInfo]
    block: Block


class Vote(BaseModel):
    account: str
    signature: str
    sequence: int
    blocks: list[str]
    type: str


class Difficulty(BaseModel):
    multiplier: Decimal
    network_current: str
    network_minimum: str
    network_receive_current: str
    network_receive_minimum: str


class PoWRequest(BaseModel):
    hash: str
    difficulty: str
    multiplier: Decimal
    version: Literal["work_1"]


class PoWResult(BaseModel):
    source: str
    work: str
    difficulty: str
    multiplier: Decimal


class PoW(BaseModel):
    success: bool
    reason: str
    duration: int
    request: PoWRequest
    result: Optional[PoWResult]
    bad_peers: list[str]

    @validator("bad_peers", pre=True)
    def validate_peers(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return []
        return value


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
    node_id: str
    signature: str
    address: str
    port: str


class Bootstrap(BaseModel):
    reason: str
    id: str
    mode: str
    total: Optional[int]
    duration: Optional[int]
