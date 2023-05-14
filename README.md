# Backend
Répertoire officiel du backend de changetondns.fr.

# Lancement
1) Lancement de l'api :
`sudo gunicorn -k uvicorn.workers.UvicornWorker api:app --reload`

# Test du leaks DNS.
`[En Admin] python3.11 dns.py`
```py
import socket
import dns.message


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
query = dns.message.make_query('12234254.google.com', 'A')
data = query.to_wire()

dest_addr = ("127.0.0.1", 53)
sock.sendto(data, dest_addr)

response, _ = sock.recvfrom(4096)
response_message = dns.message.from_wire(response)

print(response_message)
```