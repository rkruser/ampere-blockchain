from flask import Flask, jsonify
import redis
from pymongo import MongoClient

app = Flask(__name__)

# Connect to Redis and MongoDB
r = redis.Redis(host='redis', port=6379, decode_responses=True)
client = MongoClient('mongodb://mongo:27017/')
db = client.mydatabase

@app.route('/')
def hello_world():
    # Use Redis as a cache
    visits = r.incr('visits')
    
    # Use MongoDB to store a message
    db.messages.insert_one({f"message {visits}": "Hello, World!"})
    
    return jsonify(message="Hello, World!", visits=visits)

@app.route('/messages')
def get_messages():
    # Get all messages from MongoDB
    messages = db.messages.find()
    # extract all messages
    messages = [message for message in messages]
    print(messages)
    print(type(messages))
    return jsonify({"messages": str(messages)})

if __name__ == '__main__':
    app.run(host='0.0.0.0')
