from fastapi import FastAPI
from dnsleaks import DNSLeak

import threading


app = FastAPI()
serveur_dns = DNSLeak('127.0.0.1', '::1', 53)

@app.get("/mydns")
async def dns(id: int = 0):
    dns_ip = serveur_dns.get_dns__from_ip(id)
    
    if dns_ip is None:
        return {'status': ''}

    return {"message": "Hello World"}

t = threading.Thread(target=serveur_dns.start)
t.start()
