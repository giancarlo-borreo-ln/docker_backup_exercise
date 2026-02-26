from flask import Flask, jsonify
import mysql.connector
import os

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'db'),         
        user=os.environ.get('DB_USER', 'root'),       
        password=os.environ.get('DB_PASSWORD', 'root'), 
        database=os.environ.get('DB_NAME', 'backup_db')
    )

@app.route('/viewBackupHistory', methods=['GET'])
def view_backup_history():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True) 

        query = "SELECT id, filename, timestamp FROM backup_log ORDER BY timestamp DESC"
        cursor.execute(query)

        logs = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(logs), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
