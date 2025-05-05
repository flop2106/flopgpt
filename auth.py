# -*- coding: utf-8 -*-
"""
Created on Sun Sep 17 00:04:48 2023

@author: nurar
"""

from sqlalchemy import text, create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd

DATABASE_URL = 'sqlite:///password.db'
engine = create_engine(DATABASE_URL)
#Base = declarative_base(engine)
def execute_sql(statement, parameters = None):
    with engine.connect() as connection:
        result = connection.execute(text(statement), parameters)
        if 'select' in statement.lower():
            result = result.fetchall()
        else:
            with connection.begin():
                connection.execute(text(statement), parameters or {})

        #connection.commit()
    return result
class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.set_password()

    @staticmethod
    def initialize_table():
        init_table_statement = """
                                CREATE TABLE IF NOT EXISTS users (
                               user_id INTEGER PRIMARY KEY,
                               username TEXT UNIQUE NOT NULL,
                               password_hash TEXT NOT NULL
                               );
                          """
        execute_sql(init_table_statement)

    def set_password(self):
        self.password_hash = generate_password_hash(self.password)

    def check_password(self, password_db):
        return check_password_hash(password_db, self.password)

    def check_userid(self):
        check_user_statement = """
                                 SELECT
                                     *
                                 FROM
                                     users
                                WHERE
                                    username LIKE :username
                                 """

        count_user = execute_sql(check_user_statement, {'username': self.username})
        #count_user = count_user.fetchall()
        if count_user: #To check password
            rows = count_user[0]
            self.password_db = rows[2]
            if self.check_password(self.password_db): #check if the password is right
                return True
            else:
                print('Wrong Password')
                self.password = input('Insert Your Password Again: ')
                self.set_password()
                self.check_userid()
                return False
        else:
            return False



    def insert_user(self):
        check_max_id_statement = '''
            SELECT
                MAX(user_id)
            FROM
                users
            LIMIT 1
            '''
        max_id = execute_sql(check_max_id_statement)[0][0]
        if max_id == None:
            max_id = 0
        max_id += 1
        insert_statement = f"""
            INSERT INTO users (user_id, username, password_hash)
            VALUES (:max_id, :username, :password_hash);
        """
        execute_sql(insert_statement,{'max_id':max_id,
                                      'username':self.username,
                                      'password_hash':self.password_hash})
        print(f"User {self.username} Added!")



if __name__ == '__main__':
    User.initialize_table()