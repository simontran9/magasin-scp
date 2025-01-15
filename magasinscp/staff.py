from flask import url_for, redirect
from flask_admin import AdminIndexView, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user


class HomePageView(BaseView):
    @expose("/")
    def index(self):
        return redirect(url_for("account"))


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        if current_user.admin == True:
            return current_user.is_authenticated

    def is_visible(self):
        return False


class UserModelView(ModelView):
    def is_accessible(self):
        if current_user.admin == True:
            return current_user.is_authenticated

    column_labels = dict(
        first_name="Prénom",
        last_name="Dernier Nom",
        email="Addresse Courriel",
        admin="Administrateur",
        email_confirmed="Addresse Courriel confirmée",
        stamps="Étampe",
    )
    can_create = False
    column_exclude_list = "password"
    form_excluded_columns = ["password", "email_confirmed"]


class ItemModelView(ModelView):
    def is_accessible(self):
        if current_user.admin == True:
            return current_user.is_authenticated

    column_labels = dict(
        product_name="Item",
        price="Prix",
    )


class PurchasedItemsModelView(ModelView):
    def is_accessible(self):
        if current_user.admin == True:
            return current_user.is_authenticated

    column_labels = dict(
        product_name="Item",
        price="Prix",
    )
