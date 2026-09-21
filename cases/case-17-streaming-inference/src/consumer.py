from kafka import KafkaConsumer, KafkaProducer
import json
from model import model

consumer = KafkaConsumer('events', enable_auto_commit=True, group_id='model-v1')
producer = KafkaProducer(bootstrap_servers='kafka:9092')

for message in consumer:
    event = json.loads(message.value)
    score = model.predict(event['features'])
    producer.send('predictions', json.dumps({'id': event['id'], 'score': score}).encode())
