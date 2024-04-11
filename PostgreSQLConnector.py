import os
import psycopg2
from psycopg2 import sql


class PostgreSQLConnector:
    def __init__(self):
        self.dbname = os.environ.get('PG_DBNAME', 'open_weather')
        self.user = os.environ.get('PG_USER', 'root')
        self.password = os.environ.get('PG_PASSWORD', '123456')
        self.host = os.environ.get('PG_HOST', 'localhost')
        self.port = os.environ.get('PG_PORT', '5432')
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self.cursor = self.connection.cursor()
            # print("Connected to PostgreSQL database")
        except psycopg2.Error as e:
            print("Error connecting to PostgreSQL database:", e)

    def disconnect(self):
        if self.connection:
            self.cursor.close()
            self.connection.close()
            # print("Disconnected from PostgreSQL database")

    def select(self, table, columns="*", condition=None, parameters=None):
        if not parameters:
            parameters = []

        columns_sql = sql.SQL("*") if columns == "*" else sql.SQL(',').join(map(sql.Identifier, columns))

        query = sql.SQL("SELECT {} FROM {}").format(
            columns_sql,
            sql.Identifier(table)
        )
        if condition:
            query += sql.SQL(" WHERE {}").format(sql.SQL(condition))
        self.cursor.execute(query, parameters)
        return self.cursor.fetchall()

    def update(self, table, values, condition, parameters=None):
        if not parameters:
            parameters = []

        query = sql.SQL("UPDATE {} SET {} WHERE {}").format(
            sql.Identifier(table),
            sql.SQL(',').join(sql.SQL("{} = %s").format(sql.Identifier(col)) for col in values.keys()),
            sql.SQL(condition)
        )
        self.cursor.execute(query, list(values.values()) + parameters)
        self.connection.commit()

    def insert(self, table, values):
        query = sql.SQL("INSERT INTO {} ({}) VALUES ({}) RETURNING id").format(
            sql.Identifier(table),
            sql.SQL(',').join(map(sql.Identifier, values.keys())),
            sql.SQL(',').join(sql.Placeholder() * len(values))
        )
        self.cursor.execute(query, list(values.values()))
        inserted_id = self.cursor.fetchone()[0]  # Retrieve the ID of the inserted row
        self.connection.commit()
        return inserted_id

    def delete(self, table, condition=None, parameters=None):
        if not parameters:
            parameters = []

        if condition:
            query = sql.SQL("DELETE FROM {} WHERE {}").format(
                sql.Identifier(table),
                sql.SQL(condition)
            )
        else:
            query = sql.SQL("DELETE FROM {}").format(
                sql.Identifier(table)
            )
        self.cursor.execute(query, parameters)
        self.connection.commit()

    def execute_query(self, query, parameters=None):
        if not parameters:
            parameters = []

        self.cursor.execute(query, parameters)
        return self.cursor.fetchall()

    def execute_sql_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                sql_commands = file.read()
                self.cursor.execute(sql_commands)
                self.connection.commit()
            # print("SQL file executed successfully")
        except FileNotFoundError:
            print("SQL file not found")
        except psycopg2.Error as e:
            print("Error executing SQL file:", e)

    def table_exists(self, table_name):
        try:
            self.cursor.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_name = %s
                )
                """,
                (table_name,)
            )
            exists = self.cursor.fetchone()[0]
            return exists
        except psycopg2.Error as e:
            print("Error checking if table exists:", e)
            return False
