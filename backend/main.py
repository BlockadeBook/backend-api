import json
from operator import iadd

import requests
from flask import Flask, request

from backend.loader import load_json

app = Flask(__name__)

@app.route('/')
def main_page():
  return 'nothing here yet'

@app.route('/api/load', methods=['POST'])
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


if __name__ == '__main__':
  app.run(debug=True, port=5000)
