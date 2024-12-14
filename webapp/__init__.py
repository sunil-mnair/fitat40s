import os
from datetime import *

# from flask_mail import Mail,Message

from flask import Flask, render_template, redirect, url_for, request, flash,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash, check_password_hash

project_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__,static_url_path='/static')

app.config['SECRET_KEY'] = 'bytesize_2024_07'


# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fitness.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


from webapp import routes
