import redis

# Connetti al server Redis cloud del tuo collega con autenticazione
r = redis.Redis(host='redis-18934.c328.europe-west3-1.gce.redns.redis-cloud.com',
                port=18934,
                db=0,
                charset="utf-8",
                decode_responses=True,
                password='4GVWbKjMnaiMtHaX56tTNKODmzblmYtq')
print('Connesso')

# Funzione di registrazione
def registrazione():
    nome = input("Inserisci il nome utente che vuoi usare: ")
    password = input("Inserisci la password che vuoi usare: ")

    # Controllo se il nome utente esiste già
    utente_esistente = False
    for key in r.scan_iter("nome:*"):
        stored_nome = key.split(":")[1]  # Estrarre il nome utente dalla chiave
        if nome == stored_nome:
            utente_esistente = True
            break

    if utente_esistente:
        print("Nome utente già presente. Riprova.")
    else:
        # Memorizza il nuovo utente
        r.hset(nome, "passw", password)
        print("Registrazione completata con successo.")

#funzione accedi
def accedi():
    pass

#menù
scelta = input(int("cosa vuoi fare?"))
print("1. registrati")
print("2. accedi")

if scelta == 1:
    registrazione()
else:
    accedi()



    







