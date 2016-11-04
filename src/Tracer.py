import scapy

from scapy import route
from scapy.all import *
from statistics import cimbala_outliers
from statistics import cimbala_outliers_removing_smples_in_iterations
import numpy as np

        

class Tracer(object):

    def __init__(self, timeout = 5):
        super(Tracer, self).__init__()
        self.timeout = timeout

    def traceRoute(self, hostname, ttlMax = 36, timesForTtl=5):

        route = []

        for ttl in range(1,ttlMax): # Vamos a probar hasta 35 saltos
            probableNodes = []
            rrtNodes = [] 
            intermediateNodes = []
            for i in range(timesForTtl):
                rrt, src, intermediate_node = self.trace(hostname, ttl)
                print "rtt is -> ", rrt
                if(src):
                    probableNodes.append(src)
                    rrtNodes.append(rrt)
                    intermediateNodes.append(intermediate_node)
            node = self.getProbableNode(probableNodes, rrtNodes, intermediateNodes, ttl)
            if(node):
                route.append(node)
                if(node['intermediate_node']):
                    break # No sigo porque ya llegue al destino.

        # Busca outliers
        self.addRoundTripTimeDifference(route)
        self.printCheckingOutliers(route)

    # Printea usando las dos estrategias de busqueda de ouliers
    def printCheckingOutliers(self, route):
        pruned_outliers = cimbala_outliers_removing_smples_in_iterations(route)
        outliers = cimbala_outliers(route)

        print "--------- Simple Cimbala Outliers Check ---------"
        for node in route:
            if(node['rtt_dif'] in outliers):
                # print "%d Is outlier" % node['ttl']
                print node, " is Outlier"
            else:
                print node
        print "outliers", outliers
        print "-------------------------------------------------"

        print "--------- Pruned Cimbala Outliers Check ---------"
        for node in route:
            if(node['rtt_dif'] in pruned_outliers):
                # print "%d Is outlier" % node['ttl']
                print node, " is Outlier"
            else:
                print node
        print "outliers", pruned_outliers
        print "-------------------------------------------------"



    # Agrego a los paquetes el rout trip time diference
    def addRoundTripTimeDifference(self, route):
        route[0]['rtt_dif'] = route[0]['rtt']
        for i in range(1,len(route)):
            difference = np.absolute(route[i]['rtt'] - route[i-1]['rtt'])
            route[i]['rtt_dif'] = difference

    def getProbableNode(self, probableNodes,rrtNodes, intermediateNodes, ttl):
        node = None
        intermediate_node = None
        if(len(probableNodes)> 0):
            node = {'ttl': ttl}
            ip = self.most_common(probableNodes)
            probableRtt = []
            for i in range(len(probableNodes)):
                if(probableNodes[i] == ip): # Si el rrt fue del nodo probable lo agrego
                    probableRtt.append(rrtNodes[i])
                    intermediate_node = intermediateNodes[i]
            node['ip'] = ip
            node['rtt'] = np.average(probableRtt)
            node['count'] = len(probableRtt) # A modo debug para valir que la cantidad con la que nos estamos quedando tenga sentido
            node['intermediate_node'] = intermediate_node
        return node

    def sendTrace(self, hostname, ttl):
        packet = IP(dst = hostname, ttl = ttl) / ICMP() # Creo un paquete de tipo ICMP 
        return self.sendPacket(packet)

    def sendSync(self, hostname, ttl):
        packet = IP(dst = hostname, ttl = ttl)/TCP(dport=80,flags="S") # Creo un paquete de sync TCP
        return self.sendPacket(packet)

    def sendPacket(self, packet):
        start_time = time.time()
        # Envio el paquete
        reply = sr1(packet, verbose = 0, timeout = self.timeout) # Verbose = 0 es para que no escriba boludeces por pantalla
        rtt = time.time() - start_time # Guardo el tiempo que tardo en enviarse el paquete y volver (rtt)
        return rtt, reply

    def trace(self, hostname, ttl):
        intermediate_node = False
        src = None
        rtt, reply = self.sendTrace(hostname,ttl)
        if reply is None: # Si no hubo respuesta
            print "No hubo respuesta intentando sync..."
            rtt, retry = self.sendSync(hostname, ttl)
            if(self.syncWasSuccess(retry)): # Alguien respondio por lo cual se esta escuchando el puerto y hay alguien
                src = retry.src
                print("Alcanzado con el syn! " + str(src))
                intermediate_node = True
        elif reply.type == 0: # Chequeo si llegue al destino (Obtuve un Echo Reply)
            src = reply.src
            print("Done! " + str(src))
            intermediate_node = True
        elif reply.type == 11: # Estoy en un nodo intermedio
            src = reply.src
            print("%d Estoy paseando por un nodo intermedio: " % ttl, src)
        else: # Es un nodo desconocido
            print "%d Nodo desconocido" % ttl
            # nodes[i] = '*'
        return rtt, src, intermediate_node

    def syncWasSuccess(self, retry):
        success = False
        if(not retry or ICMP in retry):
            success = False
        else:
            success = True
        return success

    def most_common(self, lst):
            return max(set(lst), key=lst.count)
