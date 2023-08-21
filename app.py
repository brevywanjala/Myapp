from flask import *
from flask_caching import Cache
from difflib import SequenceMatcher
import sqlite3
from werkzeug.security import check_password_hash,generate_password_hash
from flask_mail import Mail
from datetime import datetime
import secrets
import datetime
import time
from pytube import YouTube



import webbrowser



import threading
import webbrowser
import os
import sys


app = Flask(__name__)

app.config['CACHE_TYPE'] = 'simple'
app.secret_key="aaajdakhaj"# You can also use 'redis' or other caching backends
cache = Cache(app)
home_dir = os.path.expanduser("~")
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] =True
app.config["MAIL_USE_SSL"]=False
app.config['MAIL_USERNAME'] = 'brevywanjala1@gmail.com'  # Your Gmail email
app.config['MAIL_PASSWORD'] = 'qnuypgygbskcimpd'  # Your Gmail password or app password
mail = Mail(app)

# Specify your application's name

UPLOAD_FOLDER = os.path.join(app.root_path, 'static/uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Ensure the directory exists


# Specify the database file path
DATABASE ="MyYoutube.db"
# SQLite database setup
def setup_database():
    connection = sqlite3.connect(DATABASE)  # Replace with your database file name
    cursor = connection.cursor()
    # cursor.execute("""DROP TABLE IF EXISTS videos
    #                """)
  
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY,
        name TEXT,
        video_id TEXT,
        user_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    # Create the password recovery tokens table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recovery_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            token TEXT,
            expiration DATETIME,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
        

    # videos_to_insert = [
    #     ('source of money', 'qOaTaK0oVFk'),
    #     ('source of wealth', 'p1GmFCGuVjw'),
    #     ('coding tutorial', 'H8ThscWsQV8'),
    #     ('flask', 'VE8BkImUciY'),
    #     ('importance of love', '520Du4aXqKg'),
    #     ('being loved', 'NYjTGl6YLKQ'),
    #     ('loving songs', 'vIyU4nInlt0'),
    #     ('songs of love', 'ByIdnfMFG3E'),
    #     # Add more videos as needed
    # ]

    # cursor.executemany('INSERT INTO videos (name, id) VALUES (?, ?)', videos_to_insert)
    connection.commit()
    connection.close()

setup_database()
def download_video(url, save_path):
    try:
        yt = YouTube(url)
        video_stream = yt.streams.get_highest_resolution()
        video_path = os.path.join(save_path, yt.title + ".mp4")
        video_stream.download(output_path=save_path, filename=yt.title + ".mp4")
        print("Download successful!")
        return video_path
    except Exception as e:
        print("Error:", e)
        return None

@app.route("/downloaded", methods=["GET", "POST"])
def downloaded():
    if request.method == "POST":
        video_url = request.form["video_url"]
        save_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static/uploads")
        video_path = download_video(video_url, save_directory)
        print("video path",video_path)
        if video_path:
            return redirect(url_for("watch_video", video_path=video_path))
    flash('you can copy videos using the icon below each', 'warning')  # Passing 'warning' category
    
    return render_template("downloaded.html")

@app.route("/watch/<path:video_path>")
def watch_video(video_path):
    return send_file(video_path)

@app.route("/progress")
def progress():
    def generate():
        for progress in range(0, 101, 10):
            yield f"data: {progress}\n\n"
            time.sleep(1)  # Simulate a delay
    return Response(generate(), content_type="text/event-stream")


@app.route('/admin')
def admin_dashboard():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # Get user count and usernames
    cursor.execute("SELECT COUNT(id) FROM users")
    user_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT username FROM users")
    usernames = [row[0] for row in cursor.fetchall()]
    
    connection.close()
    
    
    return render_template('admin_dashboard.html', user_count=user_count, usernames=usernames)
@app.route('/delete_all', methods=['POST'])
def delete_all_files():
    for video_file in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], video_file)
        if os.path.exists(file_path):
            os.remove(file_path)
    flash('All videos deleted successfully', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/about')
def about():
    return render_template("about.html",)
@app.route('/login', methods=['GET', 'POST'])
def login():
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        connection.close()

        if user and check_password_hash(user[3], password):  # Check the hashed password
            session['user_id'] = user[0]  # Store the user ID in the session
            flash('Logged in successfully!', 'success')
            return redirect('/')
        else:
            flash('Invalid email or password. Please try again.', 'error')

    return render_template('login.html')
@app.route('/delete/video/<string:video_id>', methods=['POST'])
def delete_video(video_id):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    user_id=session.get("user_id")
    
    cursor.execute("DELETE FROM videos WHERE video_id = ? AND user_id= ?", (video_id,user_id))
    connection.commit()
    connection.close()
    
    flash("Video deleted successfully",'success')
    return redirect("/")


@app.route('/insert/video/id', methods=['POST'])
def insertVideo_id():
    if 'user_id' not in session:
        return redirect('/login')

    name = request.form.get('name')
    video_id = request.form.get('id')
    user_id = session.get('user_id')
    print(user_id,"user_id")
    if len(name) < 25:
        flash("Video name must be at least 25 characters long",'warning')
        return redirect("/")# Use parentheses instead of square brackets
    if len(video_id) > 20:
        flash("Please provide a valid video id (maximum 20 characters)",'warning')
        return redirect('/')

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    try:
        cursor.execute("INSERT INTO videos (name, video_id, user_id) VALUES (?, ?, ?)", (name, video_id, user_id))
        connection.commit()
        flash("Video saved successfully",'success')
    except sqlite3.Error as e:
        print("SQLite error:", e)
        flash("An error occurred while saving the video",'error')

    connection.close()
    return redirect('/')
from flask_mail import Message
@app.route('/recover_password', methods=['GET', 'POST'])
def recover_password():
    if request.method == 'POST':
        email = request.form.get('email')

        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()

        # Check if the email exists in the password_backup table
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        user_id = cursor.fetchone()

        if user_id:
            # Generate a recovery token and store it with the user's email
            recovery_token = secrets.token_urlsafe(32)
            expiration_time = datetime.datetime.now() + datetime.timedelta(hours=1)
            cursor.execute("INSERT INTO recovery_tokens (user_id, token, expiration) VALUES (?, ?, ?)",
                        (user_id[0], recovery_token, expiration_time))
            connection.commit()

            # Send recovery email with the recovery link
            recovery_link = url_for('reset_password', token=recovery_token, _external=True)
            msg = Message("Password Recovery", sender="brevywanjala1@gmail.com", recipients=[email])
            msg.body = f"Click the following link to reset your password: {recovery_link}"
            mail.send(msg)  # Send the email
            print("success",msg)
            flash("Password recovery link sent to your email.",'success')

        connection.close()

    return render_template('recover_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # Check if the token exists and is not expired
    cursor.execute("SELECT user_id, expiration FROM recovery_tokens WHERE token = ?", (token,))
    recovery_info = cursor.fetchone()

    if recovery_info and datetime.datetime.strptime(recovery_info[1], "%Y-%m-%d %H:%M:%S.%f") > datetime.datetime.now():
        user_id = recovery_info[0]

        if request.method == 'POST':
            new_password = request.form.get('new_password')
            confirm_password=request.form.get("confirm_password")
            
            if new_password != confirm_password:
                flash("Password mismatch", "error")
                connection.close()
                return redirect(url_for("reset_password", token=token))
            # Update the user's password in the password_backup table
            hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
            cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, user_id))
            connection.commit()

            # Delete the recovery token
            cursor.execute("DELETE FROM recovery_tokens WHERE token = ?", (token,))
            connection.commit()

            flash("Password reset successful. You can now log in with your new password.",'success')
            connection.close()
            return redirect('/login')

        connection.close()
        return render_template('reset_password.html', token=token)
    else:
        flash("Invalid or expired recovery link.",'error')
        connection.close()
        return redirect('/recover_password')
        
