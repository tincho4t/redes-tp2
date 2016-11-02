import scapy

from scapy import route
from scapy.all import *
from statistics import cimbala_outliers

import time

hostname = "www.gamespot.com"
# hostname = "www.clarin.com" # Clarin no responde el trace pero si el sync
nodes = {}
rtts = []

for i in range(25): # Vamos a probar hasta 35 saltos

  packet = IP(dst = hostname, ttl = i) / ICMP() # Creo un paquete de tipo ICMP 

  start_time = time.time()

  # Envio el paquete
  reply = sr1(packet, verbose = 0, timeout = 5) # Verbose = 0 es para que no escriba boludeces por pantalla

  rtts.append(time.time() - start_time) # Guardo el tiempo que tardo en enviarse el paquete y volver (rtt)

  if reply is None: # Si no hubo respuesta
    print "No hubo respuesta intentando sync"
    retry = sr1(IP(dst = hostname, ttl = i)/TCP(dport=80,flags="S"), verbose = 0, timeout = 1)
    if(retry is None):
      pass
    else: # Alguien respondio por lo cual se esta escuchando el puerto y hay alguien
      nodes[i] = retry.src
      print("Alcanzado con el syn! " + str(retry.src))
      # break

  elif reply.type == 0: # Chequeo si llegue al destino (Obtuve un Echo Reply)
    nodes[i] = reply.src
    print("Done! " + str(reply.src))
    # break

  elif reply.type == 11: # Estoy en un nodo intermedio
    nodes[i] = reply.src
    print("%d Estoy paseando por un nodo intermedio: " % i, reply.src)

  else: # Es un nodo desconocido
    print "%d Nodo desconocido" % i
    nodes[i] = '*'

# En nodes tengo la IP de cada nodo intermedio
sorted_keys = sorted(nodes.keys())
# Busca outliers
outliers = cimbala_outliers(rtts)
for key in sorted_keys:
  print(key, nodes[key])
for rtt in rtts:
  s = str(rtt)
  if (rtt in outliers):
    s + " | outlier"
  print(s)