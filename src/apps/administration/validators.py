import re

from django.core import validators
from django.core.exceptions import ValidationError


class LoginRegexValidator(validators.RegexValidator):
    regex = r"^[A-Za-z][\w]*"
    message = (
        "Логин может содержать только латинские буквы и цифры, "
        "первый символ — буква."
    )
    flags = 0


class PasswordSymbolsValidator:
    @staticmethod
    def contains_digits(string):
        _digits = re.compile("\d")
        return bool(_digits.search(string))

    @staticmethod
    def contains_specials(string):
        _specials = re.compile("[.,_+-=#@$!%*?&\"']")
        return bool(_specials.search(string))

    @staticmethod
    def contains_capitals(string):
        _capitals = re.compile("[A-Z]")
        return bool(_capitals.search(string))

    def validate(self, password, user=None):
        if not self.contains_digits(password):
            raise ValidationError(
                ("Пароль должен содержать минимум 1 цифру."),
                code="password_contains_no_digits",
            )
        if not self.contains_specials(password):
            raise ValidationError(
                ("Пароль должен содержать минимум 1 специальный символ."),
                code="password_contains_no_specials",
            )
        if not self.contains_capitals(password):
            raise ValidationError(
                ("Пароль должен содержать минимум 1 заглавную букву."),
                code="password_contains_no_capitals",
            )

    def get_help_text(self):
        return (
            "Пароль должен содержать минимум 1 цифру, специальный символ и "
            "заглавную букву."
        )
