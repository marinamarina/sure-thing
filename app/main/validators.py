from wtforms import ValidationError
from ..models import User


# Custom validators
def validator_user_already_registered():
        """custom validator used in the registration form"""

        def _user_already_registered(form, field):
            kwargs = {field.id: field.data}

            if User.query.filter_by(**kwargs).first():
                raise ValidationError(message='User with this ' + str(field.id) + ' is already registered!')

        return _user_already_registered
