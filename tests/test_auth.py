from backend.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    verify_access_token,
)


def test_password_hashing():

    password = "TestPassword123"

    hashed_password = hash_password(password)

    assert hashed_password != password

    assert verify_password(
        password,
        hashed_password,
    )


def test_wrong_password_fails():

    password = "TestPassword123"

    hashed_password = hash_password(password)

    assert not verify_password(
        "WrongPassword",
        hashed_password,
    )


def test_jwt_token():

    username = "testuser"

    token = create_access_token(username)

    result = verify_access_token(token)

    assert result == username