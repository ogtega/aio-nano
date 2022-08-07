# aio-nano

## Overview

This library contains an asynchronous python RPC client for Nano nodes, allowing you to more easily develop on the Nano network with with fully type annnotated methods and responses.

## Installation

### PIP

`pip install aio-nano`

### Poetry

`poetry add aio-nano`

## Example Async HTTP RPC Call

```python
from aio_nano import Client
import asyncio

async def main():
  api_key = ...
  client = Client('https://mynano.ninja/api/node', {'Authorization': api_key})

  supply = await client.available_supply()
  print(supply)

asyncio.run(main())
```

## Example Async WebSocket RPC Subscription

```python
import asyncio
from time import time

from aio_nano import WSClient


async def main():
  ws = await WSClient("ws://localhost:7078").connect()
  start = time() * 1000
  await ws.subscribe("confirmation", lambda x: print(x), ack=True)
  print(f"Acked in {time() * 1000 - start}ms")

  await asyncio.Future()


asyncio.run(main())

```
