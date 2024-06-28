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

#   FUNZIONE REGISTRAZIONE
def registrazione2(username, password):
    if r.hexists(f"utenti:{username}", "nome"):
        print("Nome Utente già utilizzato. Sceglierne un'altro...")
        return False
    
    password_hash = hash_password(password)
    
    r.hset(f"utenti:{username}","nome",username)
    r.hset(f"utenti:{username}","password",password_hash)
    r.rpush(f"utenti:{username}","contatti",)
    r.setbit(f"utenti:{username}","dnd",0,0)
    
    return True

#   FUNZIONE LOGIN
def login(username, password):
    if not r.hexists(f"utenti:{username}", "nome"):
        print("Nome utente inesistente o password sbagliata. Riprovare...")
        return False
    
    password_salvata = r.hget(f"utenti:{username}", "password")
    if password_salvata == hash_password(password):
        return True
    else:
        print("Nome utente inesistente o password sbagliata. Riprovare...")
        return False

#   FUNZIONE RICERCA UTENTE
def ricerca_utenti(nome):
    cursor = 0
    risultati = []
    while True:
        cursor, keys = r.scan(cursor=cursor, match=f'utenti:{nome}*')
        for key in keys:
            if r.type(key) == 'hash':
                value = r.hget(key, "nome")
                if value is not None and nome in value:
                    risultati.append(value)
        if cursor == 0:
            break
    return risultati

#   FUNZIONE AGGIUNTA CONTATTI
def aggiuntacont(risultati, username):
    if not risultati:
        print("Nessun utente trovato.")
        return
    
    # Visualizza i risultati trovati
    print("Utenti trovati:")
    for idx, user in enumerate(risultati, start=1):
        print(f"{idx}. {user}")
    
    try:
        # Permette all'utente di scegliere un utente dai risultati
        scelta = int(input("Quale scegli? Inserisci il numero corrispondente: ")) - 1
        
        if scelta < 0 or scelta >= len(risultati):
            print("Scelta non valida.")
            return
        
        utentedaagg = risultati[scelta]
        
        # Verifica se l'utente scelto è già nei contatti
        contatti = r.lrange(f"utenti:{username}:contatti", 0, -1)
        
        if utentedaagg not in contatti:
            r.rpush(f"utenti:{username}:contatti", utentedaagg)
            print(f"{utentedaagg} è stato aggiunto ai tuoi contatti.")
            print("I tuoi contatti sono: \n", r.lrange(f"utenti:{username}:contatti", 0, -1))
        else:
            print("Utente già presente nei contatti.")
    except ValueError:
        print("Scelta non valida. Inserisci un numero.")

#   FUNZIONE PRIMO MENU
def main():
    while True:
        scelta = input("Vuoi (r)egistrati oppure effettuare il (l)ogin? (q) per uscire ").lower()
        
        match scelta:
            case "q":
                break
            case "r":
                username = input("Inserire l'username: ")
                password = input("Inserire la password: ")
                registrazione2(username, password)
            case "l":
                username = input("Inserire l'username: ")
                password = input("Inserire la password: ")
                loggato = login(username, password)
            case _:
                print("Scelta non valida! Riprovare...")
            
        if loggato == True:
            usernameloggato = username
            main2(usernameloggato, loggato)
            """
            valdnd = r.hget("utenti", usernameloggato, "dnd")
            if valdnd == 1:
                print("Do Not Disturb attivo")
            else:
                print("Do Not Disturb disattivo")
"""

#   FUNZIONE SECONDO MENU
def main2(usernameloggato, loggato):
    while True:
        scelta = input("""Benvenuto! Vuoi:
                       - (a)ggiungere un nuovo contatto?
                       - (v)isualizzare lista contatti?
                       - (c)hattare con un contatto?
                       - cambiare lo stato del (d)o not disturb?
                       - (t) per tornare. """).lower()
        
        match scelta:
            
            case "t":
                loggato = False
                break
              
            case "a":
                nome_ricerca = input(str("Inserire l'username da trovare: "))
                risultati = ricerca_utenti(nome_ricerca)
                if risultati:
                    aggiuntacont(risultati, usernameloggato )
                else:
                    print("Nessun utente trovato con questo nome.")
            
            case "v":
                pass

            case "d":
                valdnd = r.getbit(f"utenti:{usernameloggato}:dnd",0)
                if valdnd == 0:
                    r.setbit(f"utenti:{usernameloggato}:dnd",0, 1)
                    print("Do Not Disturb attivato")
                else:
                    r.setbit(f"utenti:{usernameloggato}:dnd",0, 0)
                    print("Do Not Disturb disattivato")

#   ENTRATA PRIMO MENU     
if __name__ == "__main__":
    main()

#   FUNZIONE MESSAGGISTICA
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