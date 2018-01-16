from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:Connor123@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    entry = db.Column(db.String(5000))

    def __init__(self, title, entry):
        self.title = title
        self.entry = entry
        
@app.route('/')
def index():
    blogs = Blog.query.all()
    return render_template('blog.html', header = "My Blog", blogs=blogs)

@app.route('/newpost', methods=['GET'])
def newpost():
    return render_template('newpost.html', header = "Add a new Entry")

@app.route('/newpost', methods=['POST', 'GET'])
def validate_entry():
    title = request.form['title']
    entry = request.form['entry']

    title_error = ""
    entry_error =""

    if title == "":
        title_error = "You must have a title"

    if entry == "":
        entry_error = "You must have enter content"

    if not title_error and not entry_error:
        title_name = request.form['title']
        entry_content = request.form['entry']
        new_entry = Blog(title_name, entry_content)
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
    post = Blog.query.filter_by(id=entry_id).all()
    
    return render_template('entry.html', post=post)

if __name__ == '__main__':
    app.run()