# Flask CRUD Application

This is a simple Flask-based web application that performs CRUD (Create, Read, Update, Delete) operations using MySQL as the backend database. The app includes user authentication, session management, and secure password hashing.

---

## Features

* User Registration and Login
* Secure password hashing with `passlib`
* Create, Read, Update, Delete items
* Flash messages for success/error feedback
* WTForms for form validation
* MySQL integration with `Flask-MySQLdb`

---

## Project Structure

```
flask_crud/
│
├── app.py                  # Main Flask application
├── templates/              # HTML templates
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── add_item.html
│   └── edit_item.html
├── static/                 # Static files (CSS, JS)
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/flask_crud.git

cd flask_crud
```

### 2. Create and activate virtual environment (optional but recommended)

```bash
python -m venv .venv

.venv\Scripts\activate  # Windows
```

### 3. Install dependencies

```bash

pip install -r requirements.txt
```

### 4. MySQL Setup

* Start your MySQL server (e.g., via XAMPP or MySQL Workbench)
* 
* Create a database:

```sql
CREATE DATABASE myflaskapp;
```

* Create `users` and `items` tables:

```sql
CREATE TABLE users (

    id INT AUTO_INCREMENT PRIMARY KEY,
    
    name VARCHAR(50),
    
    email VARCHAR(50),
    
    username VARCHAR(25),
    
    password VARCHAR(255)
    
);

CREATE TABLE items (

    id INT AUTO_INCREMENT PRIMARY KEY,
    
    title VARCHAR(200),
    
    body TEXT,
    
    author VARCHAR(50),
    
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    
);
```

---

## Running the App

```bash

python app.py
```

Access the app at: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## Requirements

See `requirements.txt`:

```
Flask==2.3.3

Flask-MySQLdb==1.0.1

WTForms==3.1.2

passlib==1.7.4

email-validator==2.1.1
```


---

## License

This project is licensed under the MIT License.

---

## Author

Omkar Dnyaneshwar Narveer
