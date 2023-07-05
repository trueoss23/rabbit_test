import pika


class MqClient:
    def __init__(self, *, mq_host, mq_port, username, password):
        credentials = pika.PlainCredentials(username, password)
        conn_params = pika.ConnectionParameters(
            host=mq_host,
            port=mq_port,
            credentials=credentials
        )
        self.connection = pika.BlockingConnection(conn_params)
        self.channel = self.connection.channel()

    def get_channel(self):
        return self.channel

    def create_exchange(self, change_name):
        self.channel.exchange_declare(
            exchange=change_name,
            exchange_type='topic',
            passive=False,
            durable=True,
            auto_delete=False
        )

    def create_queue(self, exchange_name, queue_name, routing_key,
                     is_dead=False):
        arguments = {}
        if not is_dead:
            arguments = {
                "x-dead-letter-exchange": exchange_name,
                "x-dead-letter-routing-key": routing_key,
            }
        self.channel.queue_declare(
            queue=queue_name,
            arguments=arguments,
        )
        self.queue_bind(exchange_name, queue_name, routing_key)

    def queue_bind(self, exchange_name, queue_name, routing_key):
        self.channel.queue_bind(
            queue=queue_name,
            exchange=exchange_name,
            routing_key=routing_key,
        )

    def connect(self):
        self.create_exchange(DEAD_EXCHANGE_NAME)
        self.create_queue(DEAD_EXCHANGE_NAME,
                          DEAD_QUEUE_NAME, DEAD_ROUTING_KEY, is_dead=True)

        self.create_exchange(EXCHANGE_NAME)
        self.create_queue(EXCHANGE_NAME, QUEUE_NAME, ROUTING_KEY)