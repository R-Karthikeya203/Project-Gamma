from flask import Flask, render_template, redirect, url_for, flash, request, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate 
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect
from forms import RegisterForm, LoginForm, ProjectForm, TaskForm, CommentForm, FileUploadForm
from models import db, User, Project, Task, Comment, File
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)


db.init_app(app)
migrate = Migrate(app, db)  
csrf = CSRFProtect(app)


if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        new_user = User(
            email=form.email.data,
            username=form.username.data,
            password=hashed_pw,
            role=form.role.data
        )
        db.session.add(new_user)
        db.session.commit()
        flash('User registered!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.get(form.email.data)
        if user and check_password_hash(user.password, form.password.data):
            session['user_email'] = user.email
            session['user_role'] = user.role
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_email' not in session:
        return redirect(url_for('login'))

    if session['user_role'] == 'admin':
        tasks = Task.query.all()
    else:
        tasks = Task.query.filter_by(assigned_to_email=session['user_email']).all()

    return render_template('dashboard.html', tasks=tasks, user=session)

@app.route('/project/create', methods=['GET', 'POST'])
def create_project():
    if session.get('user_role') != 'admin':
        flash("Admins only.", "danger")
        return redirect(url_for('dashboard'))
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(title=form.title.data, description=form.description.data)
        db.session.add(project)
        db.session.commit()
        flash('Project created!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('create_project.html', form=form)

@app.route('/task/create', methods=['GET', 'POST'])
def create_task():
    if session.get('user_role') != 'admin':
        flash("Admins only.", "danger")
        return redirect(url_for('dashboard'))
    form = TaskForm()
    if form.validate_on_submit():
        user = User.query.get(form.assigned_to_email.data)
        if not user:
            flash("User with that email not found.", "danger")
            return redirect(url_for('create_task'))
        task = Task(
            title=form.title.data,
            description=form.description.data,
            assigned_to_email=user.email,
            project_id=int(form.project_id.data)
        )
        db.session.add(task)
        db.session.commit()
        flash('Task created and assigned.', 'success')
        return redirect(url_for('dashboard'))
    return render_template('create_task.html', form=form)

@app.route('/task/<int:task_id>', methods=['GET', 'POST'])
def task_detail(task_id):
    task = Task.query.get_or_404(task_id)
    comments = Comment.query.filter_by(task_id=task_id).all()
    form = CommentForm()
    if form.validate_on_submit():
        new_comment = Comment(
            content=form.content.data,
            task_id=task_id,
            user_email=session['user_email']
        )
        db.session.add(new_comment)
        db.session.commit()
        flash('Comment added.', 'success')
        return redirect(url_for('task_detail', task_id=task_id))
    return render_template('task_detail.html', task=task, comments=comments, form=form)

@app.route('/task/<int:task_id>/upload', methods=['POST'])
def upload_file(task_id):
    form = FileUploadForm()
    file = request.files['file']
    if file:
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        new_file = File(filename=filename, task_id=task_id)
        db.session.add(new_file)
        db.session.commit()
        flash('File uploaded.', 'success')
    return redirect(url_for('task_detail', task_id=task_id))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)