from typing import Optional, Dict

from fastapi import HTTPException, status
from fastapi.security import OAuth2, OAuth2PasswordBearer
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel, OAuthFlowClientCredentials
from fastapi.security.utils import get_authorization_scheme_param
from starlette.requests import Request


class OAuth2ClientCredentials(OAuth2):
    """
    OAuth2 Client Credentials flow (for OpenAPI) + Bearer token extraction from Authorization header.
    This gives Swagger UI the correct 'client_credentials' authorize form.
    """

    def __init__(
        self,
        tokenUrl: str,
        scheme_name: str | None = None,
        scopes: Dict[str, str] | None = None,
        auto_error: bool = True,
    ):
        if scopes is None:
            scopes = {}

        flows = OAuthFlowsModel(
            clientCredentials=OAuthFlowClientCredentials(
                tokenUrl=tokenUrl,
                scopes=scopes,
            )
        )
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        authorization = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)

        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return None
        return param


USER_OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="/auth/token", scheme_name="UserPasswordFlow")
M2M_OAUTH2_SCHEME = OAuth2ClientCredentials(tokenUrl="/auth/m2m-token", scheme_name="M2MClientCredentialsFlow")