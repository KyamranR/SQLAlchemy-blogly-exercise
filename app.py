"""Blogly application."""

from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, connect_db, User, Post, Tag, PostTag
from datetime import datetime
from sqlalchemy.exc import IntegrityError

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
    """Rediceting to the main page"""
    return redirect(url_for('list_users'))

@app.route('/users')
def list_users():
    """Listing the users"""
    users = User.query.all()
    return render_template('list_users.html', users=users)

@app.route('/users/new', methods=['GET', 'POST'])
def add_user():
    """Adding the user"""
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
    """Showing all the users"""
    user = User.query.get_or_404(user_id)
    posts = user.posts
    tags = Tag.query.all()
    return render_template('show_user.html', user=user, posts=posts, tags=tags)

@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_user(user_id):
    """Editing the user"""
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
    """Deleting the user"""
    user = User.query.get_or_404(user_id)

    if user.posts:
        for post in user.posts:
            db.session.delete(post)
            
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('list_users'))

# this is creating post route

@app.route('/users/<int:user_id>/posts/new', methods=['GET', 'POST'])
def add_post(user_id):
    """Adding the post"""
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        tag_ids = request.form.getlist('tags')
        post = Post(title=title, content=content, created_at=formatted_dt, user_id=user_id)
        

        for tag_id in tag_ids:
            tag = Tag.query.get(tag_id)
            if tag:
                post.tags.append(tag)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('show_post', post_id=post.id))
    tags = Tag.query.all()
    return render_template('new_post.html', user=user, tags=tags)


@app.route('/posts/<int:post_id>')
def show_post(post_id):
    """Showing the post"""
    post = Post.query.get_or_404(post_id)
    user = post.users
    tags = post.tags
    return render_template('show_post.html', post=post, user=user, tags=tags)

@app.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    """Editing the post"""
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        tag_ids = request.form.getlist('tags')
        post.tags.clear()
        for tag_id in tag_ids:
            tag = Tag.query.get(tag_id)
            if tag:
                post.tags.append(tag)
        try:
            db.session.commit()
            flash('Post updated successfully', 'success')
            return redirect(url_for('show_post', post_id=post.id))
        except IntegrityError:
            db.session.rollback()
            flash('Error: Duplicate tag association', 'danger')
        return redirect(url_for('show_post', post_id=post_id))
    tags = Tag.query.all()
    return render_template('edit_post.html', post=post, tags=tags)

@app.route('/posts/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    """Deleting the post"""
    post = Post.query.get_or_404(post_id)
    user_id = post.user_id
    post_tags = PostTag.query.filter_by(post_id=post_id).all()
    for post_tag in post_tags:
        db.session.delete(post_tag)

    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('show_user', user_id=user_id))


# creating tags

@app.route('/tags')
def list_tags():
    """Listing the tags"""
    tags = Tag.query.all()
    user = User.query.first()
    return render_template('list_tags.html', tags=tags, user=user)

@app.route('/tags/<int:tag_id>')
def show_tags(tag_id):
    """Show tag details"""
    tag = Tag.query.get_or_404(tag_id)
    return render_template('show_tag.html', tag=tag)

@app.route('/tags/new', methods=['GET', 'POST'])
def add_tag():
    """Add a new tag"""
    if request.method == 'POST':
        name = request.form['name']
        tag = Tag(name=name)
        db.session.add(tag)
        db.session.commit()
        flash('Tag added successfully!', 'success')
        return redirect(url_for('list_tags'))
    return render_template('add_tag.html')

@app.route('/tags/<int:tag_id>/edit', methods=['GET', 'POST'])
def edit_tag(tag_id):
    """Editing a tag"""
    tag = Tag.query.get_or_404(tag_id)
    if request.method == 'POST':
        tag.name = request.form['name']
        db.session.commit()
        flash('Tag updated succcessfully', 'success')
        return redirect(url_for('list_tags'))
    
    return render_template('edit_tag.html', tag=tag)

@app.route('/tags/<int:tag_id>/delete', methods=['POST'])
def delete_tag(tag_id):
    """Deleting a tag"""
    tag = Tag.query.get_or_404(tag_id)
    
    db.session.delete(tag)
    db.session.commit()
    
    flash('Tag deleted successfully!', 'success')
    return redirect(url_for('list_tags'))        




if __name__ == '__main__':
    app.run(debug=True)