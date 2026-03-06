from kafka import KafkaConsumer
import json
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
cred = credentials.Certificate("firebase_key.json")  # put your key here
firebase_admin.initialize_app(cred)
db = firestore.client()

consumer = KafkaConsumer(
    'social-media',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("Consumer started...")

for message in consumer:
    post = message.value
    db.collection("posts").add(post)
    print("Saved to Firebase:", post)