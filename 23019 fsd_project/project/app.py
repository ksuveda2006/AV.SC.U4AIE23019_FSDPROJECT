from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
import json
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'super_secret_key' # Required for flashing messages

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DATABASE = 'benefits.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    # Drops existing tables for a clean slate with the new schema in development
    conn.execute('DROP TABLE IF EXISTS beneficiary')
    conn.execute('DROP TABLE IF EXISTS users')

    conn.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            locality TEXT,
            full_name TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE beneficiary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            scheme_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            docs_list TEXT,
            application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Seed Admin User
    admin_pw = generate_password_hash('suveda999')
    conn.execute("INSERT INTO users (username, password_hash, role, full_name, locality) VALUES (?, ?, ?, ?, ?)",
                 ('suveda12', admin_pw, 'Admin', 'Admin Suveda', 'All'))

    # Seed Anganwadi and Sachavalayam
    official_pw = generate_password_hash('password123')
    conn.execute("INSERT INTO users (username, password_hash, role, full_name, locality) VALUES (?, ?, ?, ?, ?)",
                 ('anganwadi1', official_pw, 'Anganwadi', 'Asha (Anganwadi)', 'Ward 1'))
    conn.execute("INSERT INTO users (username, password_hash, role, full_name, locality) VALUES (?, ?, ?, ?, ?)",
                 ('sachavalayam2', official_pw, 'Sachavalayam', 'Raju (Sachavalayam)', 'Ward 2'))

    # Seed Normal Users
    user_pw = generate_password_hash('user123')
    conn.execute("INSERT INTO users (username, password_hash, role, full_name, locality) VALUES (?, ?, ?, ?, ?)",
                 ('ravi_w1', user_pw, 'User', 'Ravi Kumar', 'Ward 1'))
    conn.execute("INSERT INTO users (username, password_hash, role, full_name, locality) VALUES (?, ?, ?, ?, ?)",
                 ('sneha_w1', user_pw, 'User', 'Sneha Reddy', 'Ward 1'))
    conn.execute("INSERT INTO users (username, password_hash, role, full_name, locality) VALUES (?, ?, ?, ?, ?)",
                 ('vijay_w2', user_pw, 'User', 'Vijay Krishna', 'Ward 2'))

    conn.commit()

    # Seed applications (Ravi has applied, Sneha hasn't)
    ravi = conn.execute("SELECT id FROM users WHERE username='ravi_w1'").fetchone()
    if ravi:
        conn.execute("INSERT INTO beneficiary (user_id, scheme_name, status, docs_list) VALUES (?, ?, ?, ?)",
                     (ravi['id'], 'National Health Mission', 'Pending', '["aadhaar_sample.pdf", "income_cert.png"]'))
    
    vijay = conn.execute("SELECT id FROM users WHERE username='vijay_w2'").fetchone()
    if vijay:
        conn.execute("INSERT INTO beneficiary (user_id, scheme_name, status, docs_list) VALUES (?, ?, ?, ?)",
                     (vijay['id'], 'PM Kisan Samman Nidhi', 'Approved', '["land_doc.pdf"]'))

    conn.commit()
    conn.close()

# Initialize the database and seeds
init_db()

