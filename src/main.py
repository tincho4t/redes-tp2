import scapy
from scapy.all import *
import time

hostname = "www.google.com"
nodes = {}
rtts = []

for i in range(50): # Vamos a probar hasta 35 saltos

  packet = IP(dst = hostname, ttl = i) / ICMP() # Creo un paquete de tipo ICMP 

  start_time = time.time()

  # Envio el paquete
  reply = sr1(packet, verbose = 0, timeout = 5) # Verbose = 0 es para que no escriba boludeces por pantalla

  rtts.append(time.time() - start_time) # Guardo el tiempo que tardo en enviarse el paquete y volver (rtt)

  if reply is None: # Si no hubo respuesta
    pass

  elif reply.type == 0: # Chequeo si llegue al destino (Obtuve un Echo Reply)
    nodes[i] = reply.src
    print("Done! " + str(reply.src))
    break

  elif reply.type == 11: # Estoy en un nodo intermedio
    nodes[i] = reply.src
    print("%d Estoy paseando por un nodo intermedio: " % i, reply.src)

  else: # Es un nodo desconocido
    nodes[i] = '*'

# En nodes tengo la IP de cada nodo intermedio
sorted_keys = sorted(nodes.keys())
for key in sorted_keys:
  print(key, nodes[key])
for rtt in rtts:
  print(rtt)