@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user ID from the session
    flash('Logged out successfully!','success')
    return redirect('/')
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Extract user signup data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Check if password and confirm_password match
        if password != confirm_password:
            flash("Passwords do not match",'error')
            return redirect("/signup")

        # Hash the password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        existing_user = cursor.fetchone()
       
        

        try:
            # Insert user data into users table
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, hashed_password))
            user_id = cursor.lastrowid  # Get the newly inserted user's ID
            connection.commit()

            # Call function to insert default videos
            insert_default_videos(cursor, connection, user_id)

            flash("Signup successful! You can now log in.",'success')
            connection.close()
            return redirect("/login")
        except sqlite3.Error as e:
            print("SQLite error:", e)
            flash("An error occurred during signup",'error')
            connection.rollback()
            connection.close()
            return redirect("/signup")

    return render_template('signup.html')


  # Create a signup.html template for the signup form



@app.route('/')
def get_videos():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session.get('user_id')
    print("user_d",user_id)# Get the user_id from the session
    
    connection = sqlite3.connect(DATABASE)  # Replace with your database file name
    cursor = connection.cursor()

    search_query = request.args.get('query', '')
    video_data = []
    if not search_query:
        direct_query = f"SELECT name, video_id FROM videos WHERE user_id = ? ORDER BY RANDOM() LIMIT 8"
        cursor.execute(direct_query, (user_id,))
        video_data = [{'name': name, 'video_id': video_id} for name, video_id in cursor.fetchall()]  # Get 3 random videos
        
    else:
        # Direct LIKE query
        direct_query = f"SELECT name, video_id FROM videos WHERE user_id = ? AND name LIKE ? LIMIT 5"
        cursor.execute(direct_query, (user_id, f'%{search_query}%'))
        video_data = [{'name': name, 'video_id': video_id} for name, video_id in cursor.fetchall()]

        # Sequence matching if direct query returns nothing
        if not video_data:
            all_video_data = [{'name': name, 'video_id': video_id} for name, video_id in cursor.execute("SELECT name, video_id FROM videos WHERE user_id = ?", (user_id,))]
            similar_videos = []
            for video in all_video_data:
                similarity_ratio = SequenceMatcher(None, search_query, video['name']).ratio()
                if similarity_ratio > 0.6:  # Adjust the similarity threshold as needed
                    similar_videos.append((video['name'], video['video_id'], similarity_ratio))
            similar_videos.sort(key=lambda x: x[2], reverse=True)  # Sort by similarity ratio
            video_data = [{'name': name, 'video_id': video_id} for (name, video_id, _) in similar_videos[:5]]

    connection.close()
    return render_template('youtube.html', api_key='AIzaSyCg3igPsBULULoDCtFo9Uq0VMsbBsBJ6E8', videos=video_data)

