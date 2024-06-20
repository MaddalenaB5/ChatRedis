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

    # Controllo se il nome utente esiste già
    if r.get(nome) == None:
        password = input("Inserisci la password che vuoi usare: ")
        r.hset(nome, "passw", password, "DnD", 0)
        print("Registrazione completata con successo.")
#login
def login():
    nome = input('Inserisci il tuo nome utente')
    password = input('Inserisci la password')

    pass_salvate = r.hget('nome', nome)

    if pass_salvate is None:
        print("Nome utente non trovato. Registrazione necessaria.")
    else:
        pass_salvate = pass_salvate.decode('utf-8')
        if pass_salvate == password:
            print("Login riuscito!")
        else:
            print("Password errata.")

#menù
scelta = int(input("cosa vuoi fare? "))
print("1. registrati")
print("2. accedi")

if scelta == 1:
    registrazione()
else:
    login()