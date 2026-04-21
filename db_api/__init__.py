import os
from pathlib import Path

import pymysql


ENV_PATHS = (
    Path.cwd() / ".env",
    Path(__file__).resolve().parents[1] / ".env",
)


def _load_env_file():
    loaded = set()
    for env_path in ENV_PATHS:
        env_path = env_path.resolve()
        if env_path in loaded or not env_path.exists():
            continue
        loaded.add(env_path)
        with env_path.open(encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                os.environ.setdefault(key, value)


def _required_env(name):
    value = os.getenv(name)
    if value is None or value == "":
        raise RuntimeError(
            "Missing database environment variable: {}. "
            "Create .env from .env.example or set it in the shell.".format(name)
        )
    return value


def get_database_config():
    _load_env_file()
    return {
        "host": _required_env("CPHOS_DB_HOST"),
        "port": int(os.getenv("CPHOS_DB_PORT", "3306")),
        "user": _required_env("CPHOS_DB_USER"),
        "password": _required_env("CPHOS_DB_PASSWORD"),
        "db": _required_env("CPHOS_DB_NAME"),
        "charset": os.getenv("CPHOS_DB_CHARSET", "utf8mb4"),
    }


class CustomOperation():
    def __init__(self):
        self.MySQLCommand = None

    def execute(self, cursor: pymysql.cursors.Cursor):
        try:
            cursor.execute(self.MySQLCommand)
            return cursor.fetchall()
        except Exception as e:
            print(e)
            raise e


class CustomTransaction():
    def __init__(self):
        self.is_connecting = False
        print("CustomTransaction init")
        db_config = get_database_config()
        self.host = db_config["host"]
        self.port = db_config["port"]
        self.user = db_config["user"]
        self.db = db_config["db"]
        self.password = db_config["password"]
        self.charset = db_config["charset"]

        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        try:
            self.conn = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                db=self.db,
                charset=self.charset,
            )
        except Exception as e:
            raise Exception("Connect to database failed.") from e
        print("Connect to database successfully.")
        self.cursor = self.conn.cursor()

        self.is_connecting = True
        if os.getenv("CPHOS_DB_SHOW_TABLES", "1") != "0":
            self.cursor.execute("show tables")
            tables = self.cursor.fetchall()
            print("The tables in the database are:")
            print(tables)

    def executeOperation(self, operation: CustomOperation):
        if not self.is_connecting:
            print("Not connecting!")
            return Exception("Not connecting!")

        try:
            result = operation.execute(self.cursor)
            return result
        except Exception as e:
            print("Execute operation failed.")
            self.conn.rollback()
            self.conn.close()
            print("Rollback. Remote Closed.")
            raise e

    def commit(self):
        if not self.is_connecting:
            print("Not connecting!")
            return Exception("Not connecting!")
        try:
            self.conn.commit()
            self.conn.close()
            self.is_connecting = False
            print("Commit successfully. Remote Closed.")
            print("You need to call customTransaction.connect() again to connect to the database.")
        except Exception as e:
            print("Commit failed.")
            raise e

    def rollBack(self):
        if not self.is_connecting:
            print("Not connecting!")
            return Exception("Not connecting!")
        try:
            self.conn.rollback()
            self.conn.close()
            self.is_connecting = False
            print("Rollback successfully. Remote Closed.")
            print("You need to call customTransaction.connect() again to connect to the database again.")
        except Exception as e:
            print("Rollback failed.")
            raise e

    def __del__(self):
        if self.is_connecting:
            print("Notice that you have not rollBack or commited the transaction yet.")
            print("Quit without commiting. Roll back.")
            print("You must call customTransaction.commit() to commit your changes.")
            self.conn.rollback()
            self.conn.close()
            self.is_connecting = False


customTransaction = CustomTransaction()
