from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import re

class SymbolValidator:
    def validate(self, password, user=None):
        if not re.search(r"[()\[\]{}|\\`~!@#$%^&*_\-+=;:'\",.<>/?]", password):
            raise ValidationError(
                _("The password must contain at least one symbol."),
                code='password_no_symbol',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least one of the following symbols: "
            "()[]{}|\\`~!@#$%^&*_-+=;:'\",.<>/? "
        )