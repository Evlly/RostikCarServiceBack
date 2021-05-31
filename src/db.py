from mysql.connector import connect, Error
from os import getenv


class DataBase:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def fetchall(self, sql: str):
        try:
            with connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql)
                    return cursor.fetchall()
        except Error as e:
            print(e)

    def fetcone(self, sql: str):
        try:
            with connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql)
                    return cursor.fetcone()
        except Error as e:
            print(e)

    def commit(self, sql: str):
        try:
            with connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql)
                    connection.commit()
        except Error as e:
            print(e)

    def callproc(self, proc: str, args: list):
        try:
            with connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database,
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.callproc(proc, args)
                    cursor.stored_results()
                    for result in cursor.stored_results():
                        print(result.fetchall())
        except Error as e:
            print(e)


db = DataBase(
    host=getenv('host'),
    user=getenv('user'),
    password=getenv('password'),
    database=getenv('database'),
)
