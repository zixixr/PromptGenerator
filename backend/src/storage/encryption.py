"""Credential encryption service using Fernet symmetric encryption.

Provides secure storage and retrieval of LLM API credentials.
"""

import os
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet


class CredentialEncryption:
    """Service for encrypting and decrypting LLM API credentials.

    Uses Fernet symmetric encryption from the cryptography library.
    Encryption key is generated once and stored in data/encryption.key.
    """

    def __init__(self, key_file: str = "./data/encryption.key"):
        """Initialize encryption service.

        Args:
            key_file: Path to encryption key file
        """
        self.key_file = Path(key_file)
        self._key = self._load_or_create_key()
        self._cipher = Fernet(self._key)

    def _load_or_create_key(self) -> bytes:
        """Load existing encryption key or create a new one.

        Returns:
            Encryption key bytes
        """
        # Ensure data directory exists
        self.key_file.parent.mkdir(parents=True, exist_ok=True)

        if self.key_file.exists():
            # Load existing key
            with open(self.key_file, "rb") as f:
                return f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(key)
            # Secure file permissions (Unix-like systems)
            try:
                os.chmod(self.key_file, 0o600)
            except Exception:
                pass  # Windows doesn't support chmod the same way
            return key

    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext credentials.

        Args:
            plaintext: Unencrypted credential string

        Returns:
            Base64-encoded encrypted string
        """
        encrypted_bytes = self._cipher.encrypt(plaintext.encode("utf-8"))
        return encrypted_bytes.decode("utf-8")

    def decrypt(self, encrypted: str) -> str:
        """Decrypt encrypted credentials.

        Args:
            encrypted: Base64-encoded encrypted string

        Returns:
            Decrypted plaintext string

        Raises:
            cryptography.fernet.InvalidToken: If decryption fails
        """
        decrypted_bytes = self._cipher.decrypt(encrypted.encode("utf-8"))
        return decrypted_bytes.decode("utf-8")

    def store_credential(self, provider: str, api_key: str) -> None:
        """Store encrypted API key for a provider.

        Args:
            provider: LLM provider name (e.g., "openai", "anthropic")
            api_key: Unencrypted API key
        """
        credentials_file = Path("./data/credentials.enc")
        credentials_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing credentials
        credentials = self._load_credentials_file()

        # Encrypt and store
        credentials[provider] = self.encrypt(api_key)

        # Save back to file
        self._save_credentials_file(credentials)

    def retrieve_credential(self, provider: str) -> Optional[str]:
        """Retrieve and decrypt API key for a provider.

        Args:
            provider: LLM provider name

        Returns:
            Decrypted API key or None if not found
        """
        credentials = self._load_credentials_file()

        encrypted = credentials.get(provider)
        if encrypted:
            return self.decrypt(encrypted)
        return None

    def delete_credential(self, provider: str) -> bool:
        """Delete stored credential for a provider.

        Args:
            provider: LLM provider name

        Returns:
            True if credential was deleted, False if not found
        """
        credentials = self._load_credentials_file()

        if provider in credentials:
            del credentials[provider]
            self._save_credentials_file(credentials)
            return True
        return False

    def _load_credentials_file(self) -> dict[str, str]:
        """Load credentials from encrypted storage file.

        Returns:
            Dictionary mapping provider names to encrypted credentials
        """
        credentials_file = Path("./data/credentials.enc")

        if not credentials_file.exists():
            return {}

        import json

        try:
            with open(credentials_file, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_credentials_file(self, credentials: dict[str, str]) -> None:
        """Save credentials to encrypted storage file.

        Args:
            credentials: Dictionary mapping provider names to encrypted credentials
        """
        import json

        credentials_file = Path("./data/credentials.enc")

        with open(credentials_file, "w") as f:
            json.dump(credentials, f, indent=2)

        # Secure file permissions
        try:
            os.chmod(credentials_file, 0o600)
        except Exception:
            pass


# Global instance
_encryption_service: Optional[CredentialEncryption] = None


def get_encryption_service() -> CredentialEncryption:
    """Get global encryption service instance.

    Returns:
        Singleton CredentialEncryption instance
    """
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = CredentialEncryption()
    return _encryption_service
