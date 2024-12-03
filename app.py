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

def eTicketGenerator(s1, s2):
	# To store the final string 
	result = "" 

	# combine two strings by alternating characters 
	i = 0
	while (i < len(s1)) or (i < len(s2)):  
		if (i < len(s1)): 
			result += s1[i] 
		if (i < len(s2)): 
			result += s2[i] 
		i += 1
	return result


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
    chart = 1234

    if request.method == "POST":

        #get values from user input
        firstName = request.form["first_name"]
        lastName = request.form["last_name"]
        row = int(request.form["row"]) - 1
        seat = int(request.form["seat"]) - 1 
        eTicket = eTicketGenerator(firstName, 'INFOTC4320')

        try:
            conn = get_db()
            isSeatTaken = conn.execute('SELECT * FROM reservations WHERE seatRow = ? AND seatColumn = ?', (row, seat)).fetchone()

            # if seat and row not taken in chart
            if not isSeatTaken:

                #insert into table, edit chart, and return chart
                insert_reservation = conn.execute('INSERT INTO reservations (passengerName, seatRow, seatColumn, eTicketNumber) VALUES (?, ?, ?, ?)', (firstName, row, seat, eTicket))
                conn.commit()

                #edit chart and get the updated seating chart
                chart = 4321
                conn.close()

                #send ticket information
                ticketConfirmation = f"Congrats {firstName} {lastName}! You have reserved Row: {row + 1}, Seat: {seat + 1}. eTicketNumber: {eTicket}"
                return render_template('reservation.html', chart=chart, ticket=ticketConfirmation)
            
            # else flash error saying seat taken
            else:
                flash("Seat taken, select an open seat")
                conn.close()

                #return old chart
                return render_template('reservation.html', chart=chart)
            
        except ValueError as e:
            chart = None
            print("Error fetching data:", e)
    return render_template('reservation.html', chart=chart)

if __name__ == "__main__":
    app.run(debug=True)