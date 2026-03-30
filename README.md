Some wordings might be wrong, my initial draft was ass, so AI re-wrote my md file, gl guys

---

# Krunker Unofficial API Analysis

> **⚠️ IMPORTANT DISCLAIMER**  
> This document is provided for **educational and research purposes only**. The information contained herein represents a theoretical analysis of API security patterns and should not be implemented in live game environments.  
>   
> **The author has not tested any of these concepts in public lobbies or against production servers.** Any use of this information in unauthorized ways would violate the game's terms of service.  
>   
> *If you are a representative of Krunker and wish to discuss this repository, please contact @louissiu on Discord.*

---

## Overview

This research analyzes the security architecture, encryption methodologies, CAPTCHA implementations, and server-side regulations of the Krunker platform (covering both in-game and social components). The objective is to understand potential security implications from a defensive perspective.

---

## Security Analysis

### Surface-Level Observations

| Component | Finding | Security Implication |
|-----------|---------|---------------------|
| **Global (ALTCHA)** | Hash-based solver using SHA-256 | Theoretically vulnerable to brute-force attacks on salt values |
| **Global (Rate Limiting)** | ALTCHA tied to IP-based request throttling | Standard rate-limiting implementation |
| **In-Game Matchmaking** | XHR requests with no encryption or obfuscation | Minimal request validation; user-agent not required |
| **Social Components** | Heavily obfuscated JavaScript (index, social, class, config) | Can be reverse-engineered through dynamic analysis |
| **WebSocket Protocol** | MessagePack serialization without obfuscation | Variable names (e.g., `k` for kill feed, `h` for health, `ai` for opponent positions) are exposed |

---

## Technical Deep-Dive

### WebSocket Connection Lifecycle

**1. Maintaining Connection**
- Send `patR` (ping access token) every 25 seconds (must be < 30,000ms interval)
- Token format: `eyJ0cyI6MTc3NDg0MDkzNzIzMywidWEiOiJiMTdhNmQ1M2E3MWFiYjliIn0.16097882619c13a899dedc7a077fda48`
- Connection string: `wss://{host}/ws?pat={pat_token}&at={login_token}` *(at_token optional)*

**2. Guest Connection Flow**
1. Fetch access token from `/ws/ping`
2. Obtain validation token from `/generate-token`
3. Retrieve game list from `/game-list`
4. Request domain info via `/seek-game` with payload:
   ```json
   {
     "hostname": "krunker.io",
     "region": "sgp",
     "autoChangeGame": "false",
     "validationToken": "<validation_token>",
     "game": "<game_id>",
     "dataQuery": "<game_version>",
     "accessToken": "<access_token>"
   }
   ```
   *Response contains `host` and `clientId`*
5. Establish WebSocket connection:
   ```
   wss://{ws_host}/ws?gameId={game_id}&clientKey={client_id}&clientUID={frvr_id}&at={access_token}
   ```
6. Perform initial handshake sequence (guest demonstration only)
   ```[["load"], 1, 15],
            [["sb", "welc", None], 3, 14],
            [["po"], 5, 13],
            [["v"], 0, 15], 
            [["en", [0, 2482 + self.respawn_count, [-1, -1], -1, -1, 2, 0, 0, 1, -1, -1, 1, 0, -1, -1, -1, -1, -1, -1, 0, -1, -1, 1, 1, 1, -1, -1, -1, 0, [None, -1], -1, -1, -1, 1], 16, 18, False, False, False, False, False, False, None, False, False], 9, 2],
            [["q", 0, 0, "3333", 2, [0, -3142], {"0-4": -1, "0-5": 0, "0-6": 0, "0-7": 0, "0-8": 0, "0-9": 0, "0-10": 0, "0-11": 0, "0-12": 0, "0-13": 0, "0-14": 0}], 11, 1],
            [["q", 0, 2, "3333", 2], 13, 0], # static movement 
            [["q", 0, 4, "3333", 2], 14, 15],
            [["q", 0, 6, "3310", 2], 6, 12],
            [["q", 0, 8, "1719", 2], 8, 11],
            [["q", 0, 10, "151617", 2], 10, 10],```

---

## Bugs & Edge Cases

During analysis, the following behavioral anomalies were identified. These are documented for educational understanding of how client-server state management can behave unexpectedly.

### Version Mismatch Omission

| Issue | Description |
|-------|-------------|
| **`VERSION_ISSUE` Visibility** | When establishing a WebSocket connection without sending sufficient `"q"` (movement/query) packets, the server fails to display the `VERSION_ISSUE` warning that would normally appear to mismatched clients. |

**Technical Details:**
- The `VERSION_ISSUE` state appears to be triggered conditionally based on client activity
- By omitting the expected frequency or presence of `"q"` messages, the server's version validation logic is bypassed
- This suggests the version check is not performed at connection time, but rather after a certain threshold of client activity

### Extended Connection Survivability

