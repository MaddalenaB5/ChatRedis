import redis

# Connetti al server Redis cloud del tuo collega con autenticazione
r = redis.Redis(host='redis-18934.c328.europe-west3-1.gce.redns.redis-cloud.com',
                port=18934,
                db=0,
                charset="utf-8",
                decode_responses=True,
                password='4GVWbKjMnaiMtHaX56tTNKODmzblmYtq')

print('Connesso')

# Aggiungi una chiave-valore
r.set('Luca', 3)

# Recupera il valore associato alla chiave
valore = r.get('Luca')
print(valore)





