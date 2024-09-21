import asyncio
import aiohttp
import random

from language import Lang

POINTS = [240, 280]
GAME_DELAY = [35, 37]

class Blum:
    def __init__(self):
        self.username = None
        self.user_agent = 'Mozilla/5.0 (Linux; Android 14; K) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/128.0.6613.88 Mobile Safari/537.36'
        self.headers = {'User-Agent': self.user_agent}
        self.tickets = 0
        self.auth_token = None
        self.query_uri = None

        
    async def start(self, query_uri, token):
        self.session = await self.create_aiohttp()

        if query_uri:
            login = await self.initQuery(query_uri)
        elif token:
            login = await self.initToken(token)
        else:
            await self.session.close()
            return

        if not login:
            print("Error logging in. Exiting")
            await self.session.close()
            return
    
        print(Lang.START_BLUM)

        cmd = None
        while True:
            check = await self.check_login()
            if not check:
                break

            await asyncio.sleep(5)

            await self.get_balance()

            cmd = input(Lang.BLUM_PROMPT)
            if cmd == "1":
                await self.play_ticket()
            elif cmd == "2":
                break
            else:
                print("Invalid command")
                continue

        await self.session.close()


    async def initQuery(self, query_uri):
        self.query_uri = query_uri
        self.session.headers.pop('Authorization', None)
        json_data = {"query": query_uri}

        retries = 0
        while True:
            resp = await self.session.post("https://user-domain.blum.codes/api/v1/auth/provider/PROVIDER_TELEGRAM_MINI_APP", json=json_data)

            if resp.status == 520:
                if retries == 6:
                    print("Max Retries Exceeded. Ensure your query uri is correct")
                    return False
                print("Error 520, retrying in 10 seconds (exit script something feels wrong)")
                await asyncio.sleep(10)
                retries += 1
                continue
            else:
                break

        resp_json = await resp.json()
        self.auth_token = "Bearer " + resp_json.get("token").get("access")
        self.session.headers['Authorization'] = self.auth_token
        await asyncio.sleep(5)
        return True


    async def initToken(self, token):
        self.auth_token = token
        self.session.headers['Authorization'] = self.auth_token
        return True



    async def get_me(self):
        r = await self.session.get("https://user-domain.blum.codes/api/v1/user/me")
        self.username = (await r.json()).get("username")


    async def check_login(self):
        r = await self.session.get("https://user-domain.blum.codes/api/v1/user/me")
        
        if r.status == 200:
            if self.username is None:
                self.username = (await r.json()).get("username")
                print(f"Logged in as {self.username}")
            return True
        else:
            print("Session expired or something went wrong.")
            print("Refresh token manually (get new token)")
            return False
        


    async def get_balance(self):
        r = await (await self.session.get("https://game-domain.blum.codes/api/v1/user/balance")).json()
        points = r.get('availableBalance')
        self.tickets = r.get('playPasses')
        print(Lang.BLUM_INFO.format(points, self.tickets))
        await asyncio.sleep(random.randint(1, 5))


    async def play_ticket(self):
        if self.tickets == 0:
            print("Motherducker..... No tickets left to play")
            return
        
        ticket_count = int(input("Enter the number of tickets to play: "))
        if ticket_count > self.tickets:
            print(f"Bro You Blind? You don't have {ticket_count} tickets")
            return
        
        for i in range(ticket_count):
            print("\nStarting game number", i+1)

            game_id = await self.get_game_id()

            if not game_id:
                print("Error getting game id (sobs.) probably ticket wasted")
                print("Quiting for safety")
                return
            
            # Sleep until game finishes on the server side
            game_duration = random.uniform(*GAME_DELAY)
            print(f"The game will run for {game_duration} seconds. Waiting for it to finish")
            await asyncio.sleep(game_duration)


            points = random.randint(*POINTS)
            json_data = {"gameId": game_id, "points": points}

            resp = await self.session.post("https://game-domain.blum.codes/api/v1/game/claim", json=json_data)
            txt = await resp.text()

            if txt != 'OK':
                print(f"Error playing ticket: {txt}")

            print(f"Played ticket with {points} points. Enjoi")

            sleep = random.randint(5, 8)
            print(f"Sleeping for {sleep} seconds\n")
            await asyncio.sleep(sleep)
            self.tickets -= 1


    async def get_game_id(self):
        resp = await self.session.post("https://game-domain.blum.codes/api/v1/game/play")
        if resp.status == 200:
            return (await resp.json()).get("gameId")
        else:
            return False


    async def create_aiohttp(self):
        return aiohttp.ClientSession(
            headers=self.headers, 
            trust_env=True, 
            connector=aiohttp.TCPConnector(verify_ssl=False),
            timeout=aiohttp.ClientTimeout(120))