import pytest, os, json, jwt, datetime
from fastapi import HTTPException, status
from src.auth_eksempel.models import User, Role
from fastapi.testclient import TestClient


from src.auth_eksempel.user_service import User_service
from src.auth_eksempel.auth_service import Auth_service
from src.auth_eksempel.models import Role
from src.auth_eksempel.auth_rest_api import Auth_rest_api

#pytestmark = pytest.mark.focus

filename = "db_test_user_flat_file.json"

def create_default_user_file(filename:str):
    user_data = {
        "admin_custom": User(
            username="admin_custom",
            password=Auth_service.hash_password("qwerty1234567890"),
            first_name=Auth_service.encrypt_data("John"),
            last_name=Auth_service.encrypt_data("Doe"),
            active=True,
            roles=[Role.admin],
        ).toDict(),
        "cat-woman@fake-mail.com": User(
            username="cat-woman@fake-mail.com",
            password=Auth_service.hash_password("qwerty1234567891"),
            first_name=Auth_service.encrypt_data("Cat"),
            last_name=Auth_service.encrypt_data("Woman"),
            active=True,
            roles=[Role.user],
        ).toDict(),
        "bat_man@fake-mail.com": User(
            username="bat_man@fake-mail.com",
            password=Auth_service.hash_password("qwerty1234567892"),
            first_name=Auth_service.encrypt_data("Bat"),
            last_name=Auth_service.encrypt_data("Man"),
            active=True,
            roles=[Role.user],
        ).toDict(),
            "debat_man@fake-mail.com": User(
            username="bat_man@fake-mail.com",
            password=Auth_service.hash_password("qwerty1234567892"),
            first_name=Auth_service.encrypt_data("Bat"),
            last_name=Auth_service.encrypt_data("Man"),
            active=False,
            roles=[Role.user],
        ).toDict()
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(user_data, f, indent=4)    


def delete_json_files():
    if os.path.exists(filename):
        os.remove(filename)


@pytest.fixture(scope="function", autouse=True)
def cleanup_files():
    # before test
    delete_json_files()
    yield
    # after test
    delete_json_files()



def test_no_user_file_creates_default_admin():
    # given
    # pass

    # when
    user_service = User_service(filename)

    # then
    assert len(user_service._user_db) == 1

    user = user_service._user_db["admin"]
    
    assert user.username == "admin"
    assert Auth_service.verify_password("admin", user.password)

    print(f"\n* encrypted first_name: {user.first_name}");
    print(f"* decrypted first_name: {Auth_service.decrypt_data(user.first_name)}");
    assert user.first_name != "admin_first_name"
    assert Auth_service.decrypt_data(user.first_name) == "admin_first_name"
    
    print(f"* encrypted last_name: {user.last_name}");
    print(f"* decrypted last_name: {Auth_service.decrypt_data(user.last_name)}");
    assert user.last_name != "admin_last_name"
    assert Auth_service.decrypt_data(user.last_name) == "admin_last_name"
    
    assert user.active == True
    assert user.roles == [Role.admin]


def test_with_existing_user_file():
    # given

    create_default_user_file(filename)

    # when
    user_service = User_service(filename)

    # then
    user_db = user_service._user_db

    user = user_db["admin_custom"]
    
    assert user.username == "admin_custom"
    assert Auth_service.verify_password("qwerty1234567890", user.password)
    assert Auth_service.decrypt_data(user.first_name) == "John"
    assert Auth_service.decrypt_data(user.last_name) == "Doe"
    assert user.active == True
    assert user.roles == [Role.admin]


def test_register_new_user():
    # given

    create_default_user_file(filename)
    user_service = User_service(filename)

    # when
    user_service.register_user("test-user@fake-mail.com", "password1234", "Peter", "Parker", [Role.user])

    # then
    user_db = user_service._user_db
    user = user_db["test-user@fake-mail.com"]
    assert user.username == "test-user@fake-mail.com"
    assert Auth_service.verify_password("password1234", user.password)
    assert Auth_service.decrypt_data(user.first_name) == "Peter"
    assert Auth_service.decrypt_data(user.last_name) == "Parker"
    assert user.active == True
    assert user.roles == [Role.user]


def test_register_new_user_where_username_is_not_email():
    # given

    create_default_user_file(filename)
    user_service = User_service(filename)

    errorMessage = "Invalid email address"
    testDataList = [
        {
            "email": "a@b", 
            "exception": None,
        }, {
            "email": "test@fake-mail.com", 
            "exception": None,
        }, {
            "email": "test-user", 
            "exception": errorMessage,
        }, {
            "email": "a@", 
            "exception": errorMessage,
        }, {
            "email": '@b', 
            "exception": errorMessage,
        },
    ]


    for testData in testDataList:
        exception = None

        # when 
        try:
            user_service.register_user(testData["email"], "pw", "f", "e", [Role.user])
        except HTTPException as e:
            exception = e

        # then
        if testData["exception"] == None:
            assert exception == None, f"email '{testData["email"]}' is invalid"
        else:
            assert exception != None, f"email '{testData["email"]}' is valid"
            assert exception.status_code == 400
            assert exception.detail == testData["exception"]




def test_register_new_user_where_username_is_taken():
    # given

    create_default_user_file(filename)
    user_service = User_service(filename)

    # when
    exception_1 = None
    try:
        user_service.register_user("cat-woman@fake-mail.com", "password1234", "Peter", "Parker", [Role.user])
    except HTTPException as e:
        exception_1 = e

    # then
    assert exception_1 != None, "exception must be thrown"
    assert exception_1.status_code == 400
    assert exception_1.detail == "Username already exists"


def test_get_bearer_token():
    # given

    create_default_user_file(filename)
    user_service = User_service(filename)

    # when
    token = user_service.get_bearer_token("admin_custom", "qwerty1234567890")
    payload = Auth_service.verify_token(token)

    # then
    assert payload["sub"] == "admin_custom"
    assert payload["roles"] == ["admin"]
    assert payload["exp"] != None
    assert payload["iat"] != None


def test_get_bearer_token_expired():
    # given

    create_default_user_file(filename)
    user_service = User_service(filename)

    # when
    payload = {
        "sub": "test-user",
        "roles": ["admin"],
        "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=0),  # just expired
        "iat": datetime.datetime.now(datetime.UTC),  # issued at
    }
    token = f"Bearer {jwt.encode(payload, Auth_service._secret, algorithm=Auth_service._algorithm)}"
    exception = None
    try:
        payload = Auth_service.verify_token(token)
    except HTTPException as e:
        exception = e

    # then
    assert exception != None, "exception must be thrown"
    assert exception.status_code == 401
    assert exception.detail == "Token expired"


def test_get_bearer_token_invalid():
    # given

    create_default_user_file(filename)
    user_service = User_service(filename)

    # when
    exception = None
    token = user_service.get_bearer_token("admin_custom", "qwerty1234567890")
    token = token[:-1]
 
    try:
        payload = Auth_service.verify_token(token)
    except HTTPException as e:
        exception = e

    # then
    assert exception != None, "exception must be thrown"
    assert exception.status_code == 401
    assert exception.detail == "Invalid token"


def test_deactivate_user_as_admin():
    # given

    create_default_user_file(filename)
    user_service = User_service(filename)
    assert user_service._user_db["bat_man@fake-mail.com"].active == True
    
    # when
    token = user_service.get_bearer_token("admin_custom", "qwerty1234567890")
    user_service.deactivate_user(token, "bat_man@fake-mail.com")    

    # then
    assert user_service._user_db["bat_man@fake-mail.com"].active == False


def test_deactivate_user_as_own_user():
    # given

    create_default_user_file(filename)
    user_service = User_service(filename)
    assert user_service._user_db["bat_man@fake-mail.com"].active == True
    
    # when
    token = user_service.get_bearer_token("bat_man@fake-mail.com", "qwerty1234567892")
    user_service.deactivate_user(token, "bat_man@fake-mail.com")    

    # then
    assert user_service._user_db["bat_man@fake-mail.com"].active == False    


def test_deactivate_user_as_different_user():
    # given

    create_default_user_file(filename)
    user_service = User_service(filename)
    assert user_service._user_db["cat-woman@fake-mail.com"].active == True
    
    # when
    token = user_service.get_bearer_token("cat-woman@fake-mail.com", "qwerty1234567891")
    exception = None
    try:
        user_service.deactivate_user(token, "bat_man@fake-mail.com")    
    except HTTPException as e:
        exception = e

    # then
    assert exception != None, "exception must be thrown"
    assert exception.status_code == 403
    assert exception.detail == "User don't have the privileges"
    assert user_service._user_db["bat_man@fake-mail.com"].active == True    


def test_activate_user_as_admin():
    # given

    create_default_user_file(filename)
    user_service = User_service(filename)
    assert user_service._user_db["debat_man@fake-mail.com"].active == False
    
    # when
    token = user_service.get_bearer_token("admin_custom", "qwerty1234567890")
    user_service.deactivate_user(token, "debat_man@fake-mail.com")    

    # then
    assert user_service._user_db["debat_man@fake-mail.com"].active == False


def test_activate_user_as_own_user():
    # given

    create_default_user_file(filename)
    user_service = User_service(filename)
    assert user_service._user_db["debat_man@fake-mail.com"].active == False
    
    # when
    token = user_service.get_bearer_token("cat-woman@fake-mail.com", "qwerty1234567891")
    exception = None
    try:
        user_service.deactivate_user(token, "debat_man@fake-mail.com")    
    except HTTPException as e:
        exception = e   

    # then
    assert exception != None, "exception must be thrown"
    assert exception.status_code == 403
    assert exception.detail == "User don't have the privileges"
    assert user_service._user_db["debat_man@fake-mail.com"].active == False    


def test_activate_user_as_different_user():
    # given

    create_default_user_file(filename)
    user_service = User_service(filename)
    assert user_service._user_db["debat_man@fake-mail.com"].active == False
    
    # when
    token = user_service.get_bearer_token("cat-woman@fake-mail.com", "qwerty1234567891")
    exception = None
    try:
        user_service.deactivate_user(token, "debat_man@fake-mail.com")    
    except HTTPException as e:
        exception = e

    # then
    assert exception != None, "exception must be thrown"
    assert exception.status_code == 403
    assert exception.detail == "User don't have the privileges"
    assert user_service._user_db["debat_man@fake-mail.com"].active == False    


def test_deactivate_admin_so_it_cant_deactivate_users():
    # given
    create_default_user_file(filename)
    user_service = User_service(filename)
    assert user_service._user_db["admin_custom"].active == True
    assert user_service._user_db["bat_man@fake-mail.com"].active == True
    
    # when admin is deactivated
    token = user_service.get_bearer_token("admin_custom", "qwerty1234567890")
    user_service.deactivate_user(token, "admin_custom")    
    
    exception = None
    try:
        user_service.deactivate_user(token, "bat_man@fake-mail.com")    
    except HTTPException as e:
        exception = e

    # then
    assert exception != None, "exception must be thrown"
    assert exception.status_code == 403
    assert exception.detail == "User don't have the privileges"
    assert user_service._user_db["debat_man@fake-mail.com"].active == False    




def test_deactive_user_from_restApi():
    # given rest api exists
    create_default_user_file(filename)

    api = Auth_rest_api(filename)
    client = TestClient(api.app)
    user_service = api.user_service

    # and user is created
    test_user_email = "batman@fake-mail.com"
    response = response = client.post(
        "/register_user",
        json={
        "username": test_user_email,
        "password": "12345678",
        "first_name": "bat",
        "last_name": "man",
        "roles": [
            "user"
        ]
        }
    )
    assert response.status_code == 200, f"Token request failed: {response.text}"

    # and bearer token for admin is obtained
    response = client.post(
        "/get_bearer_token",
        json={"username": "admin_custom", "password": "qwerty1234567890"}
    )
    assert response.status_code == 200, f"Token request failed: {response.text}"
    token = response.json()
    bearer_token = token["token"]

    # and the user is active
    
    assert user_service._get_user(test_user_email).active == True

    # when
    response = client.post(
        "/deactivate_user",
        json={"username": test_user_email},
        headers={"token": bearer_token}
    )

    # then
    assert response.status_code == 200, f"Deactivate user failed: {response.text}"
    assert user_service._get_user(test_user_email).active == False


    # when
    response = client.post(
        "/activate_user",
        json={"username": test_user_email},
        headers={"token": bearer_token}
    )

    # then
    assert response.status_code == 200, f"Deactivate user failed: {response.text}"
    assert user_service._get_user(test_user_email).active == True
