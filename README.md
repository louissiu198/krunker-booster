# 100 stars i drop a portable / web version of this shit out public / no cost to run at all (AI wrote this repo, i just ask it to explain to dummies, if you know all this ignore this bs)
# Krunker.io - Packet Wrapper & Protocol Reverse Engineering
**swuffy** contributed to the route.py => intercepting a full 4 min websocket send packets
Reverse engineering analysis of `krunker.io`'s websocket protocol, binary MessagePack payload wrappers, and the rolling state counters used for client-side protection.

## Overview

This repo contains analysis and documentation on how `krunker.io` handles networking. The frontend runs on **Three.js** and communicates with a **Node.js/TypeScript** backend via WebSockets using the `msgpack` module.

By replicating the client connection handshake, you can spin up automated bots or guest accounts into targeted game lobbies (commonly used to set up passive lobbies for nuke streaks).

*Note: This write-up covers both the current protocol counter and older variants. If an update breaks the code, use the DevTools method below to remap the values.*

---

## Table of Contents

* [Network Request Types](https://www.google.com/search?q=%23network-request-types)
* [The Connection Flow](https://www.google.com/search?q=%23the-connection-flow)
* [WebSocket Payload Layout](https://www.google.com/search?q=%23websocket-payload-layout)
* [The State Counter (Anti-Cheat)](https://www.google.com/search?q=%23the-state-counter-anti-cheat)
* [How to Debug & Log Packets](https://www.google.com/search?q=%23how-to-debug--log-packets)
* [Disclaimer](https://www.google.com/search?q=%23disclaimer)

---

## Network Request Types

To see what the game is doing, open your browser's DevTools (`Ctrl + Shift + I`) and head to the **Network** tab.

When analyzing the initial page load and asset fetching loop, you only need to care about 3 types of data:

| Type | Format / Methods | Purpose |
| --- | --- | --- |
| **XHR / Fetch** | `GET`, `POST` | Handles login authentication, matchmaker tokens, and fetching lobby details. |
| **WS** | Binary MessagePack | Real-time game events (shooting, positions, player actions). |
| **Files** | `.js`, `.json`, `.png`, `.obj` | Game scripts, asset meshes (`weapon_2.obj`, `melee_0.obj`), textures, and engine files. |

---

## The Connection Flow

Before the game opens a WebSocket connection, it hits the matchmaker endpoints to get routing data. To filter out asset spam, toggle the **Fetch/XHR** option in DevTools:

Filtering for `krunker.io` or `frvr.com` reveals the exact endpoint handshake sequence:

### 1. Authenticate Account

```http
POST https://crucible.frvr.com/v1/auth/login

```

### 2. Generate Matchmaker Token

```http
GET https://matchmaker.krunker.io/generate-token

```

Inspecting the request headers reveals the connection attributes and required CORS properties:

* **Response Example:** `1783406272:n1jiX3/4vaKRN5U7Iu+1bGbgJhxK+oHougxqUTVHHh0=`

### 3. Fetch Game Lobby Info

```http
GET https://matchmaker.krunker.io/game-info?game=SIN:frbx3

```

* **Response Example:**
```json
["SIN:frbx3","sgp",6,8,{"g":1,"i":"Subzero","c":0,"v":"cfuB2H8F8hb9edj65CKP0UiaTxAjmqsD","m":3,"cm":0},3]

```



### 4. Seek Game Endpoint

This gives you the final server host IP and access tokens needed to connect.

```http
GET https://matchmaker.krunker.io/seek-game?hostname=krunker.io&region=sgp...

```

* **Response JSON:**
```json
{
    "changeReason": null,
    "gameId": "SIN:138rs",
    "host": "lobby-l27ld-29dg7.singapore.krunker.io",
    "port": 3000,
    "clientId": "b8cf1272-3dad-4eec-9d02-b3e78d4d3c22",
    "data": { "t": "d", "p": 68.85074, "l": 28.4677, "b": 3, "n": false }
}

```



Using the data above, the client opens the WebSocket connection using this format:

```text
wss://{host}/ws?gameId={gameId}&clientKey={clientId}&at={accessToken}

```

---

## WebSocket Payload Layout

Once connected, data is sent as arrays serialized via MessagePack. A clean, raw client initialization exchange looks like this:

```javascript
['load']
['sb', 'welc', 'Username']
['en', [0, 2482, [-1, -1], -1, -1, 2, 0, 0, 1, -1, -1, 0, 0, -1, -1, -1, -1, -1, -1, 0, -1, -1, 1, 1, 1, -1, -1, -1, 0, [null, -1], -1, -1, -1, 1], 16, 18, false, false, false, false, false, false, null, false, false]

```

---

## The State Counter (Anti-Cheat)

Before messages are actually transmitted over the socket, they are wrapped in an envelope format: `[content, x, y]`.

`x` and `y` act as rolling validation counters. If you send static values or completely random numbers, the server will instantly disconnect you for bad packet sequence states.

### Current Logic

`y` adds 3 on every single packet. When `y + 3` crosses or equals `16`, `x` ticks up by 1 and resets the boundary via modulo 16.

```python
class Counter:
    def __init__(self, x: int = 0, y: int = 3):
        self.x = x
        self.y = y
    
    def current(self):
        c, v = self.x, self.y
        next_y = (self.y + 3) % 16
        if self.y + 3 >= 16:
            self.x = (self.x + 1) % 16
        self.y = next_y
        return c, v

```

### Legacy Logic

Older versions used a slightly more aggressive sequence skipping. For instance, after reaching `[5, 15]`, the code skipped `6` entirely and jumped straight to `[7, 2]`.

```python
class LegacyCounter:
    def __init__(self, x: int = 1, y: int = 3):
        self.x = x
        self.y = y

    def current(self):
        c, v = self.x, self.y
        next_y = (self.y + 3) % 16
        if self.y + 3 >= 16:
            self.x = (self.x + 2) % 16
        else:
            self.x = (self.x + 1) % 16
        self.y = next_y
        return c, v

```

---



---

## Disclaimer

This project is for educational and research purposes only. It is intended for documenting web protocol mechanics and security analysis. Use responsibly.
