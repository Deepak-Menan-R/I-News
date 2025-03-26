from flask import Flask, request, redirect, url_for, render_template, make_response, jsonify
from flask import session
import requests
import secrets
import sqlite3
import hashlib
from db.init_db import init_db
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)  # Enable CORS with credentials support
app.secret_key = secrets.token_hex(16)

NEWSAPI_KEY = '4d6317c37ab54d2b9500c36ac0e2d150'
BASE_URL = 'https://newsapi.org/v2/top-headlines'

# Initialize the database when the Flask app starts
init_db()

@app.route('/')
def index():
    return redirect(url_for('login')) 


# Function to get database connection
def get_db_connection():
    conn = sqlite3.connect('db/db.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/signup', methods=['OPTIONS', 'POST'])
def signup():
    if request.method == 'OPTIONS':
        # Respond to preflight requests indicating that the requested origin is allowed
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
        response.headers.add("Access-Control-Allow-Methods", "POST")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        return response

    if request.method == 'POST':
        data = request.get_json()  # Get JSON data from the request
        
        # Extract data from JSON
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        favorite_categories = data.get('categories', [])  # Get selected categories from the JSON data
        favorite_countries = data.get('countries', [])  # Get selected countries from the JSON data
        
        # Check if the user already exists
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM User WHERE username = ? OR email = ?", (username, email))
        existing_user = cursor.fetchone()
        
        if existing_user:
            return jsonify({'message': 'User already exists'}), 400
        
        # Check if categories and countries are selected
        if not favorite_categories or not favorite_countries:
            return jsonify({'message': 'Please select at least one category and one country'}), 400
        
        try:
            # Start a transaction
            conn.execute("BEGIN")
            
            # Insert the new user into the database
            cursor.execute("INSERT INTO User (username, email, password_hash) VALUES (?, ?, ?)", (username, email, hashed_password))
            user_id = cursor.lastrowid
            
            # Insert the user's favorite categories into the User_Preference table
            for category in favorite_categories:
                # Get the category_id from the Category table
                cursor.execute("SELECT category_id FROM Category WHERE category_name = ?", (category,))
                category_id = cursor.fetchone()[0]
                # Insert into User_Preference table
                cursor.execute("INSERT INTO User_Preference (user_id, category_id, country_id) VALUES (?, ?, NULL)", (user_id, category_id))
                
            # Insert the user's favorite countries into the User_Preference table
            for country in favorite_countries:
                # Get the country_id from the Country table
                cursor.execute("SELECT country_id FROM Country WHERE country_name = ?", (country,))
                country_id = cursor.fetchone()[0]
                # Insert into User_Preference table
                cursor.execute("INSERT INTO User_Preference (user_id, category_id, country_id) VALUES (?, NULL, ?)", (user_id, country_id))
            
            # Commit the transaction
            conn.commit()
            conn.close()
            
            return jsonify({'message': 'User created successfully'}), 201
        
        except Exception as e:
            # Rollback the transaction in case of error
            conn.rollback()
            print(e)
            return jsonify({'message': 'An error occurred while creating user. Please try again.'}), 500
    
    return jsonify({'message': 'Invalid request'}), 400


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()  # Get JSON data from the request
    username = data.get('username')
    password = data.get('password')
    # Hash the password to compare with the stored hash
    print(password)
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    # Check if the credentials are valid
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM User WHERE username = ?", (username,))
    user = cursor.fetchone()
    if user and user['password_hash'] == hashed_password:
        session['user_id'] = user['user_id']  # Create a session for the user
        session.modified = True  # Ensure that the session is marked as modified
        # Insert login activity into Activity table
        print(session['user_id'])
        login_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("INSERT INTO Activity (user_id, login_timestamp) VALUES (?, ?)", (user['user_id'], login_time))
        conn.commit()
        conn.close()
        response_data = {'message': 'Login successful', 'user_id': session['user_id']}
        return jsonify(response_data), 200
    else:
        conn.close()
        return jsonify({'message': 'Invalid credentials'}), 401
    
