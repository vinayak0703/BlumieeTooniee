import asyncio

from blum import Blum
from language import Lang

async def main():
    blum = Blum()

    query_uri, token = get_input()
    print("\nInitializing Blum")
    await blum.start(query_uri, token)
    
    print("Ok bie")

def get_input():
    query_uri = None
    token = None

    print(Lang.LOGIN_PROMPT)
    cmd = input("Enter command: ")

    if cmd == "1":
        query_uri = input("Enter query uri: ")
    elif cmd == "2":
        token = input("Enter auth token: ")
    else:
        print("Bruv... fr?")
        return get_input()
    
    return query_uri, token

if __name__ == "__main__":
    asyncio.run(main())