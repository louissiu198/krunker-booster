# Krunker Unofficial API Walk Through
Anaylsis of packet security, encryption methods, captcha used and server regulations.
This should just be viewed as an educational research, and please do not do this in game.
If you want to take this repo down, discord @louissiu

global = in-game & social

Surface Level:
-> [global] uses ALTCHA, a hash based solver -> vulnerable to attacks as it can be solved just by SHA-256 salt bruteforce
-> [global] ALTCHA tied to IP limit based on requests being sent
-> [in-game] matchmaking is through XHR request without any encryption / obfuscation, even user-agent isn't required atp
-> [social] index, social, class, config js are heavily obfuscated but easily debugged and hooked onto (even dynamic analysis is enough to reverse engineer the API)
-> [ws] uses msgpack, no obfuscation = requires the knowing of every variable, like k (kill feed), h (health), ai (other opponent's positions)

# Proof of concepts
1. Alive Connection in ws:
-> send patR [ping access token] to refresh every 25 second, ensure it's lower than 30000ms 
```eyJ0cyI6MTc3NDg0MDkzNzIzMywidWEiOiJiMTdhNmQ1M2E3MWFiYjliIn0.16097882619c13a899dedc7a077fda48``` from /ws/ping
-> f"wss://{host}/ws?pat={pat_token}&at={login_token}" # at_token isn't required
-> can be used for scraping market stuff

2. Joining a guest in ws:
  1. fetch access_token (previously mentioned)
  2. fetch validation_token from /generate-token
  3. fetch game list from /game-list?
  4. fetch domain info from /seek-game? using
             "hostname": "krunker.io",
            "region": "sgp",
            "autoChangeGame": "false",
            "validationToken": validation_token,
            "game": game_id,
            "dataQuery": self.game_version,
            "accessToken": access_token
  which returns r["host"], r["clientId"]
  5.         ws_url = (f"wss://{ws_host}/ws"
                  f"?gameId={self.game_id}"
                  f"&clientKey={self.client_id}"
                  f"&clientUID={self.frvr_id}"
                  f"&at={self.access_token}")
  6. intial handshake (I did not check, as I'm not invovled into this sketchy things) this is just a demo of a guest not moving
             [["load"], 1, 15],
            [["sb", "welc", None], 3, 14],
            [["po"], 5, 13],
            [["v"], 0, 15],
            [["en", [0, 2482 + self.respawn_count, [-1, -1], -1, -1, 2, 0, 0, 1, -1, -1, 1, 0, -1, -1, -1, -1, -1, -1, 0, -1, -1, 1, 1, 1, -1, -1, -1, 0, [None, -1], -1, -1, -1, 1], 16, 18, False, False, False, False, False, False, None, False, False], 9, 2],
            [["q", 0, 0, "3333", 2, [0, -3142], {"0-4": -1, "0-5": 0, "0-6": 0, "0-7": 0, "0-8": 0, "0-9": 0, "0-10": 0, "0-11": 0, "0-12": 0, "0-13": 0, "0-14": 0}], 11, 1],
            [["q", 0, 2, "3333", 2], 13, 0],
            [["q", 0, 4, "3333", 2], 14, 15],
            [["q", 0, 6, "3310", 2], 6, 12],
            [["q", 0, 8, "1719", 2], 8, 11],
            [["q", 0, 10, "151617", 2], 10, 10],
    7. does this whole thing work? Of course no.

Endpoints:
[GET] /ws/ping -> ```{"token":"TOKEN.RAND_HEX","expiresIn":30000}```
It can be generated manually, but server has deicded that RAND_HEX and stored in server, so requires to ask the endpoint for this token
30000 isn't seconds as social spawns connection expire in 30 seconds, it's ms

[POST] /v1/auth/login -> {'accessToken': 'JWT_token', 'refreshToken': 'JWT_token', 'frvrId': 'uuid4'}
  JSON: {"platform": "anonymous"}
This is the AT token, it can be guest or logged in accounts, but in this case this is guest

[POST] /auth/login/username -> {'data': {'type': 'login_ok', 'login_token': '', 'access_token': ''}}
  JSON: {
    "username": username,
    "password": password
  }
  
WS Commands:
    # Leaderboard Players
    "LP_SCORE": ['r', 'leaders', 'player_score', None, None, None, 0, None],
    "LP_KILLS": ['r', 'leaders', 'player_kills', None, None, None, 0, None],
    "LP_WINS": ['r', 'leaders', 'player_wins', None, None, None, 0, None],
    "LP_TIMEPLAYED": ['r', 'leaders', 'player_timeplayed', None, None, None, 0, None],
    "L_CLANRANK": ['r', 'leaders', 'player_clan', None, None, None, 0, None],
    "LP_FOLLOWED": ['r', 'leaders', 'player_followed', None, None, None, 0, None],
    "LP_NUKES": ['r', 'leaders', 'player_nukes', None, None, None, 0, None],
    "LP_KR": ['r', 'leaders', 'player_funds', None, None, None, 0, None],
    "LP_SKINVALUE": ['r', 'leaders', 'player_skinvalue', None, None, None, 0, None],
    "LP_EVENTTIME": ['r', 'leaders', 'player_eventtime', None, None, None, 0, None],
    "LP_RANKED_MATCHES": ['r', 'leaders', 'player_ranked_matches', None, None, None, 0, None],

    # Market / stats
    "MARKET_STATS": ['r', 'market', 'stats', None, None, None, 0, None],
    "MARKET_BLACKM": ['r', 'market', 'blackm', None, None, None, 0, None],

    # Maps/Votes (unaccesible with websocket)
    # "MAPS_VOTES": ['r', 'maps', 'votes', None, None, None, 0, None],
    # "MODS": ['r', 'mods', None, None, None, None, 0, None],
    # "ITEMS": ['r', 'items', 'items', None, None, None, 0, None],

    # (search profile johnfklee)
    "CLAN": ['r', 'clan', None, None, None, None, 0, None],  # fill clan id/name
    "PROFILE": ['r', 'profile', None, None, None, None, 0, None],  # fill username

    # History trade stats (pst)
    "TRADE_HISTORY_3MO": ['pst', None, 3],  # fill username
    "TRADE_HISTORY_4MO": ['pst', None, 4],
    "TRADE_HISTORY_5MO": ['pst', None, 5],

    # PID message / listings
    "MESSAGE_WITH_PID": ['guf', None],     # fill pid
    "LISTINGS_WITH_PID": ['uml', None],   # fill pid

    # FEED
    "FEED_GLOBAL": ['r', 'feed', None, None, None, 0, 0, None],
    "FEED_FOLLOWING": ['r', 'feed', None, None, None, 1, 0, None],
    "FEED_CLAN_MESSAGE": ['r', 'feed', None, None, None, 2, 0, None], # requires account
    "FEED_HOT": ['r', 'feed', None, None, None, 4, 0, None],
    "FEED_GIVEAWAY": ['r', 'feed', None, None, None, 5, 0, None],

    # Real market (username + self-account)
    "REAL_MARKET": ['r', 'market', 'market', None, None, None, 0, None],     # fill (pid) + username
    "INVENTORY": ['r', 'market', 'inventory', None, None, None, 0, None],
    "TRADES": ['r', 'market', 'trades', None, None, None, 0, None],






