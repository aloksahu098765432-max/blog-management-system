from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "blogsecret"


def init_db():

    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            author TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER,
            username TEXT,
            comment TEXT
        )
    ''')

    conn.commit()
    conn.close()


init_db()


@app.route('/')
def home():

    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()

    conn.close()

    return render_template('index.html', posts=posts)


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('blog.db')
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )

        conn.commit()
        conn.close()

        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('blog.db')
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:
            session['user'] = username
            return redirect(url_for('home'))

        return "Invalid Username or Password"

    return render_template('login.html')


@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect(url_for('home'))


@app.route('/create_post', methods=['GET', 'POST'])
def create_post():

    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':

        title = request.form['title']
        content = request.form['content']

        conn = sqlite3.connect('blog.db')
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO posts (title, content, author) VALUES (?, ?, ?)",
            (title, content, session['user'])
        )

        conn.commit()
        conn.close()

        return redirect(url_for('home'))

    return render_template('create_post.html')


@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):

    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()

    if request.method == 'POST':

        title = request.form['title']
        content = request.form['content']

        cursor.execute(
            "UPDATE posts SET title=?, content=? WHERE id=?",
            (title, content, post_id)
        )

        conn.commit()
        conn.close()

        return redirect(url_for('home'))

    cursor.execute(
        "SELECT * FROM posts WHERE id=?",
        (post_id,)
    )

    post = cursor.fetchone()

    conn.close()

    return render_template('edit_post.html', post=post)


@app.route('/delete_post/<int:post_id>')
def delete_post(post_id):

    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM posts WHERE id=?",
        (post_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for('home'))


@app.route('/post/<int:post_id>')
def view_post(post_id):

    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM posts WHERE id=?",
        (post_id,)
    )

    post = cursor.fetchone()

    cursor.execute(
        "SELECT * FROM comments WHERE post_id=?",
        (post_id,)
    )

    comments = cursor.fetchall()

    conn.close()

    return render_template(
        'post.html',
        post=post,
        comments=comments
    )


@app.route('/add_comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):

    if 'user' not in session:
        return redirect(url_for('login'))

    comment = request.form['comment']

    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO comments (post_id, username, comment) VALUES (?, ?, ?)",
        (post_id, session['user'], comment)
    )

    conn.commit()
    conn.close()

    return redirect(url_for('view_post', post_id=post_id))


if __name__ == "__main__":
    app.run(debug=True)