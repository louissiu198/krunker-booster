from httpx import Client, post

V = {"v":"7IS6yK5mxvg54G47hEKwUjB7Dpw86p77"}
REGION = "sgp"
SVC_URL = "https://gapi.svc.krunker.io"
FRVR_URL = "https://crucible.frvr.com"
DEFAULT_URL = "https://krunker.io"
MATCHMAKING_URL = "https://matchmaker.krunker.io"

SEQMSG_TIMEOUT = 0.5
PING_TIMEOUT = 5

user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"

class utils:
    def __init__(self, client: Client) -> None:
        self.req = client
        self.req.headers = {
            "user-agent": user_agent
        }

    def fetch_validation_token(self) -> str:
        tkn = self.req.get(f"{MATCHMAKING_URL}/generate-token")
        return tkn.text

    def get_access_token(self) -> dict:
        rsp = self.req.post(
            f"{FRVR_URL}/v1/auth/login",
            json={"platform": "anonymous"},
        ).json()["accessToken"]
        return rsp
