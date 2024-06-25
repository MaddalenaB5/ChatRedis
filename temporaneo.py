import redis
import hashlib
import getpass

#Connetti al server Redis cloud del tuo collega con autenticazione
r = redis.Redis(host='redis-18934.c328.europe-west3-1.gce.redns.redis-cloud.com',
                port=18934,
                db=0,
                charset="utf-8",
                decode_responses=True,
                password='4GVWbKjMnaiMtHaX56tTNKODmzblmYtq')

#Converte la password in un hash per motivi di sicurezza
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

#funzione registrazione
def registrazione(username, password):
    if r.hexists(f"utenti:{username}", username):
        print("Nome Utente già utilizzato. Sceglierne un'altro...")
        return False
    password_hash = hash_password(password)
    dati_utente = {
        "nome": username,
        "password": password_hash,
        "contatti": [],
        "dnd" : 0
        }
    
    r.hset(f"utenti:{username}", dati_utente)
    return True

#funzione di login
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

#funzione ricerca utenti *
def ricerca_utenti(user):
    nomi_presenti = r.hkeys("utenti")
    risultati = []
    for nome_utente in nomi_presenti:
        if user.lower() in nome_utente[0:len(user)+1].lower():
            risultati.append(nome_utente)
        
        return risultati
    
#primo menù
def main():
    while True:
        scelta = input("Vuoi (r)egistrati oppure effettuare il (l)ogin? (q) per uscire ").lower()
        
        if scelta == "q":
            break
        username = input("Inserire l'username: ")
        password = getpass.getpass("Inserire la password: ")
        
        if scelta == "r":
            registrazione(username, password)
        elif scelta == "l":
            loggato = login(username, password)
            if loggato == True:
                usernameloggato = username
                vadnd = r.hget("utenti", usernameloggato, "dnd")
                if vadnd == 1:
                    print("Do Not Disturb attivo")
                else:
                    print("Do Not Disturb disattivo")
                main2(usernameloggato, loggato)
                
        else:
            print("Scelta non valida! Riprovare...")

#secondo menù
def main2(usernameloggato, loggato):
    while True:
        scelta = input("""Benvenuto! Vuoi:
                       - (a)ggiungere un nuovo contatto?
                       - (c)hattare con un contatto?
                       - cambiare lo stato del (d)o not disturb?
                       - (t) per tornare. """).lower()
        
        if scelta == "t":
            loggato = False
            main(loggato) # aggiungere log out
        elif scelta == "a":
            nome_ricerca = input("Inserire l'username da trovare: ")
            risultati = ricerca_utenti(nome_ricerca)
        elif scelta == "d":
            valdnd = r.hget("utenti", usernameloggato, "dnd")
            if valdnd == 0:
                r.setbit("dnd", 0, 1)
                print("Do Not Disturb attivato")
            else:
                r.setbit("dnd", 0, 0)
                print("Do Not Disturb disattivato")


            
            if risultati is True:
                pass
            
#per entrare nel primo     
if __name__ == "__main__":
    main()



'''
import time
#funzione messaggi (in caso non esista chat)
def creazione_chat(username1, username2):
    nome_chat = str(username1)+ " - " + str(username2)
    inv_nome_chat = str(username2)+ " - " + str(username1)

    # controllo esistenza chat 
    if r.hexists(f"messaggi:{chat}", nome_chat) or r.hexists(f"messaggi:{chat}", inv_nome_chat):
        print("Nome Utente già utilizzato. Sceglierne un'altro...")
        return False

    # scrivere messaggio e salvare tempo
    messaggio = str(input("Scrivi il messaggio: "))
    t=time.time()

    # creazione chat
    dati_chat = {
        "nome": nome_chat,
        "num_mess": 0
        }
    
    r.hset(f"messaggi:{nome_chat}", dati_chat)
    r.zadd(f"messaggi: storico"), {messaggio: t}  # spero funzioni sono andato un po' a caso
    return True
'''