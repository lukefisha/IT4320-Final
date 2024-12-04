from flask import Flask, render_template, request, flash, redirect, url_for
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


def generate_seating_chart():
    total_rows = 12  # defualt
    total_columns = 4  # default

    # initializes seating chart with Os
    seating_chart = [['O' for _ in range(total_columns)] for _ in range(total_rows)]

    # get reserved seats from the reservations table
    conn = get_db()
    reserved_seats = conn.execute('SELECT seatRow, seatColumn FROM reservations').fetchall()
    conn.close()

    # mark reserved seats with 'X'
    for seat in reserved_seats:
        row = seat['seatRow'] - 1  
        column = seat['seatColumn'] - 1  
        if 0 <= row < total_rows and 0 <= column < total_columns:
            seating_chart[row][column] = 'X'

    # return chart formatted 
    chart_display = "<br />".join([str(row) for row in seating_chart])
    return chart_display

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        user_option = request.form.get('user_option')
        
        if user_option == "admin":
            return redirect(url_for('admin'))
        elif user_option == "reservation":
            return redirect(url_for('reservation'))
        else:
            flash("Please select an option before submitting.")

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
            chart = generate_seating_chart()
            return render_template('admin.html', chart=chart)
        else:
            #if not, display error
            flash("Invalid username/password combination")
            return render_template('admin.html')

    return render_template('admin.html')

@app.route('/reservations', methods=['GET', 'POST'])
def reservation():
    chart = generate_seating_chart() #initial chart when page is loaded

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
                conn.execute('INSERT INTO reservations (passengerName, seatRow, seatColumn, eTicketNumber) VALUES (?, ?, ?, ?)', (firstName, row, seat, eTicket))
                conn.commit()

                #edit chart and get the updated seating chart
                chart = generate_seating_chart()
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

        finally:
            # close database connection
            if conn:
                conn.close()

    return render_template('reservation.html', chart=chart)



if __name__ == "__main__":
    app.run(debug=True)