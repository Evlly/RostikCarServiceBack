from hashlib import md5

from flask import Flask, jsonify, request

from src.db import db
from datetime import datetime

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
    return jsonify({'user':{'id': user[0], 'F': user[1], 'I': user[2], 'O': user[3], 'car': user[4], 'phone': user[7]}}), 200


@app.route('/api/v1/contracts/<int:user_id>', methods=['GET'])
def user_contracts(user_id: int):
    contracts = db.callproc('get_client_contracts', [user_id, ])
    result = []
    for contract in contracts:
        result.append({
            'id': contract[0],
            'date_start': datetime.strftime(contract[1], '%d.%m.%Y'),
            'date_finish': datetime.strftime(contract[2], '%d.%m.%Y'),
            'name': contract[3],
            'fio_small': contract[4],
            'services': [
                {
                    'name': x[1],
                    'cost': x[2]
                } for x in db.callproc('get_soc_client', [contract[0], ]) if len(x) == 3
            ]
        })
    return jsonify(result), 200


@app.route('/api/v1/contracts', methods=['POST'])
def create_user_contracts():
    data = request.get_json()

    sql = f'''INSERT INTO contract (id_client, date_start, date_finish) VALUES ({data["id_client"]}, '{data["date_start"]}', '{data["date_finish"]}')'''
    db.commit(sql)
    id_contract = db.fetchall('SELECT id FROM contract ORDER BY id DESC LIMIT 1')[0][0]

    for price in data['id_price']:
        sql = f'INSERT INTO services_on_contract (id_price, id_contract) VALUES ({price["id"]}, {id_contract})'
        db.commit(sql)

    return jsonify({'msg': 'ok'})


@app.route('/api/v1/all_services', methods=['GET'])
def all_services():
    result = []
    for service in db.fetchall('SELECT * FROM view_price_back'):
        result.append({
            "id": service[0],
            "name_ts": service[1].strip(),
            "name_s": service[2].strip(),
            "cost": service[3],
        })
    return jsonify(result)

if __name__ == '__main__':
    app.run(threaded=True, port=5000)
