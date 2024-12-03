from flask import Flask, render_template, request, flash
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
    if request.method == 'POST':
        #get login from form
        username = request.form.get("username")
        password = request.form.get("password")

        #query the database with the supplied user and pass
        conn = get_db()
        admin_login = conn.execute('SELECT * FROM admins WHERE username = ? AND password = ?', (username, password, )).fetchone()
        conn.close()

        #check if it exists
        if admin_login:
            #if so, display chart
            chart = 1234
            return render_template('admin.html', chart=chart)
        else:
            #if not, display error
            flash("Invalid username/password combination")
            return render_template('admin.html')

    return render_template('admin.html')

@app.route('/reservations', methods=['GET', 'POST'])
def reservation():
    return render_template('reservation.html')

if __name__ == "__main__":
    app.run(debug=True)