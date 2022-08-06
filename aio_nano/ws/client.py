import asyncio
import json
from enum import Enum
from typing import Any, AsyncIterable, Callable, Iterable, Literal, Union, overload

from websockets.client import WebSocketClientProtocol, connect
from websockets.exceptions import ConnectionClosed
from websockets.typing import Data


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
                print(await self.client.recv())
            except ConnectionClosed:
                self.client = await self.connection

    @overload
    async def subscribe(
        self,
        topic: Literal[Topic.confirmation] | Literal["confirmation"],
        cb: Callable[[object], Any],
        **options: Any,
    ):
        ...

    @overload
    async def subscribe(
        self, topic: Literal[Topic.vote], cb: Callable[[object], Any], **options: Any
    ):
        ...

    @overload
    async def subscribe(
        self,
        topic: Literal[Topic.stopped_election],
        cb: Callable[[object], Any],
        **options: Any,
    ):
        ...

    @overload
    async def subscribe(
        self,
        topic: Literal[Topic.active_difficulty],
        cb: Callable[[object], Any],
        **options: Any,
    ):
        ...

    @overload
    async def subscribe(
        self, topic: Literal[Topic.pow], cb: Callable[[object], Any], **options: Any
    ):
        ...

    @overload
    async def subscribe(
        self,
        topic: Literal[Topic.telemetry],
        cb: Callable[[object], Any],
        **options: Any,
    ):
        ...

    @overload
    async def subscribe(
        self,
        topic: Literal[Topic.new_unconfirmed_block],
        cb: Callable[[object], Any],
        **options: Any,
    ):
        ...

    @overload
    async def subscribe(
        self,
        topic: Literal[Topic.bootstrap],
        cb: Callable[[object], Any],
        **options: Any,
    ):
        ...

    async def subscribe(
        self, topic: Topic | str, cb: Callable[[object], Any], **options: Any
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
