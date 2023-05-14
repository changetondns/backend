import dns.message
import threading
import socket
import select


class DNSLeaks:
    def __init__(self, ipv4: str, ipv6: str, port: int):
        self.port = port
        self.ipv4 = ipv4
        self.ipv6 = ipv6

        self.users = {}

    def _delete_user(self, identifier):
        """Supprime l'utilisateur du dictionnaire users.

        Args:
            identifier (int): L'tilisateurs ayant fait la demande d'identification de DNS.
        """
        
        if identifier in self.users:
            del self.users[identifier]

    def get_dns_from_ip(self, identifier):
        """Renvoie l'ip du DNS utilisé par l'utilisateur.

        Args:
            identifier (int): L'tilisateurs ayant fait la demande d'identification de DNS.

        Returns:
            str: IP du DNS de l'utilisateur.
        """
        if identifier in self.users:
            return self.users[identifier]

        return None

    def _handle_dns_query(self, raw_query):
        """Traite la demande du FAI.

        Args:
            raw_query (bytes): La requete envoyé par le FAI.

        Raises:
            NotImplementedError: Type de DNS non supporte.

        Returns:
            tuples: Reponse au FAI.
        """
        query = dns.message.from_wire(raw_query)
   
        question = str(query.question[0])
        name, rtype = [r.strip() for r in question.split('IN')]

        if rtype == 'A':
            ip_resp = self.ipv4
        elif rtype == 'AAAA':
            ip_resp = self.ipv6
        else:
            return

        response = dns.message.make_response(query)
        rrset = dns.rrset.from_text(name, 10, 1, rtype, ip_resp)
        response.answer.append(rrset)
        wire_resp = response.to_wire()

        return name, wire_resp

    def start(self):
        """Lance le serveur."""
        sock6 = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM) # initialise les connections UDP et non TCP.
        sock4 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      
        sock6.bind((self.ipv6, self.port)) 
        sock4.bind((self.ipv4, self.port)) # Permet de rendre le socket accesible via cette ip.

        rsocks = [sock6, sock4]

        while True:
            rlist, _, _ = select.select(rsocks, [], []) # Attend que les sockets de lecture reçoive un event.
      
            for conn in rlist:
                dgram, addr = conn.recvfrom(4096)

                try:
                    name, wire_resp = self._handle_dns_query(dgram)
                except NotImplementedError:
                    continue 

                try:
                    identifier = int(name.split('.')[0])
                    ip_addr, *_ = addr
             
                    self.users[identifier] = ip_addr
                    
                    t = threading.Timer(300, self._delete_user, args=[identifier])
                    t.start()

                except ValueError as e:
                    pass

                conn.sendto(wire_resp, addr)

if __name__ == '__main__':
    server = DNSLeak('127.0.0.1', '::1', 53)
    server.start()