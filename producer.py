from kafka import KafkaProducer
import json
import time
import random
from datetime import datetime, timedelta

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

users = ["john_doe", "tech_guru21", "alice_w", "charlie.dev", "emma.smith",
         "data_ninja", "cloud_master", "ai_expert", "cyber_sam", "bigdata_queen"]

post_types = ["text", "image", "video"]

hashtags = ["#AI","#CloudComputing","#Cybersecurity","#DataScience","#BigData",
            "#MachineLearning","#DeepLearning","#TechNews","#Innovation","#Programming"]

sentences = [
    "Exploring AI trends.",
    "Cloud deployment success!",
    "Cybersecurity awareness matters.",
    "Big data analytics insights.",
    "Machine learning breakthrough.",
    "Deep learning experiment.",
    "Tech innovation is inspiring.",
    "Python project in progress.",
    "Future of automation.",
    "Data science revolution."
]

def realistic_timestamp():
    now = datetime.now()
    delta = timedelta(minutes=random.randint(0, 120))
    return (now - delta).strftime("%Y-%m-%d %H:%M:%S")

while True:
    post = {
        "user": random.choice(users),
        "type": random.choice(post_types),
        "topic": random.choice(hashtags),
        "text": random.choice(sentences),
        "likes": random.randint(50, 1200),
        "comments": random.randint(5, 300),
        "shares": random.randint(0, 200),
        "timestamp": realistic_timestamp()
    }

    producer.send("social-media", post)
    print("Sent to Kafka:", post)

    time.sleep(6)