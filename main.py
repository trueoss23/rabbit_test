import pika

# Подключение к брокеру RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Определение очередей
main_queue = 'main_queue'
error_queue = 'error_queue'

# Создание очередей, если они еще не существуют
channel.queue_declare(queue=main_queue)
channel.queue_declare(queue=error_queue)

# Функция-продюсер
def producer():
    while True:
        # Генерация сообщения (заглушка)
        message = generate_message()
        
        # Публикация сообщения в основную очередь
        channel.basic_publish(exchange='pes', routing_key=main_queue, body=message)

# Функция-воркер
def worker():
    def callback(ch, method, properties, body):
        message = body.decode()
        
        try:
            # Обработка сообщения (заглушка)
            process_message(message)
            
            # Подтверждение успешной обработки сообщения
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            # Если произошла ошибка, помещаем сообщение в очередь ошибок
            channel.basic_publish(exchange='pes', routing_key=error_queue, body=message)

    # Установка предпочитаемого количества сообщений для получения
    channel.basic_qos(prefetch_count=1)

    # Подписка на очередь для получения сообщений
    channel.basic_consume(queue=main_queue, on_message_callback=callback)

    # Запуск цикла получения сообщений
    channel.start_consuming()

# Функция для обработки ошибок
def error_handler():
    def callback(ch, method, properties, body):
        message = body.decode()
        
        # Обработка ошибки (заглушка)
        handle_error(message)
        
        # Возвращение сообщения в основную очередь
        channel.basic_publish(exchange='pes', routing_key=main_queue, body=message)
        
        # Подтверждение успешной обработки сообщения из очереди ошибок
        ch.basic_ack(delivery_tag=method.delivery_tag)

    # Установка предпочитаемого количества сообщений для получения
    channel.basic_qos(prefetch_count=1)

    # Подписка на очередь ошибок для получения сообщений
    channel.basic_consume(queue=error_queue, on_message_callback=callback)

    # Запуск цикла получения сообщений из очереди ошибок
    channel.start_consuming()


# Заглушка для функции генерации сообщений
def generate_message():
    return "Example message"

# Заглушка для функции обработки сообщений
def process_message(message):
    print("Processing message:", message)

# Заглушка для функции обработки ошибок
def handle_error(message):
    print("Handling error for message:", message)


# Запуск продюсера
producer()

# Запуск воркеров
worker()

# Запуск обработчика ошибок
error_handler()