@app.route('/')
def index():
    if 'user_id' not in session:
        return render_template('index.html')
        
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    if not user:
        session.clear()
        return redirect(url_for('index'))

    data = {}
    if user['role'] == 'Admin':
        data['schemes'] = conn.execute('''
            SELECT b.*, u.full_name, u.locality 
            FROM beneficiary b 
            JOIN users u ON b.user_id = u.id 
            ORDER BY b.application_date DESC
        ''').fetchall()
    elif user['role'] in ['Anganwadi', 'Sachavalayam']:
        # Fetch all users in their ward
        ward_users = conn.execute('''
            SELECT u.id, u.full_name, u.username, b.scheme_name, b.status, b.application_date 
            FROM users u
            LEFT JOIN beneficiary b ON u.id = b.user_id
            WHERE u.locality = ? AND u.role = 'User'
        ''', (user['locality'],)).fetchall()
        data['ward_users'] = ward_users
    else:
        # Normal User
        data['my_schemes'] = conn.execute('''
            SELECT * FROM beneficiary WHERE user_id = ? ORDER BY application_date DESC
        ''', (user['id'],)).fetchall()
        
    conn.close()
    return render_template('dashboard.html', user=user, data=data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['locality'] = user['locality']
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Admin cannot be created here. Only User, Anganwadi, Sachavalayam
    if request.method == 'POST':
        full_name = request.form['full_name']
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        locality = request.form['locality']
        
        if not full_name or not username or not password or not role or not locality:
            flash('All fields are required!', 'danger')
            return redirect(url_for('register'))
            
        if role not in ['User', 'Anganwadi', 'Sachavalayam']:
            flash('Invalid role selected.', 'danger')
            return redirect(url_for('register'))
            
        conn = get_db_connection()
        existing = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
        if existing:
            flash('Username already exists. Please pick another one.', 'danger')
            conn.close()
            return redirect(url_for('register'))
            
        hashed_pw = generate_password_hash(password)
        conn.execute('INSERT INTO users (username, password_hash, role, full_name, locality) VALUES (?, ?, ?, ?, ?)',
                     (username, hashed_pw, role, full_name, locality))
        conn.commit()
        conn.close()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/submit', methods=('GET', 'POST'))
def submit():
    if 'user_id' not in session:
        flash('You must be logged in to track a benefit.', 'warning')
        return redirect(url_for('login'))
        
    if session.get('role') != 'User':
        flash('Only normal users can submit applications. Admins/Officials should only review.', 'warning')
        return redirect(url_for('index'))

    if request.method == 'POST':
        scheme_name = request.form['scheme_name']

        if not scheme_name:
            flash('Please select a scheme!', 'danger')
            return redirect(url_for('submit'))

        conn = get_db_connection()
        # Check if already applied for this scheme
        exists = conn.execute('SELECT id FROM beneficiary WHERE user_id = ? AND scheme_name = ?',
                              (session['user_id'], scheme_name)).fetchone()
        
        if exists:
            flash('You have already applied for this scheme.', 'warning')
            conn.close()
            return redirect(url_for('submit'))
            
        saved_files = []
        for key, file in request.files.items():
            if file and file.filename != '':
                filename = secure_filename(f"{session['user_id']}_{key}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                saved_files.append(filename)
                
        # Also grab any extra text fields dynamically added by the schema JS
        # like mobile_number or family_details and add them to a JSON blob
        extra_data = {}
        for key, val in request.form.items():
            if key not in ['scheme_name'] and val.strip() != '':
                extra_data[key] = val.strip()
                
        # Combine filenames and extra text data into docs_list just to store them easily
        docs_str = json.dumps({"files": saved_files, "text_data": extra_data})
            
        conn.execute('INSERT INTO beneficiary (user_id, scheme_name, docs_list) VALUES (?, ?, ?)',
                     (session['user_id'], scheme_name, docs_str))
        conn.commit()
        conn.close()
        
        return redirect(url_for('success'))
        
    return render_template('submit.html')

@app.route('/update_status/<int:id>', methods=['POST'])
def update_status(id):
    if session.get('role') != 'Admin':
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('index'))

    new_status = request.form.get('status')
    if new_status in ['Pending', 'Approved', 'Rejected']:
        conn = get_db_connection()
        conn.execute('UPDATE beneficiary SET status = ? WHERE id = ?', (new_status, id))
        conn.commit()
        conn.close()
        flash('Status updated successfully.', 'success')
    else:
        flash('Invalid status.', 'danger')

    return redirect(url_for('index'))

@app.route('/success')
def success():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('success.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
