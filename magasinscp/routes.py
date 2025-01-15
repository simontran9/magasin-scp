import os
from flask import render_template, url_for, redirect, flash, request
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from magasinscp import app, db, bcrypt, mail, messages
from magasinscp.models import User, Item, PurchasedItems
from magasinscp.forms import (
    RegistrationForm,
    LoginForm,
    PurchaseItemForm,
    ConfirmEmailForm,
    RequestResetForm,
    ResetPasswordForm,
)
from dotenv import load_dotenv


load_dotenv()


def convert_to_name(name: str) -> str:
    """
    Capitilizes a string as if it is a proper noun
    """
    return name[0].upper() + name[1:].lower()


@app.route("/")
def index():
    return render_template("index.html", active="home")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500


s = URLSafeTimedSerializer(app.config["SECRET_KEY"])


def send_confirmation_email(account_email):
    token = s.dumps(account_email, salt="email-confirm")
    msg = Message(messages.CONFIRM_EMAIL_HEADING, recipients=[account_email])
    msg.body = (
        "Veuillez confirmer votre adresse courriel en cliquant sur ce lien :\n\n"
        + url_for("confirm_email", token=token, _external=True)
        + "\n\n"
        + "Merci,\n"
        + "L'équipe de développeurs"
    )
    mail.send(msg)
    flash(
        "Un message pour confirmer votre address courriel a été envoyé à "
        + account_email
        + ". Vous ne pouvez pas acheter des étampes avant d'avoir confirmé votre adresse courriel.",
        "warning",
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("account"))

    form = RegistrationForm()
    if form.validate_on_submit():

        # Hash the password and create the user
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )

        first_name = convert_to_name(form.first_name.data)
        last_name = convert_to_name(form.last_name.data)

        user = User(
            first_name=first_name,
            last_name=last_name,
            email=form.email.data,
            password=hashed_password,
            admin=False,
            email_confirmed=False,
            stamps=0,
        )
        db.session.add(user)
        db.session.commit()
        flash(
            first_name + " " + last_name + ", votre compte a été crée avec succès!",
            "success",
        )

        # Verify email address and send confirmation email
        send_confirmation_email(form.email.data)

        login_user(user)
        return redirect(url_for("account"))
    return render_template("register.html", form=form, active="register")


@app.route("/confirm_email/<token>")
def confirm_email(token):
    try:
        email = s.loads(token, salt="email-confirm", max_age=900)
    except SignatureExpired:
        return render_template("reset_password_email_expired.html"), 400

    if current_user.is_authenticated:
        current_user.email_confirmed = True
        db.session.commit()
        flash(
            messages.ACCOUNT_ACTIVATED,
            "success",
        )
    else:
        flash(
            messages.ACCOUNT_NOT_ACTIVATED,
            "danger",
        )
        return redirect(url_for("login"))
    return redirect(url_for("account"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("account"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("account"))
        else:
            flash(
                messages.INVALID_USERNAME_OR_PASSWORD,
                "danger",
            )
    return render_template("login.html", form=form, active="login")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    if current_user.email_confirmed == False:
        form = ConfirmEmailForm()
        if form.validate_on_submit():
            send_confirmation_email(current_user.email)
        return render_template("confirm_email.html", form=form, active="account")
    return render_template("account.html", active="account")


def send_client_receipt(item_name, item_price):
    client_msg = Message(
        messages.USER_PURCHASE_EMAIL_HEADING,
        recipients=[current_user.email],
    )
    client_msg.body = (
        "Votre commande a été prise en compte.\n\n"
        + "Vous avez achetez:\n\n"
        + "1 "
        + item_name
        + " pour "
        + str(item_price)
        + " étampes.\n\n"
        + "Merci,\n"
        + "Le magasin SCP"
    )
    mail.send(client_msg)


def send_order_staff(item_name, item_price):
    staff_msg = Message(
        messages.STAFF_PURCHASE_EMAIL_HEADING,
        recipients=[os.environ.get("STAFF_EMAIL_ADDRESS")],
    )
    staff_msg.body = (
        current_user.first_name
        + " "
        + current_user.last_name
        + " a acheté un item dans le magasin SCP.\n\n"
        + "Leur commande:\n\n"
        + "1 "
        + item_name
        + " pour "
        + str(item_price)
        + " étampes.\n\n"
        + "Merci,\n"
        + "Le magasin SCP"
    )
    mail.send(staff_msg)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if current_user.email_confirmed == False:
        return render_template("block_store.html")

    purchase_form = PurchaseItemForm()

    if purchase_form.validate_on_submit():
        items = Item.query.all()
        clicked_item = request.form.get("clicked_item")
        desired_item = Item.query.filter_by(product_name=clicked_item).first()
        if desired_item:
            if current_user.can_buy(desired_item):
                desired_item.buy(current_user)
                bought_item_name = desired_item.product_name
                bought_item_price = desired_item.price
                bought_item = PurchasedItems(
                    product_name=bought_item_name,
                    price=bought_item_price,
                    user=current_user,
                )
                db.session.add(bought_item)
                db.session.commit()
                flash(
                    "Félicitations! Vous avez achetez "
                    + bought_item_name
                    + " pour "
                    + str(bought_item_price)
                    + " étampes!",
                    "success",
                )
                send_client_receipt(bought_item_name, bought_item_price)
                send_order_staff(bought_item_name, bought_item_price)
            else:
                flash(
                    "Malheureusement, vous n'avez pas assez d'étampes pour acheter "
                    + desired_item.product_name
                    + ".",
                    "danger",
                )
        return redirect(url_for("buy"))
    elif request.method == "GET":
        items = Item.query.all()

    return render_template(
        "buy.html", items=items, active="buy", purchase_form=purchase_form
    )


def send_reset_password_email(user):
    token = user.get_reset_token()

    msg = Message(
        messages.RESET_PASS_EMAIL_HEADING,
        recipients=[user.email],
    )

    msg.body = (
        "Pour réinitialiser votre mot de passe, veuillez suivre ce lien :\n\n"
        + url_for("reset_token", token=token, _external=True)
        + "\n\n"
        + "Si vous n'avez pas fait cette demande, ignorez simplement cet e-mail et aucun changement ne sera effectué.\n\n"
        + "Merci,\n"
        + "L'équipe de développeurs"
    )

    mail.send(msg)


@app.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = RequestResetForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_password_email(user)
        flash(
            messages.RESET_PASSWORD_LINK_SENT,
            "info",
        )
        return redirect(url_for("login"))

    return render_template("reset_request.html", form=form)


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    user = User.verify_reset_token(token)

    if user is None:
        flash(
            messages.INVALID_TOKEN,
            "warning",
        )
        return redirect(url_for("reset_request"))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user.password = hashed_password
        db.session.commit()
        flash(
            messages.RESET_PASSWORD_SUCCESS,
            "success",
        )
        return redirect(url_for("login"))

    return render_template("reset_token.html", form=form)
