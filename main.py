from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy
import cgi
import os
import jinja2

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    body = db.Column(db.String(500))
    

    def __init__(self, name, body):
        self.name = name
        self.body = body
        
    def __repr__(self):
        return '<Blog %r>' % self.name

@app.route('/newpost', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':
        blog_name = request.form['blog_name']
        blog_body = request.form['blog_body']
        
        if blog_name == '' or blog_body == '':
            flash("Please enter a valid Blog Title or Content!")
            return render_template('blog_post.html', blog_body = blog_body, blog_name = blog_name)
        
        new_blog = Blog(blog_name, blog_body)
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
    if blog_id == None:
        blogs = Blog.query.all()
        return render_template('blogs_view.html', blogs=blogs)

    else:
        blogs = Blog.query.filter_by(id=blog_id).first()
        return render_template('blog_entry.html', blog=blogs)


# def show_blogs():
#     id = request.args.get(Blog.id)
#     single_blog = Blog.query.filter_by(id=id).first()
#     blogs = Blog.query.all()
#     if id == single_blog:
#         return render_template('blog_entry.html', blogs=blogs)
#     return render_template('blogs_view.html', blogs=blogs)

# def single_blog():
#     single_blog = Blog.query.filter_by(blog_id=blog_id).first()
#     return render_template('blog_entry.html', blog_name=blog_name, blog_body=blog_body)


app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RU'

if __name__ == '__main__':
    app.run()