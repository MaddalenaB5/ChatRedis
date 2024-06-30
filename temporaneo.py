import redis as red
import hashlib
import datetime

# Connetti al server Redis cloud del tuo collega con autenticazione
r = red.Redis(host='redis-18934.c328.europe-west3-1.gce.redns.redis-cloud.com',
                port=18934,
                db=0,
                charset="utf-8",
                decode_responses=True,
                password='4GVWbKjMnaiMtHaX56tTNKODmzblmYtq')

#Converte la password in un hash per motivi di sicurezza
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# Funzione che gestisce la registrazione dell'utente
def registrazione(username, password):
    if r.hexists(f"utenti:{username}", "nome"):
        print("\n<<< Nome Utente già utilizzato. Sceglierne un altro...")
        return False
    
    password_hash = hash_password(password)
    
    # Creazione hash con nome utente e password, lista dei contatti inizializzata con un solo elemento, bitmap per il DnD
    r.hset(f"utenti:{username}","nome",username)
    r.hset(f"utenti:{username}","password",password_hash) 
    r.lpush(f"utenti:{username}:contatti", "trovati:")
    r.setbit(f"utenti:{username}:dnd", 0,0)

    return True


# Funzione per il login dell'utente
def login(username, password):
    if not r.hexists(f"utenti:{username}", "nome"): #controlla l'esistenza dell'hash associato all'utente
        print("\n<<< Nome utente inesistente o password sbagliata. Riprovare...")
        return False
    
    password_salvata = r.hget(f"utenti:{username}", "password") #get della password contenuta nell'hash associato all'utente
    if password_salvata == hash_password(password):
        return True
    else:
        print("\n<<< Nome utente inesistente o password sbagliata. Riprovare...")
        return False


# funzione ricerca utenti
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


# Funzione per aggiungere nuovi contatti
def aggiungi_contatti(username, ris):
    
    if ris:
        
        for i, contatto in enumerate(ris, start = 1):
                print(f"{i}. {contatto}")
    
        utentedaagg = int(input("Inserisci il numero corrispondente al contatto che vuoi aggiungere: "))
        contatti = r.lrange(f"utenti:{username}:contatti", 0, -1)  #restituisce una lista di redis associata alla chiave contatti
        contatto_selezionato = ris[utentedaagg - 1]
        if contatto_selezionato in contatti:
            print('Contatto già presente')
        else:
            contatti.append(contatto_selezionato)
            r.rpush(f"utenti:{username}:contatti", contatto_selezionato) #comando che aggiunge l'elemento nella lista
            print("i tuoi contatti sono: \n", contatti)
           #sistemare senza inserimento parziale già fatto sopra
           # mettere la condizione per il quale il contatto non sia già presente nella lista contatti
    
    else:
        print("La ricerca non è andata a buon fine, impossibile aggiungere contatti.")



# Funzione per la visualizzazione della lista dei contatti
def vis_contatti(username, chattare = False, storico = False):
    contatti = r.lrange(f"utenti:{username}:contatti", 0, -1)  #recupera i contatti dell'utente
    if contatti[1:]:
        for i, contatto in enumerate(contatti[1:], start = 1):
            print(f"{i + 1}. {contatto}")
    
        if chattare or storico:
            prova = int(input("Digita il numero del contatto con cui vuoi chattare: "))
            user2 = contatti[prova - 1]
            return user2
            
    else:
        print("\n<<< Hai la lista contatti vuota.")


# Prima parte del menù, gestisce registrazione, login e DnD
def main(loggato = False):
    while True:
        print("""
 __________________________________________
|         Benvenuto in ChatRedis!          |
|                                          |
|          - Registrazione: (r)            |
|          - Login: (l)                    |
|          - Uscire: (q)                   |
|__________________________________________|
        """)

        scelta = input("\nInserisci la tua scelta (r, l, q): ").lower()
        
        match scelta:
            
            case "q":
                print("\nArrivederci!")
                break
            
            case "r":
                flag = str(input("\nSei sicuro che vuoi registrarti? [y/n]  ")).lower()
                if flag == "y":
                    while True:
                        print("""\n\n
---------- Fase di Registrazione ----------
                              """)
                        username = input("\n> Inserire l'username: ").lower()
                        password = input("> Inserire la password: ")
    
                        if registrazione(username, password):
                            print(""""
<<< Registrazione avvenuta con successo!

---------- Fine Registrazione ----------""")
                            loggato = login(username, password)
                            break
                        else:
                            print("""
 __________________________________                                        
| - Se vuoi uscire scrivi t        |
|                                  |
| - Se vuoi riprovare premi INVIO: |
|__________________________________|""")

                            flag = input("\n> ")
                            
                            if flag == "t":
                                print(""""
<<< Registrazione fallita.

---------- Fine Registrazione ----------""")
                                break
                
            case "l":
                while True:
                    print("""\n\n
---------- Fase di Login ----------
                                  """)
                    
                    username = input("\n> Inserire l'username: ").lower()
                    password = input("> Inserire la password: ")
                    loggato = login(username, password)
                    
                    if not loggato:
                        print("""
 __________________________________                                        
| - Se vuoi uscire scrivi t        |
|                                  |
| - Se vuoi riprovare premi INVIO: |
|__________________________________|""")

                        flag = input("\n> ")
                            
                        if flag == "t":
                            print(""""
<<< Login fallito.

---------- Fine Login ----------
""")
                            break
                    else:
                        print("""
<<< Login effettuato!!

---------- Fine Login ----------
""")
                        break
                    

            case _:
                print("\nScelta non valida! Riprovare...")
            
        if loggato == True:
            print("""\n\n          
---------- Info di Sistema ----------
                  """)
            usernameloggato = username

            valdnd = r.getbit(f"utenti:{usernameloggato}:dnd",0)  # comando che estrae il bitmap DnD associato all'utente loggato
            if valdnd == 1:
                print("\n<<< Hai il Do Not Disturb attivo")
            else:
                print("\n<<< Hai il Do Not Disturb disattivo")
            
            if not r.lrange(f"utenti:{username}:contatti", 0, -1)[1:]:
                
                print("\n<<< Hai una lista contatti vuota.")
            print("""
                  
-------------------------------------
                  """)
            main2(usernameloggato, loggato)

