from abc import abstractmethod
from contextlib import asynccontextmanager
from typing import Protocol


class SupportsAsyncClose(Protocol):
    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def wait_closed(self) -> None:
        raise NotImplementedError()


@asynccontextmanager
async def async_closing(subject: SupportsAsyncClose):
    try:
        yield subject
    finally:
        subject.close()
        await subject.wait_closed()
