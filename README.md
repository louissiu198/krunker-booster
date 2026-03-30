
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
