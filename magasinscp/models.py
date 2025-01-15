from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin, AnonymousUserMixin
from magasinscp import db, login_manager, app


class Anonymous(AnonymousUserMixin):
    def __init__(self):
        self.admin = False


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


login_manager.login_view = "login"
login_manager.login_message_category = "info"
login_manager.anonymous_user = Anonymous


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(15), nullable=False)
    last_name = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    admin = db.Column(db.Boolean, default=False)
    email_confirmed = db.Column(db.Boolean, default=False)
    stamps = db.Column(db.Integer, nullable=True)
    purchased_items = db.relationship("PurchasedItems", backref="user")

    def can_buy(self, item):
        return self.stamps >= item.price

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config["SECRET_KEY"], expires_sec)
        return s.dumps({"user_id": self.id}).decode("utf-8")

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config["SECRET_KEY"])
        try:
            user_id = s.loads(token)["user_id"]
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"{self.first_name} {self.last_name}"


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(45), unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)

    def buy(self, user):
        user.stamps -= self.price
        db.session.commit()

    def __repr__(self):
        return f"Item('{self.product_name}', '{self.price}')"


class PurchasedItems(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(45), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
