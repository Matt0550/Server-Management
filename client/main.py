from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

login_manager = LoginManager()

app = Flask(__name__)
login_manager.init_app(app)

# AUTH
