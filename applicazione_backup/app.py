from flask import Flask, request, jsonify, send_file
import mysql.connector
import os
import subprocess
import zipfile

app = Flask(__name__)
SHARED_FOLDER = '/shared_backups'

def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'db'),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', 'root'),
        database=os.environ.get('DB_NAME', 'backup_db')
    )

@app.route('/mysqlBackup', methods=['POST'])
def mysql_backup():
    file_name = request.args.get('fileName')
    if not file_name:
        return jsonify({"error": "Devi specificare il parametro fileName nell'URL"}), 400

    sql_file = os.path.join(SHARED_FOLDER, f"{file_name}.sql")
    zip_file = os.path.join(SHARED_FOLDER, f"{file_name}.zip")

    db_host = os.environ.get('DB_HOST', 'db')
    db_pass = os.environ.get('DB_PASSWORD', 'root')
    db_name = os.environ.get('DB_NAME', 'backup_db')

    try:
        dump_command = f"mysqldump -h {db_host} -u root -p{db_pass} {db_name} > {sql_file}"
        subprocess.run(dump_command, shell=True, check=True)

        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(sql_file, arcname=f"{file_name}.sql")
        
        os.remove(sql_file)

        conn = get_db_connection()
        cursor = conn.cursor()
        query = "INSERT INTO backup_log (filename) VALUES (%s)"
        cursor.execute(query, (f"{file_name}.zip",))
        conn.commit()
        cursor.close()
        conn.close()

        return send_file(zip_file, as_attachment=False)

    except Exception as e:
        return jsonify({"error": f"Si è verificato un errore: {str(e)}"}), 500

if __name__ == '__main__':
    os.makedirs(SHARED_FOLDER, exist_ok=True)
    app.run(host='0.0.0.0', port=5001)
