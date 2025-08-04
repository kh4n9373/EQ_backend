from app.authorization import (
    create_access_token,
    decrypt_refresh_token,
    encrypt_refresh_token,
)


class TestAuth:

    def test_create_access_token(self):
        data = {"sub": "test@example.com", "name": "Test User"}
        token = create_access_token(data)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_encrypt_decrypt_refresh_token(self):
        original_token = "original_refresh_token_123"
        # Encrypt
        encrypted = encrypt_refresh_token(original_token)
        assert isinstance(encrypted, str)
        assert encrypted != original_token
        # Decrypt
        decrypted = decrypt_refresh_token(encrypted)
        assert decrypted == original_token