# Seconda parte del menù, gestisce tutte le altre azioni
def main2(usernameloggato, loggato):
    while True:
        print(f"""
                     
    Benvenuta/o {usernameloggato.title()}!!       
 ______________________________________________
|Vuoi:                                         |
|   - (a)ggiungere un nuovo contatto?          |
|   - (v)isualizzare lista contatti?           |
|   - (c)hattare con un contatto?              |
|   - Vedere lo (s)torico della chat?          |
|   - cambiare lo stato del (d)o not disturb?  |
|   - (t) per tornare.                         |
|______________________________________________|""")

        scelta = input("\nInserisci la tua scelta (a, v, c, s, d, t): ").lower()
        
        match scelta:
            
            case "t":
                loggato = False
                break
              
            case "a":
                nome_ricerca = str(input("Inserire l'username da trovare: ")).lower()
                risultati = ricerca_utenti(nome_ricerca)
                aggiungi_contatti(usernameloggato, risultati)
            
            case "v":
                vis_contatti(usernameloggato)
                
            case "d":
                valdnd = r.getbit(f"utenti:{usernameloggato}:dnd",0) # estrazione del bitmap DnD associato all'utente loggato
                if valdnd == 0:
                    r.setbit(f"utenti:{usernameloggato}:dnd",0, 1) # modifica del valore in "attivo"
                    print("Do Not Disturb attivato")
                else:
                    r.setbit(f"utenti:{usernameloggato}:dnd",0, 0) # modifica del valore in "disattivato"
                    print("Do Not Disturb disattivato")
            case "c":
                user2 = vis_contatti(usernameloggato, True, False)
                chat(usernameloggato, user2)
            
            case "s":
                user2 = vis_contatti(usernameloggato, False, True)
                nome_chat = usernameloggato + " - " + user2
                inv_nome_chat = user2 + " - " + usernameloggato
                
                mostrare_chat(nome_chat, inv_nome_chat, user2)
                
            case _:
                print("Scelta non valida! Riprovare...")

#   FUNZIONE MESSAGGISTICA

#funzione messaggi
def chat(username1, username2):
    nome_chat = username1 + " - " + username2
    inv_nome_chat = username2 + " - " + username1

    mostrare_chat(nome_chat, inv_nome_chat, username2) # modificato

    # scrittura messaggio e tempo
    valdnd = r.getbit(f"utenti:{username2}:dnd", 0)
    
    if valdnd == 1:
        print("L'utente non vuole essere disturbato.")
        
    else:
        print("L'utente può essere disturbato \n")
        scelta = str(input("messaggio effimero [y/n]: ")).lower()
        messaggio = str(input("> "))
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        score = now.timestamp()

        if scelta == "y":
            # Imposta la scadenza per i singoli messaggi dopo 60 secondi
            r.zadd(f"chat_ttl:{nome_chat}", {f"> {messaggio} ({timestamp})": score})
            r.zadd(f"chat_ttl:{inv_nome_chat}", {f"< {messaggio} ({timestamp})": score})
            r.expire(f"chat_ttl:{nome_chat}", 60)
            r.expire(f"chat_ttl:{inv_nome_chat}", 60)
        else:
            # aggiungo messaggio al sorted set
            r.zadd(f"chat:{nome_chat}", {f"> {messaggio} ({timestamp})": score})
            r.zadd(f"chat:{inv_nome_chat}", {f"< {messaggio} ({timestamp})": score})
    

def mostrare_chat(nome_chat, inv_nome_chat, username2):
    print(f">> Chat con {username2} <<\n")
    r.zunionstore(f"chat_mista:{nome_chat}", [f"chat_ttl:{nome_chat}", f"chat:{nome_chat}"])
    r.zunionstore(f"chat_mista:{inv_nome_chat}", [f"chat_ttl:{inv_nome_chat}", f"chat:{inv_nome_chat}"]) # modificato
    
    if r.exists(f"chat_mista:{nome_chat}"):
        for el in r.zrange(f"chat_mista:{nome_chat}", 0, -1, withscores=False):
            print(el)
    else:
        return print("Non fare l'asociale e manda il primo messaggio!\n")             

#per entrare nel primo     
if __name__ == "__main__":
    main()
    
"""
GRAFICO:
2: Sistemare la parte grafica

OPZIONALI
2: notifiche PUBSUB
"""