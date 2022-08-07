import asyncio
import json
from enum import Enum
from typing import Any, AsyncIterable, Callable, Iterable, Literal, Union, overload

from websockets.client import WebSocketClientProtocol, connect
from websockets.exceptions import ConnectionClosed
from websockets.typing import Data

from aio_nano.ws.models import (
    Block,
    Bootstrap,
    Confirmation,
    Difficulty,
    PoW,
    Telemetry,
    Vote,
)


class Topic(str, Enum):
    confirmation = "confirmation"
    vote = "vote"
    stopped_election = "stopped_election"
    active_difficulty = "active_difficulty"
    pow = "work"
    telemetry = "telemetry"
    new_unconfirmed_block = "new_unconfirmed_block"
    bootstrap = "bootstrap"


class WSClient(connect):
    __slots__ = "connection", "client", "loop"

    connection: connect
    client: WebSocketClientProtocol
    loop: asyncio.AbstractEventLoop
    _callbacks: dict[str, list[Callable]]

    _parsers: dict[str, Callable[[dict], object]] = {
        "confirmation": lambda msg: Confirmation.parse_obj(msg),
        "vote": lambda msg: Vote.parse_obj(msg),
        "stopped_election": lambda msg: msg.get("hash"),
        "active_difficulty": lambda msg: Difficulty.parse_obj(msg),
        "work": lambda msg: PoW.parse_obj(msg),
        "telemetry": lambda msg: Telemetry.parse_obj(msg),
        "new_unconfirmed_block": lambda msg: Block.parse_obj(msg),
        "bootstrap": lambda msg: Bootstrap.parse_obj(msg),
    }

    def __init__(self, uri: str, **args) -> None:
        self.connection = connect(uri, **args)
        self.loop = asyncio.get_event_loop()
        self._callbacks = {}

    async def connect(self):
        self.client = await self.connection
        self.loop.create_task(self._recv())

    async def send(self, data: Union[Data, Iterable[Data], AsyncIterable[Data]]):
        await self.client.send(data)

    async def _recv(self):
        while True:
            try:
                data = json.loads(await self.client.recv())
                topic = data.get("topic") or ""
                msg = data.get("message") or {}

                for cb in self._callbacks[topic]:
                    obj = self._parsers.get(topic, lambda _: None)(msg)
                    if asyncio.iscoroutinefunction(cb):
                        asyncio.create_task(cb(obj))
                        continue
                    cb(obj)

            except ConnectionClosed:
                self.client = await self.connection

    @overload
    async def subscribe(
        self,
        topic: Literal[Topic.confirmation] | Literal["confirmation"],
        cb: Callable[[Confirmation], Any],
        **options: Any,
    ):
        ...

    @overload
    async def subscribe(
        self,
        topic: Literal[Topic.vote] | Literal["vote"],
        cb: Callable[[Vote], Any],
        **options: Any,
    ):
        ...

    @overload
    async def subscribe(
        self,
        topic: Literal[Topic.stopped_election] | Literal["stopped_election"],
        cb: Callable[[str], Any],
        **options: Any,
    ):
        ...

    @overload
    async def subscribe(
        self,
        topic: Literal[Topic.active_difficulty] | Literal["active_difficulty"],
        cb: Callable[[Difficulty], Any],
        **options: Any,
    ):
        ...

    @overload
    async def subscribe(
        self,
        topic: Literal[Topic.pow] | Literal["work"],
        cb: Callable[[PoW], Any],
        **options: Any,
    ):
        ...

    @overload
    async def subscribe(
        self,
        topic: Literal[Topic.telemetry] | Literal["telemetry"],
        cb: Callable[[Telemetry], Any],
        **options: Any,
    ):
        ...

    @overload
    async def subscribe(
        self,
        topic: Literal[Topic.new_unconfirmed_block] | Literal["new_unconfirmed_block"],
        cb: Callable[[Block], Any],
        **options: Any,
    ):
        ...

    @overload
    async def subscribe(
        self,
        topic: Literal[Topic.bootstrap] | Literal["bootstrap"],
        cb: Callable[[Bootstrap], Any],
        **options: Any,
    ):
        ...

    async def subscribe(
        self, topic: Topic | str, cb: Callable[[Any], Any], **options: Any
    ):
        await self.send(
            json.dumps(
                {
                    "action": "subscribe",
                    "topic": str(topic),
                    **({"options": options} if options else {}),
                }
            )
        )
        self._callbacks[str(topic)] = self._callbacks.get(str(topic)) or []
        self._callbacks[str(topic)].append(cb)
