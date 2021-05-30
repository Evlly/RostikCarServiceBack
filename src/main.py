from flask import Flask, jsonify, request
from db import db

app = Flask(__name__)


@app.route('/api/v1/hello_world')
def hello_world():
    return jsonify({'message': 'hello world'})


@app.route('/api/v1/register', methods=['POST'])
def registration():
    data = request.get_json()
    if blank_fields := {'F', 'I', 'O', 'car', 'login', 'password', 'phone'} - set(data.keys()):
        return jsonify({'error': f'Поля {blank_fields} не заполнены'}), 400

    if db.execute(f"SELECT * FROM clients WHERE login='{data['login']}';"):
        return jsonify({'error': 'Пользователь с таким логином существует'}), 400


if __name__ == '__main__':
    app.run(threaded=True, port=5000)
