from flask import Flask, jsonify
import pymysql
import os
import socket

app = Flask(__name__)

# Database configuration from environment variables
DB_HOST = os.environ.get("DB_HOST")
DB_USER = os.environ.get("DB_USER", "admin")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = os.environ.get("DB_NAME", "novapaydb")


def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=3306,
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5
    )


@app.route("/")
def home():
    hostname = socket.gethostname()

    try:
        connection = get_db_connection()

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    c.full_name,
                    c.account_number,
                    t.transaction_type,
                    t.amount,
                    t.description
                FROM customers c
                JOIN transactions t
                    ON c.customer_id = t.customer_id
                ORDER BY t.transaction_id
            """)

            transactions = cursor.fetchall()

        connection.close()

        return jsonify({
            "application": "NovaPay Digital Banking Platform",
            "server": hostname,
            "database": "Connected to Amazon RDS MySQL",
            "transactions": transactions
        })

    except Exception as error:
        return jsonify({
            "application": "NovaPay Digital Banking Platform",
            "server": hostname,
            "database": "Connection failed",
            "error": str(error)
        }), 500


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "server": socket.gethostname()
    }), 200


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8080
    )
