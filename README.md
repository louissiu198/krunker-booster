[# Krunker Nukester - Demo & Walkthrough
A huge exploit of krunker.io in terms of networking, packet handling and server side protection.

So we all know that krunker is a browser game with frontend powered by threejs and backend by some kind of typescript/javascript servers.
The logic of the game is the Frontend (USER) connects -> with the Backend (SERVER) to perform some actions which it will get recorded to mark a successful action (ie. shooting one bullet)
This is done through websocket (msgpack module), websocket is a communication protocol that provides two way connection between a client and a server

What is basically a nukester bot? 
It's just basically spawning bots like accounts or guest into lobby for people to earn nukes

How to make it?
You'd need to know basic intercepting knowledge, computer, chrome (any browser, but easiest in chrome), brain
Chrome, press Ctrl + Shift + i, open DevTools

You should see console page, then navigate to Network section, there's a lot of data
In easier terms, commonly you only need to recognize 3 types of network request there is:
XHR, WS (websocket), Files (including json, css, js, png)
XHR includes GET, POST, OPTIONS (3 widely used / seen in frontend)

The response of data usually brings valuable information:

Now, click the button FETCH/XHR, which the DevTools would give you all the XHR requests
Scroll through them to find important informations, make the request url has "krunker.io" in it

1. POST https://crucible.frvr.com/v1/auth/login
2. GET https://matchmaker.krunker.io/generate-token 1783406272:n1jiX3/4vaKRN5U7Iu+1bGbgJhxK+oHougxqUTVHHh0=
3. GET https://matchmaker.krunker.io/game-info?game=SIN%3Afrbx3 ["SIN:frbx3","sgp",6,8,{"g":1,"i":"Subzero","c":0,"v":"cfuB2H8F8hb9edj65CKP0UiaTxAjmqsD","m":3,"cm":0},3]
4. GET https://matchmaker.krunker.io/seek-game?hostname=krunker.io&region=sgp&autoChangeGame=false&validationToken=1783405986%3A8MH7MQfAUYSrOZSYtIDeGkv1aVXoM4sHsgDtJRCrQQY%3D&dataQuery=%7B%22v%22%3A%22cfuB2H8F8hb9edj65CKP0UiaTxAjmqsD%22%7D&accessToken=eyJhbGciOiJSUzI1NiIsImtpZCI6ImtleS0wIiwidHlwIjoiSldUIn0.eyJleHAiOjE3ODM0ODgyNzAsImV4dHJhIjp7ImlkZW50aWZpZXIiOiI2YTRjOGQ4ZGE0MGQ4ZGMzZmUzY2I5YTEiLCJwbGF0Zm9ybSI6ImFub255bW91cyIsInZlcmlmaWVkIjp0cnVlfSwiaWF0IjoxNzgzNDAxODcwLCJpc3MiOiJGUlZSIiwic3ViIjoiMjY5M2JjZWEtNGZmYi00OWQzLWIwMGYtYWZkOWU1NmE1NmRhIn0.XCyPCMLximC5-y-1mVU-zi-hp4LxJLqm4y_TEgEWlFTO3G50ENCKoCE9wiUFdhqXooXZg-ExHX8mwTKiDOa8YqJkm30F8x0XuL7CIaLC80psLYxufsbI4QH5Jc4YfSEFWYrUIZUBSyir70F73hFvTYZijCZSnE4eCd2FqoycfwPYUTNLBtQQ176mOtvOZiIN5SDUkC2h3ryTl07v7WML_bqkS-H_vO6iyGbFPbeqqXrI3eZLCbX0HhtDFL7SJZs3YvYDQY2DZ6fWO_WKwsjq6MO8kLwTJn6SFLFbBcveT-LZvXR9ssaQ3ksGb1d7xpy1yN2xKZkviYr37aUAF2fAPw {
    "changeReason": null,
    "gameId": "SIN:138rs",
    "host": "lobby-l27ld-29dg7.singapore.krunker.io",
    "port": 3000,
    "clientId": "b8cf1272-3dad-4eec-9d02-b3e78d4d3c22",
    "data": {
        "t": "d",
        "p": 68.85074,
        "l": 28.467729831339422,
        "d": 40.383010168660576,
        "b": 3,
        "n": false
    }
}
4. WS f"wss://{host}/ws?gameId={gid}&clientKey={ckey}&at={at}" 

Now we know these 4 requests is the core of how a players joins a lobby, we will investigate further.
=> websocket has a lot of messages between clients and user, and in msgpack format, the core content look like this
['load'],
['sb', 'welc', 'Username'],
['en', [0, 2482, [-1, -1], -1, -1, 2, 0, 0, 1, -1, -1, 0, 0, -1, -1, -1, -1, -1, -1, 0, -1, -1, 1, 1, 1, -1, -1, -1, 0, [None, -1], -1, -1, -1, 1], 16, 18, False, False, False, False, False, False, None, False, False],
['q', 0, 0, '1233', 2, [0, -1571, 0, 1], {'0-4': -1, '0-5': 0, '0-6': 0, '0-7': 0, '0-8': 0, '0-9': 0, '0-10': 0, '0-11': 0, '0-12': 0, '0-13': 0, '0-14': 0}],
['q', 0, 2, [7, 10, 3, 3, 5, 7], 0, [0, -1570, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]],

Before their message it sent, they are further wrapped in the format  of [content, x, y] where x, y are krunker.io's boilerplate states (I call them as counters), which serves for 3 purposes.
1. Deduplication so no extra packets are being sent to server
2. Compression, enabling data like coordinates to be sent, making it more efficient, allowing more low spec computers to play
3. [Important] Anti-cheat, most reverse engineers might only see the surface, might think randomly placing a number or keeping it static will make it work, which is why it's a big error. (each big krunker update also updates the counter)

After the counter are wrapped, they look like this, 7/7/2026's version
[['load'], 0, 3],
[['sb', 'welc', 'Username'], 0, 6],
[['en', [0, 2482, [-1, -1], -1, -1, 2, 0, 0, 1, -1, -1, 0, 0, -1, -1, -1, -1, -1, -1, 0, -1, -1, 1, 1, 1, -1, -1, -1, 0, [None, -1], -1, -1, -1, 1], 16, 18, False, False, False, False, False, False, None, False, False], 0, 9],
We do not need to understand complex calculation behind this, just by observing 4-9 outcomes, we can see the pattern, x only adds 1 if y > 16 (which is 256 bits), and y adds 3 each time (both resets to 0 after it exceeds the maximum bit)
class counter:
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

the older version is much complex, 15/4/2026's version
[['load'], 1, 3],
[['sb', 'welc', 'Username'], 2, 6],
[['en', [0, 2482, [-1, -1], -1, -1, 2, 0, 0, 1, -1, -1, 0, 0, -1, -1, -1, -1, -1, -1, 0, -1, -1, 1, 1, 1, -1, -1, -1, 0, [None, -1], -1, -1, -1, 1], 16, 18, False, False, False, False, False, False, None, False, False], 3, 9],
with some certain values it will skip, like after the value of [5, 15], you would think it would be [6, 2], however its [7, 2]

py
class counter:
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



](https://github.com/notemrovsky/tiktok-reverse-engineering)
