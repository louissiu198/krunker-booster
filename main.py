import random
import threading
import websockets
import json, time, asyncio
from httpx import Client, get
from urllib.parse import urlencode
from libs.ws import ws
from libs.route import route
from libs.utils import utils
from libs.counter import counter
from python_socks.async_.asyncio import Proxy

with open("./input/config.json", "r") as f:
    config = json.load(f)

router = route()

##### DYNAMIC
LOCK = threading.Lock()
V = config["v"]
REGION = config["region"]
SVC_URL = config["url"]["svc"]
FRVR_URL = config["url"]["frvr"]
DEFAULT_URL = config["url"]["default"]
MATCHMAKING_URL = config["url"]["matchmaking"]

SEQMSG_TIMEOUT = 0.5
PING_TIMEOUT = 5
MAX_RETRIES = 5

accounts = [] # code remove from preview
user_agent = None # code remove from preview


# Line 31-33: code remove from preview


def get_proxy(country, duration=30):
    pass
    # Line 45: code remove from preview

class logger:
    def __init__(self, bot_id = None, show: bool = True):
        self.show = show
        self.bot_id = bot_id
    
    def info(self, msg):
        if self.show:
            prefix = f"[Bot-{self.bot_id}] " if self.bot_id else ""
            with LOCK:
                print(f"{prefix}{msg}")
    
    def error(self, msg):
        prefix = f"[Bot-{self.bot_id}] " if self.bot_id else ""
        with LOCK:
            print(f"❌ {prefix}{msg}")

