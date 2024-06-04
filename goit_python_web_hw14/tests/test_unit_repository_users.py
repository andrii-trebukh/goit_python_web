import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel

from src.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email,
    new_password,
    update_avatar
)


class TestUsers(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)

    async def test_get_user_by_email(self):
        user = User()
        self.session.query().filter().first.return_value = user
        result = await get_user_by_email(
            email="example@mail.com",
            db=self.session
        )
        self.assertEqual(result, user)

    async def test_get_user_by_email_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_user_by_email(
            email="example@mail.com",
            db=self.session
        )
        self.assertIsNone(result)

    async def test_create_user(self):
        body = UserModel(
            username="name",
            email="example@mail.com",
            password="password"
        )
        result = await create_user(body=body, db=self.session)
        self.assertTrue(hasattr(result, "id"))
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)
        self.assertTrue(hasattr(result, "created_at"))
        self.assertIsNone(result.refresh_token)
        self.assertFalse(result.confirmed)
        self.assertIsNone(result.avatar)

    async def test_update_token(self):
        user = User()
        token = "token_str"
        result = await update_token(user=user, token=token, db=self.session)
        self.assertIsNone(result)

    async def test_confirmed_email(self):
        email = "example@mail.com"
        result = await confirmed_email(email=email, db=self.session)
        self.assertIsNone(result)

    async def test_new_password(self):
        user = User()
        password = "password"
        result = await new_password(
            user=user,
            password=password,
            db=self.session
        )
        self.assertIsNone(result)

    async def test_update_avatar(self):
        email = "example@mail.com"
        url = "url_str"
        result = await update_avatar(email=email, url=url, db=self.session)
        self.assertEqual(result.avatar, url)


if __name__ == '__main__':
    unittest.main()