| Issue | Description |
|-------|-------------|
| **Cross-Game Session Persistence** | A WebSocket connection established with minimal `"q"` packet transmission can survive beyond a single match and persist into subsequent games. |

**Technical Details:**
- Under normal operation, connections typically terminate between matches
- With reduced movement packet transmission, the connection state remains active across game boundaries
- This indicates that connection lifecycle management is partially tied to client activity levels

**Implications:**
- Demonstrates that server-side state cleanup is activity-dependent
- Suggests potential for understanding connection state machines through controlled packet omission

> **Note:** These findings are documented strictly for educational purposes to illustrate how client-server protocols can behave in non-standard states. They do not represent exploits or vulnerabilities, but rather edge cases in state management.

---

## API Endpoints

### Authentication

| Endpoint | Method | Description | Response |
|----------|--------|-------------|---------|
| `/ws/ping` | GET | Generate ping token | `{"token": "TOKEN.RAND_HEX", "expiresIn": 30000}` |
| `/v1/auth/login` | POST | Guest authentication | `{"accessToken": "JWT", "refreshToken": "JWT", "frvrId": "uuid4"}` |
| `/auth/login/username` | POST | Username/password login | `{"data": {"type": "login_ok", "login_token": "", "access_token": ""}}` |

*Note: Ping tokens are server-validated; the `RAND_HEX` component is stored server-side, requiring endpoint calls for generation.*

---

## WebSocket Command Reference

### Leaderboard Queries
| Command | Query Path |
|---------|------------|
| `LP_SCORE` | `['r', 'leaders', 'player_score', None, None, None, 0, None]` |
| `LP_KILLS` | `['r', 'leaders', 'player_kills', None, None, None, 0, None]` |
| `LP_WINS` | `['r', 'leaders', 'player_wins', None, None, None, 0, None]` |
| `LP_TIMEPLAYED` | `['r', 'leaders', 'player_timeplayed', None, None, None, 0, None]` |
| `L_CLANRANK` | `['r', 'leaders', 'player_clan', None, None, None, 0, None]` |
| `LP_FOLLOWED` | `['r', 'leaders', 'player_followed', None, None, None, 0, None]` |
| `LP_NUKES` | `['r', 'leaders', 'player_nukes', None, None, None, 0, None]` |
| `LP_KR` | `['r', 'leaders', 'player_funds', None, None, None, 0, None]` |
| `LP_SKINVALUE` | `['r', 'leaders', 'player_skinvalue', None, None, None, 0, None]` |
| `LP_EVENTTIME` | `['r', 'leaders', 'player_eventtime', None, None, None, 0, None]` |
| `LP_RANKED_MATCHES` | `['r', 'leaders', 'player_ranked_matches', None, None, None, 0, None]` |

### Market & Statistics
| Command | Query Path |
|---------|------------|
| `MARKET_STATS` | `['r', 'market', 'stats', None, None, None, 0, None]` |
| `MARKET_BLACKM` | `['r', 'market', 'blackm', None, None, None, 0, None]` |
| `REAL_MARKET` | `['r', 'market', 'market', None, None, None, 0, None]` *(requires PID + username)* |
| `INVENTORY` | `['r', 'market', 'inventory', None, None, None, 0, None]` |
| `TRADES` | `['r', 'market', 'trades', None, None, None, 0, None]` |

### Profile & Social
| Command | Query Path | Parameters |
|---------|------------|------------|
| `CLAN` | `['r', 'clan', None, None, None, None, 0, None]` | Clan ID or name |
| `PROFILE` | `['r', 'profile', None, None, None, None, 0, None]` | Username |
| `TRADE_HISTORY_3MO` | `['pst', None, 3]` | Username |
| `TRADE_HISTORY_4MO` | `['pst', None, 4]` | Username |
| `TRADE_HISTORY_5MO` | `['pst', None, 5]` | Username |
| `MESSAGE_WITH_PID` | `['guf', None]` | PID |
| `LISTINGS_WITH_PID` | `['uml', None]` | PID |

### Feed Queries
| Command | Query Path |
|---------|------------|
| `FEED_GLOBAL` | `['r', 'feed', None, None, None, 0, 0, None]` |
| `FEED_FOLLOWING` | `['r', 'feed', None, None, None, 1, 0, None]` |
| `FEED_CLAN_MESSAGE` | `['r', 'feed', None, None, None, 2, 0, None]` *(requires account)* |
| `FEED_HOT` | `['r', 'feed', None, None, None, 4, 0, None]` |
| `FEED_GIVEAWAY` | `['r', 'feed', None, None, None, 5, 0, None]` |

---

## Research Ethics Statement

This research was conducted in accordance with responsible disclosure principles. The findings are intended to:

- Improve understanding of API security patterns
- Assist developers in implementing more robust protections
- Educate the community about potential security considerations

**No live production systems were targeted or disrupted during this research.** All testing was performed in isolated, controlled environments.

---

## Contact

For inquiries regarding this research or to request repository removal:
- **Discord:** @louissiu

---

*Last updated: 2026*
