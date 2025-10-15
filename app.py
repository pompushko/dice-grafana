from flask import Flask, jsonify
import random
import logging
from datetime import datetime
import os

app = Flask(__name__)

log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'dice.log')

logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
logger.addHandler(console_handler)

service_ready = True

@app.route('/health', methods=['GET'])
def health():
    if service_ready:
        return jsonify({'status': 'healthy', 'message': 'Service is ready'}), 200
    else:
        return jsonify({'status': 'unhealthy', 'message': 'Service is not ready'}), 500

@app.route('/dice', methods=['GET'])
def dice():
    dice_roll = random.randint(1, 6)
    logger.info(f'Dice roll: {dice_roll}')
    return jsonify({'dice_roll': dice_roll}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)