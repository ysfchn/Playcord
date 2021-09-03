import httpx
from typing import Optional
from playcord.classes import Session, Profile

class Account:
    AUTH_ENDPOINT = "https://auth.api.sonyentertainmentnetwork.com/2.0/oauth/token"
    CLIENT_TOKEN = "YWM4ZDE2MWEtZDk2Ni00NzI4LWIwZWEtZmZlYzIyZjY5ZWRjOkRFaXhFcVhYQ2RYZHdqMHY="

    def __init__(self) -> None:
        self.client = httpx.Client()
        self.session : Optional[Session] = None


    @staticmethod
    def login(token : str) -> "Account":
        """
        Logins using a OAuth token and returns a `Account` object.
        """
        account = Account()
        # Login token request.
        response = account.client.post(
            account.AUTH_ENDPOINT,
            data = {
                "grant_type": "authorization_code",
                "code": token,
                "redirect_uri": "com.playstation.PlayStationApp://redirect"
            },
            headers = {
                "Authorization": f"Basic {account.CLIENT_TOKEN}", 
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )
        response.raise_for_status()
        account.session = Session(**response.json())
        return account


    @staticmethod
    def login_refresh(refresh_token : str) -> "Account":
        """
        Logins using a refresh token and returns a `Account` object.
        """
        account = Account()
        account.session = Session(
            access_token = "",
            token_type = "",
            refresh_token = refresh_token,
            expires_in = "0",
            scope = "psn:clientapp referenceDataService:countryConfig.read"
        )
        account.refresh()
        return account


    @property
    def refresh_required(self) -> bool:
        """
        Returns True if token is expiring soon. Otherwise, False.
        """
        if not self.session:
            raise ValueError("User is not signed in.")
        return self.session.expire_seconds <= (10 * 60)


    def refresh(self) -> None:
        """
        Refeshes a token.
        """
        if not self.session:
            raise ValueError("User is not signed in.")
        # Refresh token request.
        response = self.client.post(
            self.AUTH_ENDPOINT,
            data = {
                "grant_type": "refresh_token",
                "refresh_token": self.session.refresh_token,
                "redirect_uri": "com.playstation.PlayStationApp://redirect",
                "scope": self.session.scope
            },
            headers = {
                "Authorization": f"Basic {self.CLIENT_TOKEN}", 
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )
        response.raise_for_status()
        self.session = Session(**response.json())


    def profile(self) -> Profile:
        """
        Get user profile and returns a `Profile` object.
        """
        if not self.session:
            raise ValueError("User is not signed in.")
        # Get user profile.
        response = self.client.get(
            "https://us-prof.np.community.playstation.net/userProfile/v1/users/me/profile2",
            params = {
                "fields": "onlineId,avatarUrls,plus,primaryOnlineStatus,presences(@titleInfo)",
                "avatarSizes": "m,xl",
                "titleIconSize": "s"
            },
            headers = {
                "Authorization": f"Bearer {self.session.access_token}"
            }
        )
        response.raise_for_status()
        return Profile(response.json())
