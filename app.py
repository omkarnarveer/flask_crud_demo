from flask import Flask, render_template, flash, redirect, url_for, session, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

# --- CONFIGURATION ---
# Secret key for session management and CSRF protection
app.config['SECRET_KEY'] = 'your_super_secret_key_12345'

# MySQL database configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Your MySQL username
app.config['MYSQL_PASSWORD'] = ('root')  # Your MySQL password
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'  # Returns rows as dictionaries

# Initialize MySQL
mysql = MySQL(app)


# --- DECORATORS ---
# Check if user is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login.', 'danger')
            return redirect(url_for('login'))

    return wrap


# --- FORMS (using Flask-WTF) ---
# Registration Form
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50), validators.Email()])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


# Item Form
class ItemForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = TextAreaField('Body', [validators.Length(min=30)])


# --- ROUTES ---
# Home / Index - Show all public items
@app.route('/')
def index():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM items ORDER BY create_date DESC")
    items = cur.fetchall()
    cur.close()

    if result > 0:
        return render_template('index.html', items=items)
    else:
        msg = 'No Items Found'
        return render_template('index.html', msg=msg)


# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)",
                    (name, email, username, password))
        mysql.connection.commit()
        cur.close()

        flash('You are now registered and can log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']

        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            data = cur.fetchone()
            password = data['password']

            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username
                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)
        cur.close()
    return render_template('login.html')


# User Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


# Dashboard - Show user's own items
@app.route('/dashboard')
@is_logged_in
def dashboard():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM items WHERE author = %s ORDER BY create_date DESC", [session['username']])
    items = cur.fetchall()
    cur.close()

    if result > 0:
        return render_template('dashboard.html', items=items)
    else:
        msg = 'No Items Found'
        return render_template('dashboard.html', msg=msg)


# Add Item (CREATE)
@app.route('/add_item', methods=['GET', 'POST'])
@is_logged_in
def add_item():
    form = ItemForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO items(title, body, author) VALUES(%s, %s, %s)",
                    (title, body, session['username']))
        mysql.connection.commit()
        cur.close()

        flash('Item Created', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_item.html', form=form)


# Edit Item (UPDATE)
@app.route('/edit_item/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_item(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM items WHERE id = %s AND author = %s", (id, session['username']))
    item = cur.fetchone()

    # If item doesn't exist or doesn't belong to the user, redirect.
    if not item:
        flash('Not authorized to edit this item.', 'danger')
        return redirect(url_for('dashboard'))

    form = ItemForm(request.form)
    # Populate form fields from DB
    if request.method == 'GET':
        form.title.data = item['title']
        form.body.data = item['body']

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']

        cur.execute("UPDATE items SET title=%s, body=%s WHERE id=%s", (title, body, id))
        mysql.connection.commit()
        cur.close()

        flash('Item Updated', 'success')
        return redirect(url_for('dashboard'))

    return render_template('edit_item.html', form=form)


# Delete Item (DELETE)
@app.route('/delete_item/<string:id>', methods=['POST'])
@is_logged_in
def delete_item(id):
    cur = mysql.connection.cursor()

    # Security check: ensure the item belongs to the logged-in user before deleting
    cur.execute("SELECT author FROM items WHERE id = %s", [id])
    item = cur.fetchone()

    if item and item['author'] == session['username']:
        cur.execute("DELETE FROM items WHERE id = %s", [id])
        mysql.connection.commit()
        flash('Item Deleted', 'success')
    else:
        flash('Not authorized to delete this item.', 'danger')

    cur.close()
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True)