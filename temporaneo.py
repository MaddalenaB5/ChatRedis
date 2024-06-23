import redis
import hashlib
import getpass

# Connetti al server Redis cloud del tuo collega con autenticazione
r = redis.Redis(host='redis-18934.c328.europe-west3-1.gce.redns.redis-cloud.com',
                port=18934,
                db=0,
                charset="utf-8",
                decode_responses=True,
                password='4GVWbKjMnaiMtHaX56tTNKODmzblmYtq')

# Converte la password in un hash per motivi di sicurezza
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def registrazione(username, password):
    if r.hexists("utenti", username):
        print("Nome Utente già utilizzato. Sceglierne un'altro...")
        return False
    password_hash = hash_password(password)
    dati_utente = {
        "nome": username,
        "password": password_hash,
        "contatti": [],
        "dnd": 0
        }
    
    r.hset("utenti", username, dati_utente)
    return True

def ricerca_utenti(nome):
    nomi_presenti = r.hkeys("utenti")
    risultati = []
    
    for nome_utente in nomi_presenti:
        if nome.lower() in nome_utente.lower():
            risultati.append(nome_utente)
        
        return risultati
    
    
def login(username, password):
    if not r.hexists("utenti", username):
        print("Nome utente inesistente o password sbagliata. Riprovare...")
        return False
    
    password_salvata = r.hget(username, "password")
    if password_salvata == hash_password(password):
        print("Benvenuto!")
        return True
    else:
        print("Nome utente inesistente o password sbagliata. Riprovare...")
        return False
    
def main():
    while True:
        scelta = input("Vuoi (r)egistrati oppure effettuare il (l)ogin? (q per uscire): ").lower()
        
        if scelta == "q":
            break
        username = input("Inserire l'username: ")
        password = getpass.getpass("Inserire la password: ")
        
        if scelta == "r":
            registrazione(username, password)
        elif scelta == "l":
            loggato = login(username, password)
            
            if loggato == True:
                main2(loggato)
        else:
            print("Scelta non valida! Riprovare...")

def main2(loggato):
    while True:
        scelta = input("""Benvenuto! Vuoi:
                       - (a)ggiungere un nuovo contatto?
                       - vuoi (c)hattare con un contatto?
                       - (t) per tornare. """).lower()
        
        if scelta == "t":
            loggato = False
            main(loggato) # aggiungere log out
        elif scelta == "a":
            nome_ricerca = input("Inserire l'username da trovare: ")
            risultati = ricerca_utenti(nome_ricerca)
            
            if risultati is True:
                pass
            
            
if __name__ == "__main__":
    main()