@app.route('/cate_post', methods=['POST'])
def cate_post():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        category = data.get('category')

        if not user_id:
            return jsonify({'message': 'User ID is missing in the request'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM User WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()

        if not user:
            return jsonify({'message': 'Invalid user ID'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT country_id FROM User_Preference WHERE user_id = ?", (user_id,))
        user_country = cursor.fetchall()
        country_names = []
        for country_id in user_country:
            country_id = country_id[0] if country_id else None
            if country_id:
                cursor.execute("SELECT country_name FROM Country WHERE country_id = ?", (country_id,))
                country_name = cursor.fetchone()[0] if country_id else None
                if country_name:
                    country_names.append(country_name)
        all_articles = []
        for country in country_names:
            params = {
                'country': country,
                'category': category,
                'pageSize': 20,
                'apiKey': NEWSAPI_KEY,
            }
            response = requests.get(BASE_URL, params=params)
            data = response.json()
            articles = data.get('articles', [])
            valid_articles = [article for article in articles if article.get('title')
                              and article.get('url')
                              and article.get('description') != '[Removed]'
                              and article.get('content') != '[Removed]'
                              and article.get('publishedAt') != '1970-01-01T00:00:00Z']
            for article in valid_articles:
                article['category'] = category
                article['country'] = country
                all_articles.append(article)

        # User ID is valid, proceed with retrieving top headlines
        return jsonify({'categry_articles': all_articles}), 200
        
    except Exception as e:
        print('Error:', e)
        return jsonify({'message': 'An error occurred while processing the request'}), 500
    

@app.route('/categories', methods=['POST'])
def categories():
    try:
        data = request.get_json()
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'message': 'User ID is missing in the request'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM User WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()

        if not user:
            return jsonify({'message': 'Invalid user ID'}), 401

        # User ID is valid, proceed with retrieving top headlines
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT category_id FROM User_Preference WHERE user_id = ?", (user_id,))
        user_categories = cursor.fetchall()
        category_names = []
        for category_id in user_categories:
            # Ensure category_id is extracted correctly
            category_id = category_id[0] if category_id else None
            if category_id:
                cursor.execute("SELECT category_name FROM Category WHERE category_id = ?", (category_id,))
                category_name = cursor.fetchone()
                if category_name:
                    category_names.append(category_name[0])

        return jsonify({'categories': category_names}), 200
    except Exception as e:
        print('Error:', e)
        return jsonify({'message': 'An error occurred while processing the request'}), 500

@app.route('/top_headlines', methods=['POST'])
def top_headlines():
    try:
        data = request.get_json()
        print(data.keys())

        user_id = data['user_id']
        print("Request:\n", request.headers)

        if not user_id:
            return jsonify({'message': 'User ID is missing in the request'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM User WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()

        if not user:
            return jsonify({'message': 'Invalid user ID'}), 401

        # User ID is valid, proceed with retrieving top headlines
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT category_id, country_id FROM User_Preference WHERE user_id = ?", (user_id,))
        user_preferences = cursor.fetchall()

        all_articles = []
        category_names = []
        country_names = []

        for category_id, country_id in user_preferences:
            # Fetch category name
            cursor.execute("SELECT category_name FROM Category WHERE category_id = ?", (category_id,))
            category_name = cursor.fetchone()[0] if category_id else None
            if category_name:
                category_names.append(category_name)
            # Fetch country name
            cursor.execute("SELECT country_name FROM Country WHERE country_id = ?", (country_id,))
            country_name = cursor.fetchone()[0] if country_id else None
            if country_name:
                country_names.append(country_name)

        for country in country_names:
            for category in category_names:
                params = {
                    'country': country,
                    'category': category,
                    'pageSize': 5,
                    'apiKey': NEWSAPI_KEY,
                }
                response = requests.get(BASE_URL, params=params)
                data = response.json()
                articles = data.get('articles', [])

                # Filter out articles that have been removed or have missing data
                valid_articles = [article for article in articles if article.get('title')
                                  and article.get('url')
                                  and article.get('description') != '[Removed]'
                                  and article.get('content') != '[Removed]'
                                  and article.get('publishedAt') != '1970-01-01T00:00:00Z']

                for article in valid_articles:
                    article['category'] = category
                    article['country'] = country
                    all_articles.append(article)

        return jsonify({'articles': all_articles}), 200

    except Exception as e:
        print('Error:', e)
        return jsonify({'message': 'An error occurred while processing the request'}), 500


@app.route('/get_username', methods=['POST'])
def get_username():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        print(user_id)

        if not user_id:
            return jsonify({'message': 'User ID is missing in the request'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM User WHERE user_id = ?", (user_id,))
        username = cursor.fetchone()[0]
        conn.close()

        return jsonify({'username': username}), 200

    except Exception as e:
        print('Error:', e)
        return jsonify({'message': 'An error occurred while processing the request'}), 500

# Logout route
@app.route('/logout', methods=['POST'])
def logout():
    try:
        # Assuming user_id is sent in the request payload
        user_id = request.json.get('user_id')
        
        if user_id:
            # Update the logout timestamp in the Activity table
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE Activity SET logout_timestamp = ? WHERE user_id = ? AND logout_timestamp IS NULL", (datetime.now(), user_id))
            conn.commit()
            conn.close()

            return jsonify({'message': 'Logout successful'}), 200
        else:
            return jsonify({'error': 'User ID not provided'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/feedback', methods=['POST'])
def feedback():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        feedback = data.get('feedback')
        print(user_id,feedback)
        if not user_id or not feedback:
            return jsonify({'message': 'User ID or feedback is missing in the request'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Feedback (user_id, feedback_text, feedback_date) VALUES (?, ?, ?)", (user_id, feedback, datetime.now()))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Feedback submitted successfully'}), 201

    except Exception as e:
        print('Error:', e)
        return jsonify({'message': 'An error occurred while processing the request'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
