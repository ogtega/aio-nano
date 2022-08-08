import pytest

from aio_nano import Client


@pytest.fixture
async def rpc():
    rpc = Client(uri="http://localhost:7076")
    yield rpc
    await rpc.client.close()
