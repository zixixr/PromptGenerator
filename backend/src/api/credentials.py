"""Credentials API routes.

Handles secure storage and retrieval of LLM API credentials.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..storage.encryption import get_encryption_service

router = APIRouter()


class CredentialRequest(BaseModel):
    """Request model for storing credentials."""

    provider: str
    api_key: str


class CredentialResponse(BaseModel):
    """Response model for credential operations."""

    provider: str
    stored: bool


@router.post("/credentials", response_model=CredentialResponse, status_code=201)
async def store_credential(request: CredentialRequest) -> CredentialResponse:
    """Store an encrypted API credential.

    Args:
        request: Provider and API key

    Returns:
        Confirmation of storage
    """
    encryption = get_encryption_service()

    try:
        encryption.store_credential(request.provider, request.api_key)
        return CredentialResponse(provider=request.provider, stored=True)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to store credential: {str(e)}"
        )


@router.get("/credentials/{provider}")
async def check_credential_exists(provider: str) -> dict[str, bool]:
    """Check if a credential exists for a provider.

    Note: Does not return the actual credential for security.

    Args:
        provider: Provider name

    Returns:
        Dict indicating if credential exists
    """
    encryption = get_encryption_service()

    credential = encryption.retrieve_credential(provider)

    return {"exists": credential is not None}


@router.delete("/credentials/{provider}", status_code=204)
async def delete_credential(provider: str) -> None:
    """Delete a stored credential.

    Args:
        provider: Provider name

    Raises:
        HTTPException: If credential not found
    """
    encryption = get_encryption_service()

    deleted = encryption.delete_credential(provider)

    if not deleted:
        raise HTTPException(
            status_code=404, detail=f"No credential found for provider {provider}"
        )
