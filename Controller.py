from flask import Blueprint, jsonify, request
from Find_Countours import generate_walls
import glob
import os
import random
import time

controller_api = Blueprint('controller_api', __name__)

if not os.path.exists("temp"):
    os.mkdir("temp")


@controller_api.route("/send_image", methods=["POST"])
def process_image():
    print("result")
    file = request.files['imagem']
    print("result1")

    path = 'temp/im-received.jpg'
    print("result2")

    file.save(path)
    print("result3")

    result = generate_walls(path)

    print(result)
    os.remove(path)

    return jsonify(result)
