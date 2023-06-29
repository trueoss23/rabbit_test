import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare("dlx_exchange", "direct")
channel.queue_declare("test_queue", arguments={
  "x-dead-letter-exchange": "dlx_exchange", "x-dead-letter-routing-key": "dlx_key"})
channel.queue_declare("dead_letter_queue")
channel.queue_bind("dead_letter_queue", "dlx_exchange", "dlx_key")

channel.exchange_declare(exchange='logs', exchange_type='fanout')

result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='logs', queue=queue_name)

print(' [*] Waiting for logs. To exit press CTRL+C')


def callback(ch, method, properties, body):
    print(" [x] %r" % body)


channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()