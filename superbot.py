
import json
import os
import time
import urllib.parse
import urllib.request

TG = f"https://api.telegram.org/bot{os.environ['TELEGRAM_TOKEN']}"
HERO = f"https://superheroapi.com/api/{os.environ['SUPERHERO_TOKEN']}"


def chamar(url, dados=None):
    corpo = json.dumps(dados).encode() if dados else None
    req = urllib.request.Request(url, corpo, {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=40))


def buscar(nome):
    r = chamar(f"{HERO}/search/{urllib.parse.quote(nome)}")
    return r["results"][0] if r.get("response") == "success" else None


def ficha(h):
    p = h["powerstats"]
    return (
        f"{h['name']}\n"
        f"Editora: {h['biography']['publisher']}\n\n"
        f" Inteligência: {p['intelligence']}\n"
        f" Força: {p['strength']}\n"
        f" Velocidade: {p['speed']}\n"
        f" Durabilidade: {p['durability']}\n"
        f" Poder: {p['power']}\n"
        f" Combate: {p['combat']}"
    )


def responder(chat_id, texto):
    if texto.startswith("/start"):
        chamar(f"{TG}/sendMessage", {"chat_id": chat_id, "text": "Mande o nome de um herói (em inglês). Ex: batman"})
        return

    heroi = buscar(texto)
    if not heroi:
        chamar(f"{TG}/sendMessage", {"chat_id": chat_id, "text": "Herói não achado ou nome inválido."})
        return

    chamar(f"{TG}/sendPhoto", {"chat_id": chat_id, "photo": heroi["image"]["url"], "caption": ficha(heroi)})


offset = 0
print("Bot rodando...")
while True:
    try:
        updates = chamar(f"{TG}/getUpdates", {"timeout": 30, "offset": offset})["result"]
        for u in updates:
            offset = u["update_id"] + 1
            msg = u.get("message", {})
            if msg.get("text"):
                responder(msg["chat"]["id"], msg["text"])
    except Exception as e:
        print("erro:", e)
        time.sleep(5)