from flask import Blueprint, jsonify, request
from Find_Countours import generate_walls
import glob
import os
import random
import time

controller_api = Blueprint('controller_api', __name__)


@controller_api.route("/send_image", methods=["POST"])
def process_image():
    file = request.files['image']
    path = 'temp/im-received.jpg'
    file.save(path)

    result = generate_walls(path)

    os.remove(path)

    return jsonify(result)
