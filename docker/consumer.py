import pika
import settings


def init_rmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=settings.RMQ_HOST,
        port=settings.RMQ_PORT,
        virtual_host=settings.RMQ_VHOST,
        credentials=pika.PlainCredentials(settings.RMQ_USERNAME,
                                          settings.RMQ_PASSWORD),
    ))
    channel = connection.channel()

    channel.exchange_declare(exchange=settings.RMQ_INPUT_EXCHANGE,
                             exchange_type='fanout')

    return channel, connection


if __name__ == '__main__':
    channel, connection = init_rmq()

    channel.basic_publish(exchange=settings.RMQ_INPUT_EXCHANGE,
                          routing_key='',
                          body='message from rmq')

