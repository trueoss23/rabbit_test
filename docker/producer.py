import logging
import pika
import settings


logger = logging.getLogger(__name__)


def init_rmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=settings.RMQ_HOST,
        port=settings.RMQ_PORT,
        virtual_host=settings.RMQ_VHOST,
        credentials=pika.PlainCredentials(settings.RMQ_USERNAME,
                                          settings.RMQ_PASSWORD),
    ))
    channel = connection.channel()

    # создаем service_a_inner_exch
    channel.exchange_declare(exchange=settings.RMQ_INPUT_EXCHANGE,
                             exchange_type='fanout')

    # создаем dead_letter_exchange
    channel.exchange_declare(exchange=settings.RMQ_DEAD_EXCHANGE,
                             exchange_type='fanout')

    # создаем service_a_input_q
    channel.queue_declare(
        queue=settings.RMQ_INPUT_QUEUE,
        durable=True,
        arguments={
            # благодаря этому аргументу сообщения из service_a_input_q
            # при nack-е будут попадать в dead_letter_exchange
            'x-dead-letter-exchange': settings.RMQ_DEAD_EXCHANGE,
        }
    )

    # создаем очередь для "мертвых" сообщений
    channel.queue_declare(
        queue=settings.RMQ_DEAD_QUEUE,
        durable=True,
        arguments={
            # благодаря этому аргументу сообщения из service_a_input_q
            # при nack-е будут попадать в dead_letter_exchange
            'x-message-ttl': settings.RMQ_DEAD_TTL,
            # также не забываем, что у очереди "мертвых" сообщений
            # должен быть свой dead letter exchange
            'x-dead-letter-exchange': settings.RMQ_INPUT_EXCHANGE,
        }
    )
    # связываем очередь "мертвых" сообщений с dead_letter_exchange
    channel.queue_bind(
        exchange=settings.RMQ_DEAD_EXCHANGE,
        queue=settings.RMQ_DEAD_QUEUE,
    )

    # связываем основную очередь с входным exchange
    channel.queue_bind(settings.RMQ_INPUT_QUEUE, settings.RMQ_INPUT_EXCHANGE)

    return channel


def callback(ch, method, properties, body):
    logger.info('Processing message `%s`', body)
    if can_retry(properties):
        logger.warning('Retrying message')
        # requeue=False отправит сообщение не в исходную очередь, а в dead letter exchange
        ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
        return

    logger.error('Can`t retry, drop message')
    ch.basic_ack(delivery_tag=method.delivery_tag)


def can_retry(properties):
    """
    Заголовок x-death проставляется при прохождении сообщения через dead letter exchange.
    С его помощью можно понять, какой "круг" совершает сообщение.
    """
    deaths = (properties.headers or {}).get('x-death')
    if not deaths:
        return True
    if deaths[0]['count'] >= settings.RETRY_COUNT:
        return False
    return True


if __name__ == '__main__':
    channel = init_rmq()

    logger.info('Consuming.')
    channel.basic_consume(
        queue=settings.RMQ_INPUT_QUEUE, on_message_callback=callback
    )
    channel.start_consuming()

