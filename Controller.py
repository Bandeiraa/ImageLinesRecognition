from flask import Blueprint, jsonify, request
from Find_Countours import generate_walls
import glob
import os
import random
import time
import json

controller_api = Blueprint('controller_api', __name__)

if not os.path.exists("temp"):
    os.mkdir("temp")


@controller_api.route("/send_image", methods=["POST"])
def process_image():
    file = request.files['imagem']

    path = 'temp/im-received.jpg'

    file.save(path)

    result = generate_walls(path)
    os.remove(path)

    return jsonify(result)
