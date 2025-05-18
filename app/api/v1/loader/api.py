from flask import Blueprint, request

from app.loader.loader import load_json

loader_api = Blueprint("loader_api", __name__)

@loader_api.route('/load', methods=['POST'])
def load():
  """loads given json to database"""
  data = request.json
  res = ""
  def log(msg):
    nonlocal res
    res += msg
  load_json(data, log)
  print(res)
  return res