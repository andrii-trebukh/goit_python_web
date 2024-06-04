from . import Field


class Number(Field):
    def is_valid(self, value):
        if not value.isdigit():
            raise ValueError("Incorrect input. Should be number.")
        return True
