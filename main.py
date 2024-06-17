import psycopg2
import pprint
import json


class Client:
    def __init__(self, name:str, surname:str, email:str, phone:tuple = None):
        self.name = name
        self.surname = surname
        self.email = email
        self.phone = phone

def create_table(conn):
    with conn.cursor() as cur:
        cur.execute('''CREATE TABLE IF NOT EXISTS client(
                                                    id_client SERIAL PRIMARY KEY,
                                                    name VARCHAR(50) NOT NULL, 
                                                    surname VARCHAR(50) NOT NULL, 
                                                    email VARCHAR(100) UNIQUE);
                    ''')
        print('Созадана таблица client')
        cur.execute('''CREATE TABLE IF NOT EXISTS phone(
                                                    id_phone SERIAL PRIMARY KEY,
                                                    phone VARCHAR(50) UNIQUE,
                                                    id_client INTEGER REFERENCES client(id_client));
                    ''')
        conn.commit()
        print('Созадана таблица phone')


def insert_client(conn, client):
    cur.execute('INSERT INTO client(name, surname, email) VALUES (%s, %s, %s)', (client.name, client.surname, client.email))
    conn.commit()
    print('Добавлен новый клиент')
    id_client = get_id_client(conn, client)
    if client.phone:
        for phone in client.phone:
            cur.execute('INSERT INTO phone(phone, id_client) VALUES (%s, %s)', (phone, id_client))
            print('Добавлен новый телефон')
    conn.commit()


def insert_phone(conn, client, phone):
    if get_id_client(conn, client) == None:
        print('Такого клиента нет')
        return
    id_client = get_id_client(conn, client)
    cur.execute('INSERT INTO phone(phone, id_client) VALUES (%s, %s)', (phone, id_client))
    conn.commit()
    print('Добавлен новый телефон')

def change_client(conn, client, client1):
    if get_id_client(conn, client) == None:
        print('Такого клиента нет')
        return
    id_client = get_id_client(conn, client)
    cur.execute('UPDATE client SET name = %s, surname = %s, email = %s WHERE id_client = %s',
                (client1.name, client1.surname, client1.email, id_client))
    conn.commit()

def del_phone(conn):
    cur.execute('SELECT * FROM client')
    conn.commit()
    pprint.pprint(cur.fetchall())
    id_client = input('Выберите id клиента: ')
    cur.execute('SELECT id_phone, phone FROM phone WHERE id_client = %s', (id_client,))
    conn.commit()
    pprint.pprint(cur.fetchall())
    id_phone = input('Выберите id телефона: ')
    cur.execute('DELETE FROM phone WHERE id_phone = %s', (id_phone,))
    conn.commit()
    print('Телефон удален')

def del_client(conn, client):
    if get_id_client(conn, client) == None:
        print('Такого клиента нет')
        return
    id_client = get_id_client(conn, client)
    cur.execute('DELETE FROM phone WHERE id_client = %s', (id_client,))
    cur.execute('DELETE FROM client WHERE id_client = %s', (id_client,))
    conn.commit()
    print('Клиент удален')


def get_id_client(conn, client):
    cur.execute('SELECT id_client FROM client WHERE name = %s AND surname = %s AND email = %s',
                (client.name, client.surname, client.email))
    conn.commit()
    return cur.fetchone()[0]

def search_client(conn):
    query = input('Запрос: ')
    query = '%' + query + '%'

    cur.execute('''SELECT name, surname, email, phone.phone FROM client 
                    JOIN phone ON client.id_client = phone.id_client
                    WHERE name LIKE %s OR surname LIKE %s OR email LIKE %s OR phone LIKE %s
                    GROUP BY client.id_client, phone.phone;
                ''',
                (query, query, query, query))
    conn.commit()
    if cur.rowcount == 0:
        return print('Таких клиентов нет')

    return print(cur.fetchall())

client = Client('Иван', 'Иванов', 'iv@iv.ru', ('+7-111-111-11-11', '+7-222-222-22-22'))
client1 = Client('Петр', 'Петров', 'pe@pe.ru', ('+7-333-353-33-33', '+7-444-444-44-44'))
client2 = Client('Сергей', 'Сергеев', 'se@se.ru', ('+7-555-555-55-55', '+7-666-666-66-66'))
client3 = Client('Алексей', 'Алексеев', 'al@al.ru', ('+7-777-777-77-77', '+7-888-888-88-88'))

with open("connection.json", encoding='utf-8') as f:
    json_data = json.load(f)
    dbname = json_data['dbname']
    user = json_data['user']
    password = json_data['password']


with psycopg2.connect(dbname=dbname, user=user, password=password) as conn:
    with conn.cursor() as cur:
        cur.execute('SELECT version()')

        db_version = cur.fetchone()
        print(db_version)

        create_table(conn)
        insert_client(conn, client)
        insert_client(conn, client1)
        insert_client(conn, client2)
        insert_client(conn, client3)
        insert_phone(conn, client, '+7-333-333-33-33')
        del_client(conn, client)

        search_client(conn)
        del_phone(conn)
