import sqlite3
from flask import Flask, render_template, request, redirect, url_for, g
from datetime import date

app = Flask(__name__)

DATABASE = 'users.db'
DONATION_DB = 'donations.db'
DONATED_DB = 'donated.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def get_donation_db():
    db = getattr(g, '_donation_database', None)
    if db is None:
        db = g._donation_database = sqlite3.connect(DONATION_DB)
    return db

def get_donated_db():
    db = getattr(g, '_donated_database', None)
    if db is None:
        db = g._donated_database = sqlite3.connect(DONATED_DB)
    return db


# Close the database connection after each request
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

    db = getattr(g, '_donation_database', None)
    if db is not None:
        db.close()
    
    db = getattr(g, '_donated_database', None)
    if db is not None:
        db.close()

# Create a table to store user information
def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''CREATE TABLE IF NOT EXISTS users
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       name TEXT NOT NULL,SR
                       email TEXT NOT NULL UNIQUE,
                       password TEXT NOT NULL)''')
        db.commit()

# Initialize the database
init_db()

# Create a table to store donation information
def init_donation_db():
    with app.app_context():
        db = get_donation_db()
        db.execute('''CREATE TABLE IF NOT EXISTS donations
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       donor_name TEXT NOT NULL,
                       donation_type TEXT NOT NULL,
                       quantity INTEGER NOT NULL,
                       contact_number TEXT NOT NULL,
                       date TEXT NOT NULL)''')
        db.commit()

# Initialize the donation database
init_donation_db()

# Create a table to store donated_item information
def init_donated_db():
    with app.app_context():
        db = get_donated_db()
        db.execute('''CREATE TABLE IF NOT EXISTS donated
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       donated_to TEXT NOT NULL,
                       donated_type TEXT NOT NULL,
                       quantity INTEGER NOT NULL,
                       contact_number TEXT NOT NULL,
                       date TEXT NOT NULL)''')
        db.commit()

# Initialize the donated_item database
init_donated_db()


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Save the data to the database
        db = get_db()
        db.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', (name, email, password))
        db.commit()

        # Redirect to the home page
        return redirect('/')
    else:
        return render_template('signup.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['username']
        password = request.form['password']

        # Retrieve user information from the database
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

        # Check if the user exists and the password is correct
        if user and user[3] == password:
            return redirect('/donate')
        else:
            return render_template('login.html', error='Invalid email or password')

    else:
        return render_template('login.html')
    
@app.route('/donate', methods=['GET', 'POST'])
def donate():
    if request.method == 'POST':
        # Get form data
        donor_name = request.form['donor_name']
        donation_type = request.form['donation_type']
        contact_number = request.form['contact_number']
        quantity = request.form['quantity']

        # Save the data to the database
        db = get_donation_db()
        cur = db.cursor()
        cur.execute('INSERT INTO donations (donor_name, donation_type, contact_number, quantity, date) VALUES (?, ?, ?, ?, ?)',
                    (donor_name, donation_type, contact_number, quantity, date.today().strftime('%Y-%m-%d')))
        db.commit()

        # Redirect to the dashboard page
        return redirect('/dashboard')
    else:
        return render_template('donate.html')

@app.route('/donated_item',methods = ['GET','POST'])
def donated_item():
    if request.method == 'POST':
        # Get form data
        donated_to = request.form['donated_to']
        donated_type = request.form['donated_type']
        contact_number = request.form['contact_number']
        quantity = request.form['quantity']

        # Save the data to the database
        db = get_donated_db()
        cur = db.cursor()
        cur.execute('INSERT INTO donated (donated_to, donated_type, contact_number, quantity, date) VALUES (?, ?, ?, ?, ?)',
                    (donated_to, donated_type, contact_number, quantity, date.today().strftime('%Y-%m-%d')))
        db.commit()

        # Redirect to the dashboard page
        return redirect('/dashboard')
    else:
        return render_template('donated.html')



#@app.route('/dashboard')
#def dashboard():
    # Retrieve all donations from the database
   # db = get_donation_db()
   # donations = db.execute('SELECT * FROM donations').fetchall()

    #return render_template('dashboard.html', donations=donations)


@app.route('/dashboard')
def dashboard():
    # Retrieve all donations from the database
    db = get_donated_db()
    donated = db.execute('SELECT * FROM donated').fetchall()

    return render_template('dashboard.html', donated=donated)

if __name__ == '__main__':
    app.run(debug=True)
