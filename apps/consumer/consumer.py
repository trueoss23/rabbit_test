import asyncio

from aio_pika import ExchangeType, connect
from aio_pika.abc import AbstractIncomingMessage


async def on_message(message: AbstractIncomingMessage) -> None:
    async with message.process():
        print(message.body.decode())


async def accept_message() -> None:
    connection = await connect("amqp://guest:guest@localhost/")

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)

        my_exchange = await channel.declare_exchange(
            "publisher", ExchangeType.FANOUT,
        )
        queue = await channel.declare_queue(exclusive=True)
        await queue.bind(my_exchange)
        await queue.consume(on_message)

        print(" [*] Waiting for message. To exit press CTRL+C")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(accept_message())
