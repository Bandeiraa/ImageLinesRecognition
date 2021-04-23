from flask import Blueprint, jsonify, request
from Find_Countours import generate_walls
import glob
import os
import random
import time

controller_api = Blueprint('controller_api', __name__)


@controller_api.route('/send_image', methods=['GET'])
def get_verify_query():
    path = "Resources/newFiles/1.jpg"
    result = generate_walls(path)

    return jsonify(result)
