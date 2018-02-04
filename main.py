from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:Connor123@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    entry = db.Column(db.String(5000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, entry, owner):
        self.title = title
        self.entry = entry
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password     

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'index', 'list_blogs']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')  

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', header = "Home", users=users)

@app.route('/blogs', methods=['POST', 'GET'])
def list_blogs():
    selected_user = request.args.get('user')
    if not selected_user:
        user = User.query.all()
        blogs = Blog.query.join(User).all()
        return render_template('listblogs.html', header = "Blogz", blogs=blogs, user=user)
    else:
        user = User.query.filter_by(username=selected_user).first()
        blogs = Blog.query.filter_by(owner=user).join(User).all()
        return render_template('listblogs.html', header = "Blogz", blogs=blogs, user=user)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        if user and user.password == password:
            flash('User password incorrect', 'error')
            password = ""
            verify = ""
            return render_template('login.html', username = username,
            password = password, verify = verify)

        else:
            flash('User does not exist', 'error')
            password = ""
            verify = ""
            return render_template('login.html', username = username,
            password = password, verify = verify)


    return render_template('login.html', header ="Login")

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        username_error = ""
        password_error = ""
        verify_error = ""

        if username == "":
            username_error = "This is a required field"

        if username != "":    
            if " " in username:
                username_error = "No spaces allowed in username"
            if len(username) < 3 or len(username) > 20:
                username_error = "Username must be 3 - 20 characters"
        
        if password == "":
            password_error = "This is a required field"
        
        if password != "":    
            if len(password) < 3 or len(password) > 20:
                password_error = "Password must be 3 - 20 characters"
        
        if verify == "":
            verify_error = "This is a required field"

        if password != verify:
            verify_error="Passwords do not match!"

        if not username_error and not password_error and not verify_error:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            else:
                flash('Duplicate User', 'error')
        else:
            password = ""
            verify = ""
            return render_template('register.html', username = username, username_error = username_error,
            password = password, password_error = password_error, verify = verify, 
            verify_error = verify_error)

    return render_template('register.html', header ="Register")

@app.route('/newpost', methods=['GET'])
def newpost():
    return render_template('newpost.html', header = "Add a new Entry")

@app.route('/newpost', methods=['POST', 'GET'])
def validate_entry():
    title = request.form['title']
    entry = request.form['entry']
    owner = User.query.filter_by(username=session['username']).first()

    title_error = ""
    entry_error =""

    if title == "":
        title_error = "You must have a title"

    if entry == "":
        entry_error = "You must have enter content"

    if not title_error and not entry_error:
        title_name = request.form['title']
        entry_content = request.form['entry']
        new_entry = Blog(title_name, entry_content, owner)
        db.session.add(new_entry)
        db.session.commit()
        entry_number = new_entry.id
        return redirect('/entry?id={0}'.format(entry_number))
    else:
        return render_template('newpost.html', title = title, entry = entry, 
    title_error = title_error, entry_error = entry_error)

@app.route('/entry', methods= ['GET', 'POST'])
def entry_display():
    entry_id = request.args.get('id')
    post = Blog.query.filter_by(id=entry_id).join(User).all()
    
    return render_template('entry.html', post=post)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blogs')

if __name__ == '__main__':
    app.run()