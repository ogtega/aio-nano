# aio-nano

## Overview

This library contains an asynchronous python RPC client for Nano nodes, allowing you to more easily develop on the Nano network with with fully type annnotated methods and responses.

## Installation

### PIP

`pip install aio-nano`

### Poetry

`poetry add aio-nano`

## Example

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