class bot:
    def __init__(self, agid: str, botid: int, log: bool = True, account: str = None) -> None:
        self.logger = logger(botid, log)
        self.botid = botid
        self.target_game_id = agid

        # Line 63-68: code remove from preview    

        for attempt in range(MAX_RETRIES):
            if null: # code remove from preview    
                return
            try:
                self.proxy = null
                self.req = Client(proxy=self.proxy)
                self.ip = self.req.get("https://api.ipify.org").text
                self.u = utils(self.req)
                self.c = counter(0, 3)
                self.at = self.u.get_access_token()
                self.vt = self.u.fetch_validation_token()
                if account:
                    self.at = account.split(":")[2]
                self.hst, self.cid, self.gid = self.seek_game(agid)
                break
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1}/{MAX_RETRIES} failed: {e}")
                if "GameFull" in str(e) or "Lobby is full" in str(e):
                    pass
                    # Line 83-89: code remove from preview    

        self.state = {
            "is_dead": False,
            "game_ended": False,
        }

        # Line 92-100: code remove from preview (proper loop per thread)

    async def start(self):
        await self.connect_ws(self.hst, self.gid, self.cid, self.at)

    def stop_b(self):
        global stop_b
        stop_all_bots = True
        with LOCK:
            # Line 100-113: code remove from preview (proper loop per thread)
            self.logger.info("🛑 All bots stopped due to full lobby")

    def seek_game(self, game_id: str = None) -> (str, str, str):
        params = {
            "hostname": DEFAULT_URL.split("//")[1],
            "region": REGION,
            "autoChangeGame": "false",
            "validationToken": self.vt,
            "dataQuery": json.dumps(V),
            "accessToken": self.at,
        }
        if game_id:
            params["game"] = game_id
        params = urlencode(params)
        
        try:
            response = self.req.get(f"{MATCHMAKING_URL}/seek-game?{params}")
            game_data = response.json()
            
            if "clientId" in game_data and "host" in game_data:
                return game_data["host"], game_data["clientId"], game_data["gameId"]
            elif "error" in game_data:
                if game_data["error"] == "GameFull":
                    # code remove from preview 
                    return False, False, False
        except Exception as e:
            pass
            # code remove from preview 
        return False, False, False

    @staticmethod
    def fetch_game_list():
        try:
            glist = get(f"{MATCHMAKING_URL}/game-list?hostname=krunker.io").json()
        except:
            return None
            
        games = glist.get('games', [])
        if not games:
            return None
        
        print("\n" + "="*80)
        print("Available Servers:")
        print("-"*80)
        
        target_games = []
        for game in games:
            if game[1] == "sgp": # ur region
                target_games.append(game)
        
        if not target_games:
            target_games = games
        
        for i, game in enumerate(target_games[:50]):
            print(f"  {i}: {game[0]} | {game[1]} | {game[4].get('i', 'Unknown')} | {game[2]}/{game[3]} players | {game[5] if len(game) > 5 else 0}ms")
        
        if len(target_games) > 50:
            print(f"  ... and {len(target_games) - 50} more games")
        print("-"*80)
        
        while True:
            gId = input("\nEnter the Game ID you want to join: ").strip()
            if not gId:
                continue
            if gId.startswith("https://"):
                gId = gId.split("=")[1]
            found_game = None
            for game in target_games:
                if game[0] == gId:
                    found_game = game
                    break
            
            if found_game:
                print(f"\nSelected game: {found_game[0]} | {found_game[1]} | {found_game[4].get('i', 'Unknown')} | {found_game[2]}/{found_game[3]} players")
                return gId
            return gId
    
    async def spawn(self, websocket, st_index: int = 0):
        # code remove from preview 
        seq = router.get()
        await asyncio.sleep(3)
        
        for s in seq[st_index:]:
            if null: # code remove from preview 
                return
            x, y = self.c.current()
            try:
                await websocket.send(ws.encode_msgpack([s, x, y]))
            except Exception:
                return  
            await asyncio.sleep(0.05)
        
        self.spawn_active = False

    async def handle_ws_rsp(self, websocket):
        async for message in websocket:
            if null: # code remove from preview 
                break
            obj = ws.decode_msgpack_stream(message)
            if obj:
                for msg in obj:
                    if isinstance(msg, list) and len(msg) > 0:
                        cmd = msg[0]
                        context = msg[1] if len(msg) > 1 else None
                        if cmd == "h" and context == 0 and len(msg) > 3:
                            self.logger.info("Player dead - stopping spawn sequence")
                            # code remove from preview 
                        elif cmd == "t" and len(msg) > 2 and msg[2] == 1:
                            self.logger.info(f"Timer: {cmd} {context} {msg[2]}")
                            countdown = int(context.split(":")[1])
                            self.logger.info(f"Game ended, stopping spawn sequence")
                            self.spawn_active = False
                            # code remove from preview 
            await asyncio.sleep(0)
    
    async def respawn(self, websocket):
        # code remove from preview 
        await asyncio.sleep(1)
        await self.spawn(websocket, 2)  

    async def connect_ws(self, game_ws_host: str, gid: str, ckey: str, at: str):
        headers = {} # code remove from preview 
        
        current_host = game_ws_host
        current_gid = gid
        current_ckey = ckey
        current_at = at
        self.cid = ckey 
        
        while null: # code remove from preview 
            ws_url = f"wss://{host}/ws?gameId={gid}&clientKey={ckey}&at={at}" # code remove from preview             
            try:
                proxy = Proxy.from_url(self.proxy)
                sock = await proxy.connect(dest_host=current_host, dest_port=443)

                async with websockets.connect(
                    ws_url,
                    sock=sock,
                    additional_headers=headers,
                    ping_interval=None,
                    ping_timeout=None
                ) as websocket:
                    self.websocket = websocket
                    self.logger.info("Connected successfully!")
                    
                    tsk1 = asyncio.create_task(self.spawn_entity(websocket))
                    tsk2 = asyncio.create_task(self.handle_ws_rsp(websocket))
                    
                    await asyncio.gather(tsk1, tsk2, return_exceptions=True)
                    self.logger.error("Connection dropped normally or task sequence completed.")
                    
            except websockets.exceptions.ConnectionClosed as e:
                # code remove from preview 
                pass
            except (OSError, asyncio.TimeoutError) as e:
                # code remove from preview 
                pass
            except Exception as e:
                # code remove from preview 
                pass

            # code remove from preview (if bot is kicked, recovery logic)       

def run():
    global stop_all_bots
    
    gId = bot.fetch_game_list()
    # code remove from preview 
    print(f"\nLaunching {tNum} bots...")
    threads = []
    
    for i in range(tNum):
        # code remove from preview 
        t = threading.Thread(
            target=lambda g=gId, b_id=i+1, l=log, acc=account: bot(g, b_id, l, acc), 
            name=f"Bot-{i+1}"
        )
        threads.append(t)
        t.start()
    
    try:
        # code remove from preview 
        for t in threads:
            t.join(timeout=2)
    except KeyboardInterrupt:
        # code remove from preview 
        for t in threads:
            t.join(timeout=1)

if __name__ == "__main__":
    run()