from app.services.auth_service import create_user, authenticate_user, decode_token

def test_auth_flow():
    # Step 1: Create user
    create_user("alice", "mypassword", role="admin")

    # Step 2: Authenticate user (login)
    token = authenticate_user("alice", "mypassword")
    print("\nJWT Token:", token)

    # Step 3: Decode token (verify session)
    payload = decode_token(token)
    print("\nDecoded Payload:", payload)


if __name__ == "__main__":
    test_auth_flow()
