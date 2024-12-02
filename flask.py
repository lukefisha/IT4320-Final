from flask import Flask, render_template, url_for
import sqlite3


app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SECRET_KEY"] = 'your_secret_key'
DATABASE = 'reservations.db'

#function to get connection to database
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/', methods=['GET', 'POST'])
def main():
    return render_template('main.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    return render_template('admin.html')

@app.route('/reservations', methods=['GET', 'POST'])
def reservation():
    return render_template('reservation.html')

app.run(port=5008, debug=True)