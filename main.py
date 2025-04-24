import requests
import random
import string

BASE_URL = "https://api.poketrade.duckdns.org/api"

main_account = {
    "email": "randysim9@gmail.com",
    "username": "Scrooge_McDuck",
    "password": "password"
}

def login(account):
    # get refresh and access token
    payload = {
        "username": account["username"],
        "password": account["password"]
    }

    response = requests.post(f"{BASE_URL}/token/", json=payload)

    if response.status_code != 200:
        raise Exception(f"Failed to login: {response.text}")
    
    refresh = response.json()["refresh"]
    
    response = requests.post(f"{BASE_URL}/token/refresh/", json={"refresh": refresh})

    if response.status_code != 200:
        raise Exception(f"Failed to refresh token: {response.text}")
    
    access = response.json()["access"]

    return {
        "access": access,
        "refresh": refresh
    }
    

def signup():
    # random email
    email = f"{''.join(random.choices(string.ascii_letters + string.digits, k=10))}@gmail.com"
    # random password
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    # random username
    username = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

    payload = {
        "email": email,
        "username": username,
        "password": password,
    }

    response = requests.post(f"{BASE_URL}/user/create/", json=payload)

    if response.status_code != 201:
        raise Exception(f"Failed to signup: {response.text}")
    
    return {
        "email": email,
        "password": password,
        "username": username
    }

def get_user_cards(username):
    url = f"{BASE_URL}/card/?owner={username}"

    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Failed to get user cards: {response.text}")

    return response.json()

def purchase_pack(access):
    url = f"{BASE_URL}/cards/random/"

    payload = {
        "count": 3
    }

    response = requests.post(url, json=payload, headers={"Authorization": f"Bearer {access}"})

    if response.status_code != 201:
        raise Exception(f"Failed to purchase pack: {response.text}")
    
    return response.json()

def sell_card(card_id, price, access):
    url = f"{BASE_URL}/cards/marketplace/"

    payload = {
        "card_id": card_id,
        "price": price
    }

    response = requests.post(url, json=payload, headers={"Authorization": f"Bearer {access}"})

    if response.status_code != 200:
        raise Exception(f"Failed to sell card: {response.text}")
    
    return response.json()

def buy_card(card_id, access):
    url = f"{BASE_URL}/cards/purchase/"

    payload = {
        "card_id": card_id
    }

    response = requests.post(url, json=payload, headers={"Authorization": f"Bearer {access}"})

    if response.status_code != 200:
        raise Exception(f"Failed to buy card: {response.text}")
    
    return response.json()

# claim a welcome pack (apparently this is how you do it)
def claim_welcome_pack(access):
    url = f"{BASE_URL}/cards/random/"

    payload = {
        "welcome_pack": True
    }
    response = requests.post(url, json=payload, headers={"Authorization": f"Bearer {access}"})

    if response.status_code != 201:
        raise Exception(f"Failed to claim welcome back: {response.text}")
    
    return response.json()

# Creates clients that buy your shitty cards using the welcome bonus
def gain_creds(clients=20):
    tokens = login(main_account)
    gained_creds = 0

    for _ in range(clients):
        main_cards = get_user_cards(main_account["username"])

        if not main_cards:
            purchase_pack(tokens["access"])
            main_cards = get_user_cards(main_account["username"])

        # sort by rarity
        rarity_order = ['common', 'uncommon', 'rare', 'ultra_rare', 'legendary', "mythical"]

        card_to_sell = sorted(main_cards, key=lambda x: rarity_order.index(x["rarity"]))[0]

        if card_to_sell is None:
            print("No cards to sell")
            return
        
        # sell card
        sell_card(card_to_sell["id"], 250, tokens["access"])

        client_account = signup()
        client_tokens = login(client_account)

        # claim welcome pack
        res = claim_welcome_pack(client_tokens["access"])

        # buy card
        buy_card(card_to_sell["id"], client_tokens["access"])
        gained_creds += 250
    
    print(f"Gained {gained_creds} credits")

# you can spam welcome packs! there's no limit!
def spam_welcome_packs(packs=20):
    tokens = login(main_account)
    creds = 0

    for _ in range(packs):
        claim_welcome_pack(tokens["access"])
        creds += 250
    
    print(f"Gained {creds} credits")
    
    
if __name__ == "__main__":
    gain_creds(20)