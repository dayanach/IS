import json
from threading import Thread
import pika
import requests


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    payload = json.loads(body.decode('utf-8'))
    msg = \
        requests.put("http://127.0.0.1:5000/products/"+payload['product type']+"/quantity?value=" + str(payload['quantity']))
    print(msg.content)


def pull_message():
    connection = pika.BlockingConnection(pika.ConnectionParameters('104.198.35.199'))
    channel = connection.channel()

    channel.exchange_declare(exchange='order', exchange_type='topic')

    result = channel.queue_declare('', exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange='order', queue=queue_name, routing_key="*.*.inventory.update")

    print(' [*] Waiting for messages. To exit press CTRL+C')

    channel.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=True)

    channel.start_consuming()


class MessagePuller(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()

    def run(self):
        while True:
            pull_message()
