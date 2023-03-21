from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, \
    ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, Length
from wtforms.widgets import TextArea
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

# Create a Flask instance
app = Flask(__name__)
# Add Database
# Old SQLITE DB
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# New MYSQL DB
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'mysql+pymysql://root:password123@localhost/our_users'
# Secret Key
app.config['SECRET_KEY'] = "my_super_secret_key"
# Initialize Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Create Blog Post Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))


# Create a Post Form
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = StringField("Content", validators=[DataRequired()],
                          widget=TextArea())
    author = StringField("Author", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Add Post Page
@app.route('/add-post', methods=['GET', 'POST'])
def add_post():
    form = PostForm()
    # Validate The Form
    if form.validate_on_submit():
        post = Posts(title=form.title.data, content=form.content.data,
                     author=form.author.data, slug=form.slug.data)
        # Clear The Form
        form.title.data = ''
        form.content.data = ''
        form.author.data = ''
        form.slug.data = ''

        # Add Post To Database
        with app.app_context():
            db.session.add(post)
            db.session.commit()

        # Return a Massage
        flash("Blog Post Submitted Successfully!")

    # Redirect to Webpage
    return render_template('add_post.html', form=form)


# Create Blog Page
@app.route('/posts')
def posts():
    # Get all the posts from the database
    posts = Posts.query.order_by(Posts.date_posted.desc())

    # Redirect to Webpage
    return render_template('posts.html', posts=posts)


# View Of The Post
@app.route('/posts/<int:id>')
def post(id):
    # Get the post from the database
    post = Posts.query.get_or_404(id)

    # Redirect to Webpage
    return render_template('post.html', post=post)


# Edit Of The Post
@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    # Get the post from the database
    post = Posts.query.get_or_404(id)
    form = PostForm()

    # Validate The Form
    if form.validate_on_submit():

        #Update Data
        post.title = form.title.data
        post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data

        # Update Database
        db.session.commit()

        # Return a Massage
        flash("Post Has Been Updated!")

        # Redirect to Webpage
        return redirect(url_for('post', id=post.id))

    #Fill Out The Form Of Updating
    form.title.data = post.title
    form.author.data = post.author
    form.slug.data = post.slug
    form.content.data = post.content

    # Redirect to Webpage
    return render_template('edit_post.html', form=form)


# Delete Of The Post
@app.route('/posts/delete/<int:id>')
def delete_post(id):
    # Get the post from the database
    post_to_delete = Posts.query.get_or_404(id)

    try:
        # Delete From Database
        db.session.delete(post_to_delete)
        db.session.commit()

        # Return a Massage
        flash('Blog Post Was Deleted!')

        # Get all the posts from the database
        posts = Posts.query.order_by(Posts.date_posted.desc())

        # Redirect to Webpage
        return render_template('posts.html', posts=posts)

    except:
        # Return an Error Massage
        flash('Oops! There was a problem with deleting, try again...')

        # Get all the posts from the database
        posts = Posts.query.order_by(Posts.date_posted.desc())

        # Redirect to Webpage
        return render_template('posts.html', posts=posts)


# Create User Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    # Make password
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Name %r>' % self.name


# Create User Form
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    password_hash = PasswordField('Password', validators=[DataRequired(),
                                                          EqualTo(
                                                              'password_hash2',
                                                              message='Passwords Must Match!')])
    password_hash2 = PasswordField('Confirm Password',
                                   validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create Form Class
class NamerForm(FlaskForm):
    name = StringField("What`s Your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create Password Form
class PasswordForm(FlaskForm):
    email = StringField("What`s Your Email", validators=[DataRequired()])
    password_hash = PasswordField("What`s Your Password",
                                  validators=[DataRequired()])
    submit = SubmitField("Submit")


# Add NEW Database Record
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash the password
            hashed_pw = generate_password_hash(form.password_hash.data)

            user = Users(name=form.name.data, email=form.email.data,
                         favorite_color=form.favorite_color.data,
                         password_hash=hashed_pw)
            with app.app_context():
                db.session.add(user)
                db.session.commit()
            name = form.name.data
            form.name.data = ''
            form.email.data = ''
            form.favorite_color.data = ''
            form.password_hash.data = ''

            flash("User Added Successfully")
    our_users = Users.query.order_by(Users.date_added)
    return render_template('add_user.html', form=form, name=name,
                           our_users=our_users)


# Update Database Record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        try:
            db.session.commit()
            flash('User Updated Successfully!')
            return render_template('update.html',
                                   name_to_update=name_to_update, form=form)
        except:
            flash('Error with Updating!!')
            return render_template('update.html',
                                   name_to_update=name_to_update, form=form)
    return render_template('update.html',
                           name_to_update=name_to_update, form=form, id=id)


# Delete Database Record
@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('User Deleted Successfully!')
        our_users = Users.query.order_by(Users.date_added)
        return render_template('add_user.html', form=form, name=name,
                               our_users=our_users)
    except:
        flash('Error with Deleting!!')
        our_users = Users.query.order_by(Users.date_added)
        return render_template('add_user.html', form=form, name=name,
                               our_users=our_users)


# Create route decorator
@app.route('/')
def index():
    first_name = 'John'
    favorite_pizza = ['Pepperoni', 'Cheese', 'Mushrooms', 41]
    return render_template('index.html',
                           first_name=first_name,
                           favorite_pizza=favorite_pizza)


# http://127.0.0.1:5000/user/John
@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


# Invalid URL
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


# Internal Server Error
@app.errorhandler(500)
def page_not_found(error):
    return render_template('500.html'), 500


# Create Name Page
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    # Validate Form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submitted Successfully")
    return render_template('name.html', name=name, form=form)


# Create Password Test Page
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()

    # Validate Form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        form.email.data = ''
        form.password_hash.data = ''

        # Lookup user by email
        pw_to_check = Users.query.filter_by(email=email).first()

        # Check hash password
        passed = check_password_hash(pw_to_check.password_hash, password)

    return render_template('test_pw.html', email=email, password=password,
                           form=form, pw_to_check=pw_to_check, passed=passed)


if __name__ == '__main__':
    app.run(debug=True)
