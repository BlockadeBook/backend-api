from flask import Flask, request
import json_extractor
app = Flask(__name__)

@app.route('/')
def hello_world():
  return 'Hello, World!'

@app.route('/greet/<name>')
def greet(name):
  return f'Hello, {name}!'

@app.route('/api/load', methods=['POST'])
def load():
  data = request.get_json()
  print(json_extractor.extract(data))
  return "ok"


if __name__ == '__main__':
  json_extractor.init()
  app.run(debug=True)
