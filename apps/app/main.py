from aio_pika import DeliveryMode, ExchangeType, Message, connect
from fastapi import FastAPI, HTTPException

import uvicorn
import asyncio


app = FastAPI()


async def send_message(message: str) -> None:
    connection = await connect("amqp://guest:guest@localhost/")
    async with connection:
        channel = await connection.channel()

        my_exchange = await channel.declare_exchange(
            "publisher", ExchangeType.FANOUT,
        )

        message_body = f'{message}'.encode()

        message = Message(
            message_body,
            delivery_mode=DeliveryMode.PERSISTENT,
        )
        await my_exchange.publish(message, routing_key="")


@app.post("/send-message")
async def send_message_to_rabbitmq(message: str):
    try:
        await send_message('Pes')
        return {"message": "Сообщение успешно отправлено"}
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Ошибка при отправке сообщения: {str(e)}")


if __name__ == '__main__':
    uvicorn.run("main:app", host="localhost", port=8001, reload=True)
