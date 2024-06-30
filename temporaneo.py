import redis
import hashlib
import getpass
import time

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
    r.rpush(f"utenti:{username}","contatti", "Contatti: ")
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
def ricerca_utenti(username_loggato, nome_ricerca):

  risultati = []
  #pattern = f"utenti:{nome_ricerca}*"

  # Scansione di tutti gli hash utente
  for key in r.scan(match="utenti:*", type="hash"):
    pattern = "utenti:" + nome_ricerca
    
    if key == f"utenti:{username_loggato}" or pattern not in key:
        continue
    
    else:
        risultati.append(r.hget(key, "nome"))

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

# Funzione per la visualizzazione della lista dei contatti
def vis_contatti(username):
    contatti = r.lrange(f"utenti:{username}:contatti", 0, -1)  #recupera i contatti dell'utente
    if contatti:
        for i, contatto in enumerate(contatti[1:], start = 1):
            print(f"{i + 1}. {contatto}")

# Prima parte del menù, gestisce registrazione, login e DnD
def main(loggato = False):
    while True:
        scelta = input("Vuoi (r)egistrati oppure effettuare il (l)ogin? (q) per uscire ").lower()
        
        match scelta:
            
            case "q":
                break
            
            case "r":
                username = input("Inserire l'username: ").lower()
                password = input("Inserire la password: ")
                registrazione2(username, password)
                
            case "l":
                username = input("Inserire l'username: ").lower()
                password = input("Inserire la password: ")
                loggato = login(username, password)
                
            case _:
                print("Scelta non valida! Riprovare...")
            
        if loggato == True:
            usernameloggato = username

            valdnd = r.getbit(f"utenti:{usernameloggato}:dnd",0)  # comando che estrae il bitmap DnD associato all'utente loggato
            if valdnd == 1:
                print("Do Not Disturb attivo")
            else:
                print("Do Not Disturb disattivo")

            main2(usernameloggato, loggato)

# Seconda parte del menù, gestisce tutte le altre azioni
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
                nome_ricerca = input(str("Inserire l'username da trovare: ")).lower()
                risultati = ricerca_utenti(nome_ricerca)
                if risultati:
                    aggiuntacont(risultati, usernameloggato )
                else:
                    print("Nessun utente trovato con questo nome.")
            
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
                user2 = vis_contatti(usernameloggato, True)
                chat(usernameloggato, user2)
            case _:
                print("Scelta non valida! Riprovare...")

#   FUNZIONE MESSAGGISTICA

#funzione messaggi
def chat(username1, username2):
    nome_chat = username1 + " - " + username2
    inv_nome_chat = username2 + " - " + username1

    mostrare_chat(nome_chat, username2)

    # scrittura messaggio e tempo
    valdnd = r.getbit(f"utenti:{username2}:dnd", 0)
    
    if valdnd == 1:
        print("L'utente non vuole essere disturbato.")
        
    else:
        print("L'utente può essere disturbato \n")
        
        messaggio = str(input("> "))
        t = time.time()
        # aggiungo messaggio al sorted set
        r.zadd(f"chat:{nome_chat}", {f"> {messaggio}": t})
        r.zadd(f"chat:{inv_nome_chat}", {f"< {messaggio}": t})
    


def mostrare_chat(nome_chat, username2):
    print(f">> Chat con {username2} <<\n")
    if r.exists(f"chat:{nome_chat}"):
        return print(r.zrange(f"chat:{nome_chat}", 0, -1, withscores=True))
    else:
        return print("Non fare l'asociale e manda il primo messaggio!\n")            

#per entrare nel primo     
if __name__ == "__main__":
    main()