from hashlib import md5

from flask import Flask, jsonify, request

from src.db import db

app = Flask(__name__)


@app.route('/api/v1/hello_world')
def hello_world():
    return jsonify({'message': 'hello world'})


@app.route('/api/v1/register', methods=['POST'])
def registration():
    data = request.get_json()
    if blank_fields := {'F', 'I', 'O', 'car', 'login', 'password', 'phone'} - set(data.keys()):
        return jsonify({'error': f'Поля {blank_fields} не заполнены'}), 400

    if db.fetchall(f"SELECT * FROM clients WHERE login='{data['login']}';"):
        return jsonify({'error': 'Пользователь с таким логином существует'}), 400

    r = db.commit(f"CALL add_client('{data['F']}', '{data['I']}', '{data['O']}', '{data['car']}', '{data['login']}', " +
    f"'{data['password']}', '{data['phone']}');")
    return jsonify({'message': 'Пользователь успешно зарегистрирован', 'test': r}), 200


@app.route('/api/v1/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'не передан json'})
    if blank_fields := {'login', 'password'} - set(data.keys()):
        return jsonify({'error': f'Поля {blank_fields} не заполнены'}), 400

    hash_password = md5(data['password'].encode()).hexdigest()
    user = db.fetchall(f"SELECT * FROM clients WHERE login='{data['login']}' AND password='{hash_password}'")
    if not user:
        return jsonify({'error': 'Неправильный логин или пароль'}), 400

    user = user[0]
    return jsonify({'id': user[0], 'F': user[1], 'I': user[2], 'O': user[3], 'car': user[4], 'phone': user[7]}), 200


@app.route('/api/v1/contracts/<int:user_id>', methods=['GET'])
def user_contracts(user_id: int):
    contracts = db.callproc('get_client_contracts', [user_id, ])
    result = []
    for contract in contracts:
        result.append({
            'id': contract[0],
            'date_start': contract[1],
            'date_finish': contract[2],
            'name': contract[3],
            'fio_small': contract[4],
            'services': {
                'name': 'Твоя процедура не работает, почини',
                'cost': 1023
            }
        })
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(threaded=True, port=5000)
