import base64
import hashlib
import urllib.parse
import uuid

from nylas.models.auth import (
    CodeExchangeResponse,
    PkceAuthUrl,
    TokenInfoResponse,
    CodeExchangeRequest,
    TokenExchangeRequest,
    ProviderDetectResponse,
    ProviderDetectParams,
    URLForAuthenticationConfig,
    URLForAdminConsentConfig,
)
from nylas.models.response import Response
from nylas.resources.grants import Grants
from nylas.resources.resource import Resource


def _hash_pkce_secret(secret: str) -> str:
    sha256_hash = hashlib.sha256(secret.encode()).digest()
    return base64.b64encode(sha256_hash).decode()


def _build_query(config: dict) -> dict:
    config["response_type"] = "code"

    if not config["access_type"]:
        config["access_type"] = "online"

    if config["scopes"]:
        config["scopes"] = " ".join(config["scopes"])

    return config


def _build_query_with_pkce(config: dict, secret_hash: str) -> dict:
    params = _build_query(config)

    params["code_challenge"] = secret_hash
    params["code_challenge_method"] = "s256"

    return params


def _build_query_with_admin_consent(config: dict) -> dict:
    params = _build_query(config)

    params["response_type"] = "adminconsent"
    params["credential_id"] = config["credentialId"]

    return params


class Auth(Resource):
    @property
    def grants(self) -> Grants:
        """
        Access the Grants API.

        Returns:
            The Grants API.
        """
        return Grants(self._http_client)

    def url_for_oauth2(self, config: URLForAuthenticationConfig) -> str:
        """
        Build the URL for authenticating users to your application via Hosted Authentication.

        Args:
            config: The configuration for building the URL.

        Returns:
            The URL for hosted authentication.
        """
        query = _build_query(config)

        return self._url_auth_builder(query)

    def exchange_code_for_token(
        self, request: CodeExchangeRequest
    ) -> CodeExchangeResponse:
        """
        Exchange an authorization code for an access token.

        Args:
            request: The request parameters for the code exchange

        Returns:
            Information about the Nylas application
        """

        request_body = dict(request)
        request_body["grant_type"] = "authorization_code"

        return self._get_token(request_body)

    def refresh_access_token(
        self, request: TokenExchangeRequest
    ) -> CodeExchangeResponse:
        """
        Refresh an access token.

        Args:
            request: The refresh token request.

        Returns:
            The response containing the new access token.
        """

        request_body = dict(request)
        request_body["grant_type"] = "refresh_token"

        return self._get_token(request_body)

    def id_token_info(self, id_token: str) -> TokenInfoResponse:
        """
        Get info about an ID token.

        Args:
            id_token: The ID token to query.

        Returns:
            The API response with the token information.
        """

        query_params = {
            "id_token": id_token,
        }

        return self._get_token_info(query_params)

    def validate_access_token(self, access_token: str) -> TokenInfoResponse:
        """
        Get info about an access token.

        Args:
            access_token: The access token to query.

        Returns:
            The API response with the token information.
        """

        query_params = {
            "access_token": access_token,
        }

        return self._get_token_info(query_params)

    def url_for_oauth2_pkce(self, config: URLForAuthenticationConfig) -> PkceAuthUrl:
        """
        Build the URL for authenticating users to your application via Hosted Authentication with PKCE.

        IMPORTANT: YOU WILL NEED TO STORE THE 'secret' returned to use it inside the CodeExchange flow

        Args:
            config: The configuration for the authentication request.

        Returns:
            The URL for hosted authentication with secret & hashed secret.
        """
        secret = str(uuid.uuid4())
        secret_hash = _hash_pkce_secret(secret)
        query = _build_query_with_pkce(config, secret_hash)

        return PkceAuthUrl(secret, secret_hash, self._url_auth_builder(query))

    def url_for_admin_consent(self, config: URLForAdminConsentConfig) -> str:
        """Build the URL for admin consent authentication for Microsoft.

        Args:
            config: The configuration for the authentication request.

        Returns:
            The URL for hosted authentication.
        """
        config_with_provider = {"provider": "microsoft", **config}
        query = _build_query_with_admin_consent(config_with_provider)

        return self._url_auth_builder(query)

    def revoke(self, token: str) -> True:
        """Revoke a single access token.

        Args:
            token: The access token to revoke.

        Returns:
            True: If the token was revoked successfully.
        """
        self._http_client._execute(
            method="POST",
            path="/v3/connect/revoke",
            query_params={"token": token},
        )

        return True

    def detect_provider(
        self, params: ProviderDetectParams
    ) -> Response[ProviderDetectResponse]:
        """
        Detect provider from email address.

        Args:
            params: The parameters to include in the request

        Returns:
            The detected provider, if found.
        """

        json_response = self._http_client._execute(
            method="POST",
            path="/v3/providers/detect",
            query_params=params,
        )
        return Response.from_dict(json_response, ProviderDetectResponse)

    def _url_auth_builder(self, query: dict) -> str:
        return "{}/v3/connect/auth?{}".format(
            self._http_client.api_server, urllib.parse.urlencode(query)
        )

    def _get_token(self, request_body: dict) -> CodeExchangeResponse:
        json_response = self._http_client._execute(
            method="POST", path="/v3/connect/token", request_body=request_body
        )
        return CodeExchangeResponse.from_dict(json_response)

    def _get_token_info(self, query_params: dict) -> TokenInfoResponse:
        json_response = self._http_client._execute(
            method="GET", path="/v3/connect/tokeninfo", query_params=query_params
        )
        return TokenInfoResponse.from_dict(json_response)