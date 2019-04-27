from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy
import cgi
import os
import jinja2

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)



class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, body, owner):
        self.name = name
        self.body = body
        self.owner = owner
        
    def __repr__(self):
        return '<Blog %r>' % self.name

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    blogs = db.relationship('Blog', backref='owner') 

    def __init__(self, username, password):
        self.username = username
        self.password = password    

 

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'show_blogs', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/', methods=['POST','GET'])
def index():
    user_id = request.args.get('id')
    username = request.args.get('username')
    if user_id == None:
        users = User.query.all()
        return render_template('index.html', users=users)
        



@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    owner = User.query.filter_by(username=session['username']).first()
    if request.method == 'POST':
        blog_name = request.form['blog_name']
        blog_body = request.form['blog_body']
        
        if blog_name == '' or blog_body == '':
            flash("Please enter a valid Blog Title or Content!")
            return render_template('blog_post.html', blog_body = blog_body, blog_name = blog_name)
        
        new_blog = Blog(blog_name, blog_body, owner)
        db.session.add(new_blog)
        db.session.commit()        
        return redirect('/blog?id={}'.format(new_blog.id))
        
    blogs = Blog.query.all()
    return render_template('blog_post.html',title="Build A Blog!", 
        blogs=blogs)

     


@app.route('/blog', methods=['POST', 'GET'])
def show_blogs():
    blog_id = request.args.get('id')
    blog_name = request.args.get('name')
    blog_body = request.args.get('body')
    user = request.args.get('owner_id')

    if blog_id:
        blogs = Blog.query.filter_by(id=blog_id).first()
        return render_template('blog_entry.html', blog=blogs)
    if user:
        blogs_by_user = Blog.query.filter_by(owner_id=user)
        return render_template('singleUser.html', blogs=blogs_by_user)
    blogs = Blog.query.all()
    return render_template('blogs_view.html', blogs=blogs)
  
    

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        user_password = User.query.filter_by(password=password).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        
        if not user:
            flash('That username does not exist!')
            return redirect('/login')
        if password != user_password:
            flash('Incorrect password!')
            return redirect('/login')

    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if username == '' or password == '' or verify == '':
            flash('One or more fields are invalid!')
            return redirect('/signup')

        if password != verify:
            flash('Passwords do not match!')  
            return redirect('/signup')  

        if len(username) < 3:
            flash('Username must be at least 3 characters long!')
            return redirect('/signup')

        if len(password) < 3:  
            flash('Password must be at least 3 characters long!')  
            return redirect('/signup')

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            flash('That username already exists!')
            return redirect('/signup')

    return render_template('signup.html')


@app.route("/logout", methods=['POST', 'GET'])
def logout():
    del session['username']
    return redirect('/blog')

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RU'

if __name__ == '__main__':
    app.run()