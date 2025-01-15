import os
from dotenv import load_dotenv
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_admin import Admin
from flask_mail import Mail

load_dotenv()


app = Flask(__name__)


app.config["SECRET_KEY"] = os.environ.get("KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"


app.config["FLASK_ADMIN_SWATCH"] = "united"


app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USERNAME"] = os.environ.get("MESSAGE_SENDER_EMAIL_ADDRESS")
app.config["MAIL_PASSWORD"] = os.environ.get("MESSAGE_SENDER_PASSWORD")
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MESSAGE_SENDER_EMAIL_ADDRESS")


mail = Mail(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)


from magasinscp.staff import (
    MyAdminIndexView,
    UserModelView,
    ItemModelView,
    PurchasedItemsModelView,
    HomePageView,
)


admin = Admin(
    app,
    name="Compte administrateur",
    template_mode="bootstrap3",
    index_view=MyAdminIndexView(),
)


from magasinscp.models import User, Item, PurchasedItems


admin.add_view(UserModelView(User, db.session, name="Utilisateurs"))
admin.add_view(ItemModelView(Item, db.session, name="Items"))
admin.add_view(PurchasedItemsModelView(PurchasedItems, db.session, name="Commandes"))
admin.add_view(HomePageView(name="Retourner vers la page principale"))


# Not actually using routes, but making sure the module is imported
from magasinscp import routes
