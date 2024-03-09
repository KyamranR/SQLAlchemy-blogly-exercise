"""Blogly application."""

from flask import Flask, render_template, request, redirect, url_for
from models import db, connect_db, User, Post
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)

dt = datetime.utcnow()
formatted_dt = dt.strftime('%Y-%m-%d %H:%M:%S')

with app.app_context():
    db.create_all()
# this is creating user route
@app.route('/')
def redirect_to_users():
    return redirect(url_for('list_users'))

@app.route('/users')
def list_users():
    users = User.query.all()
    return render_template('list_users.html', users=users)

@app.route('/users/new', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        image_url = request.form['image_url']
        new_user = User(first_name=first_name, last_name=last_name, image_url=image_url)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('list_users'))
    return render_template('add_user.html')


@app.route('/users/<int:user_id>')
def show_user(user_id):
    user = User.query.get_or_404(user_id)
    posts = user.posts
    return render_template('show_user.html', user=user, posts=posts)

@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.image_url = request.form['image_url']
        db.session.commit()
        return redirect(url_for('list_users'))
    return render_template('edit_user.html', user=user)

@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('list_users'))

# this is creating post route

@app.route('/users/<int:user_id>/posts/new', methods=['GET', 'POST'])
def add_post(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        post = Post(title=title, content=content, created_at=formatted_dt, user_id=user_id)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('show_post', post_id=post.id))
    return render_template('new_post.html', user=user)


@app.route('/posts/<int:post_id>')
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    user = post.user
    return render_template('show_post.html', post=post, user=user)

@app.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()
        return redirect(url_for('show_post', post_id=post_id))
    return render_template('edit_post.html', post=post)

@app.route('/posts/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    user_id = post.user_id
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('show_user', user_id=user_id))


if __name__ == '__main__':
    app.run(debug=True)