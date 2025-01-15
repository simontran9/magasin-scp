from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from magasinscp.models import User


class RegistrationForm(FlaskForm):
    first_name = StringField(
        "Premier nom", validators=[DataRequired(), Length(min=3, max=15)]
    )
    last_name = StringField(
        "Dernier nom", validators=[DataRequired(), Length(min=3, max=15)]
    )
    email = StringField("Addresse courriel", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Mot de passe", validators=[DataRequired(), Length(min=8, max=20)]
    )
    confirm_password = PasswordField(
        "Confirmer votre mot de passe", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Créer votre compte")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(
                "Cette addresse courriel est déja associé avec un compte"
            )

        email_domain = email.data.split("@")[-1]

        if email_domain != "ecolecatholique.ca":
            raise ValidationError("Votre addresse courriel n'est pas de l'école")


class LoginForm(FlaskForm):
    email = StringField("Addresse courriel", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Mot de passe", validators=[DataRequired(), Length(min=8, max=20)]
    )
    remember = BooleanField("Mémoriser info")
    submit = SubmitField("Se connecter")


class PurchaseItemForm(FlaskForm):
    submit = SubmitField(label="Acheter l'item!")


class ConfirmEmailForm(FlaskForm):
    submit = SubmitField(label="Confirmer l'adresse courriel")


class RequestResetForm(FlaskForm):
    email = StringField("Addresse courriel", validators=[DataRequired(), Email()])
    submit = SubmitField("Demande de réinitialisation de votre mot de passe")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError(
                "Il n'y a pas de compte associé à cet e-mail. Veuillez créer un compte."
            )


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        "Mot de passe", validators=[DataRequired(), Length(min=8, max=20)]
    )
    confirm_password = PasswordField(
        "Confirmer votre mot de passe", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Réinitialiser le mot de passe")
