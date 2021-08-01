import socket
import ipv6


host = "::1"
port = 3300
data = b"NASA"
resolve = socket.getaddrinfo(host, port, socket.AF_INET6, socket.SOCK_DGRAM)
(family, socktype, proto, _, sockaddr) = resolve[0]
sock = None #socket.socket(family, socktype, proto)
sockaddr = ipv6.get_flow_label(sock,*sockaddr)
print("Flow Label:",hex(sockaddr[2]))
sock.sendto(data,sockaddr)