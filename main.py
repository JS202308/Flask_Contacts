import os

from uuid import uuid4
from flask import Flask, render_template, url_for, flash, redirect, request
from flask_login import LoginManager, current_user, login_required, logout_user, login_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename
from flask_caching import Cache

from models import db, User, Contact
from config import settings
from forms import SigninForm, SignUpForm, ContactForm

config = {          
    "CACHE_TYPE": "SimpleCache", 
    "CACHE_DEFAULT_TIMEOUT": 300
}


app = Flask(__name__)
app.secret_key = settings.secret_key
app.config["SQLALCHEMY_DATABASE_URI"] = settings.sqlalchemy_uri
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['MAX_FORM_MEMORY_SIZE'] = 1024 * 1024  # 1MB
app.config['MAX_FORM_PARTS'] = 500
db.init_app(app)
csrf_protect = CSRFProtect(app)
app.config.from_mapping(config)
cache = Cache(app)


UPLOAD_FOLDER = os.path.join('static', 'img')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    
    db.init_app(app)

login_manager = LoginManager()
login_manager.login_message = "Спочатку увійдіть у систему"
login_manager.login_view = "sign_in"
login_manager.init_app(app)


# with app.app_context():
#     db.drop_all()
#     db.create_all()

# @cache.cached(Timeout=30)
# @login_manager.user_loader
# def load_user(user_id):
#     print("Пішов запит до бази даних")
#     return User.query.filter_by(id=user_id).first_or_404()

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first_or_404()




@app.route("/signUp/", methods=["GET", "POST"])
def sign_up():
    sign_up_form = SignUpForm()

    if sign_up_form.validate_on_submit():
        username = sign_up_form.username.data
        password = sign_up_form.password.data
        fullname = sign_up_form.fullname.data
        phone_number = sign_up_form.phone_number.data

        user = User(
    username=username,
    password=password,
    fullname=fullname,
    phone_number=phone_number,
    img=""  )
        db.session.add(user)
        db.session.commit()

        login_user(user) 
        flash("Ви успішно зареєструвались")
        return redirect(url_for("cabinet"))  

    return render_template("sign_up.html", form=sign_up_form)


@app.route("/signIn/", methods=["GET", "POST"], endpoint="sign_in")
def sign_in_view():  # поменяли имя функции
    form = SigninForm()
    if request.method == "POST" and form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.is_verify_password(form.password.data):
            login_user(user)
            return redirect(url_for("cabinet"))
        else:
            flash("Логін або пароль невірні")
            return redirect(url_for("sign_in"))

    return render_template("sign_in.html", form=form)


@app.get("/")
@login_required
@cache.cached(timeout=30, query_string=True)
def cabinet():
    print("Функція запустилась")
    return render_template("cabinet.html")

@app.get("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for("sign_in"))

@app.route("/contact/", methods=["GET", "POST"])
@login_required
def add_contact():
    form = ContactForm()
    if form.validate_on_submit():
        filename = None

        file = form.file.data
        if file and file.filename:
            filename = f"{uuid4().hex}_{secure_filename(file.filename)}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)  

        # Создаем контакт
        contact = Contact(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone_number=form.phone_number.data,
            bio=form.bio.data,
            city=form.city.data,
            img=filename,           
            user_id=current_user.id
        )
        db.session.add(contact)
        db.session.commit()
        flash("Контакт успішно додано!")
        return redirect(url_for("cabinet"))

    return render_template("add_contact.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)