def insert_default_videos(cursor, connection, user_id):
    # Insert default video data for the new user
    default_videos = [
        ("5 Lessons I Learned From Elon Musk | Best Motivational Advice 2023", "tBGBVj_eEEs"),
        ("SCHOOL SYSTEM IS BROKEN ft Elon Musk, Robert Kiyosaki, Andrew Tate, Steve Harvey, Kim Kiyosaki", "IG2zSQ27VFQ"),
        ("The Science of Flirting: Being a H.O.T. A.P.E. | Jean Smith | TEDxLSHTM", "5cQoGNEcc5Q"),
        ("Elon Musk's Speech Will Leave You SPEECHLESS | One of the Most Eye Opening Speeches Ever 2022", "zlDmYkeQpVQ"),
        ("Brutally Honest Advice From Steve Jobs | BEST SPEECH Ever! (HQ Version)", "5Yhf0wBFtvY"),
        ("One of The Greatest Speeches Ever by President Obama | Best Eye Opening Speech", "NaaSpRMBHjg"),
        ("Elon Musk MOST SHOCKING INTERVIEW With AI!", "dUhvvoVtpVE"),
        ("Watch Ameca the humanoid robot in its FIRST public demo", "LzBUm31Vn3k"),
        ("Good Vibes Music 🌻 Popular Tiktok Songs 2023 ~ English Songs For Ringtones", "-RsAP6A5rNs"),
        ("LET HER GO PASSENGER (REMIX) TERBARU", "j0e7SjaVJqA"),
        ("Good Mood Songs🥝 Vibes to start your day | Trending Tiktok songs with Lyrics", "G16LAw5u-GI"),
        
         
        # Add more default videos as needed
    ]
    for name, video_id in default_videos:
        cursor.execute("INSERT INTO videos (name, video_id, user_id) VALUES (?, ?, ?)", (name, video_id, user_id))
        connection.commit()


if __name__ == '__main__':
     # Hide the console window
    setup_database()
    app.run(host='0.0.0.0', port=5000)
    
    
    
