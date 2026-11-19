import os

def connection_options():
    return {
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.environ["DB_USER"],
        "password": os.environ["DB_PASSWORD"],
        "database": os.getenv("DB_NAME", "krishiparampara"),
        "connection_timeout": 5,
    }
