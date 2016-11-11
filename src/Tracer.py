import scapy
import requests
import os
# pip install python-geoip-geolite2
from geoip import geolite2

from scapy import route
from scapy.all import *
from statistics import cimbala_outliers
from statistics import cimbala_outliers_removing_samples_in_iterations
import numpy as np

        

class Tracer(object):

    def __init__(self, timeout = 5):
        super(Tracer, self).__init__()
        self.timeout = timeout

    # Por cada TTL hace K request para ver el camino mas probable
    def traceEachStepRoute(self, hostname, ttlMax = 36, timesForTtl=1000):

        route = []

        for ttl in range(1,ttlMax): # Vamos a probar hasta 35 saltos
            probableNodes = []
            rrtNodes = [] 
            intermediateNodes = []
            for i in range(timesForTtl):
                rrt, src, intermediate_node = self.trace(hostname, ttl)
                print("i: ", i)
                if(src):
                    print("rtt is -> ", rrt)
                    print("ttl: %d , i: %d", ttl, i)
                    probableNodes.append(src)
                    rrtNodes.append(rrt)
                    intermediateNodes.append(intermediate_node)
            node = self.getProbableNode(probableNodes, rrtNodes, intermediateNodes, ttl)
            if(node):
                route.append(node)
                if(node['intermediate_node'] == False):
                    break # No sigo porque ya llegue al destino.

        # Busca outliers
        self.addRoundTripTimeDifference(route)
        self.printCheckingOutliers(route)

    # Construye un camino de 1 a ttlMax y lo realiza K veces para buscar el camino mas probable
    def traceEachRoute(self, hostname, ttlMax = 36, timesForTtl=5):

        probableNodes = {}
        for ttl in range(ttlMax):
            probableNodes[ttl] = list()
        # Busco los nodos
        for i in range(timesForTtl):
            for ttl in range(1,ttlMax):
                node = self.traceNode(hostname, ttl)
                if(node):
                    probableNodes[ttl].append(node)
                    if(node['intermediate_node'] == False):
                        break # Si llegue al destino termino
        # Calculo la ruta mas probable
        route = []
        for ttl in range(ttlMax):
            routeNode = self.getProbableRouteNode(probableNodes[ttl], ttl)
            if(routeNode):
                route.append(routeNode)
                if(routeNode['intermediate_node'] == False):
                    break # No sigo porque ya llegue al destino.

        # Busca outliers
        print ("route: " , route)
        self.addRoundTripTimeDifference(route)
        outliers, pruned_outliers = self.printCheckingOutliers(route)

        directory = hostname + '/'

        if not os.path.exists(directory):
            os.mkdir(directory)

        with open(directory + 'ips', 'w') as file_write:
            for node in route:
                file_write.write(str(node['ip']) + '\n')
                
        with open(directory + 'rtt', 'w') as file_write:
            for node in route:
                file_write.write(str(node['rtt']) + '\n')

        with open(directory + 'ttl', 'w') as file_write:
            for node in route:
                file_write.write(str(node['ttl']) + '\n')

        with open(directory + 'count', 'w') as file_write:
            for node in route:
                file_write.write(str(node['count']) + '\n')

        with open(directory + 'rtt_dif', 'w') as file_write:
            for node in route:
                file_write.write(str(node['rtt_dif']) + '\n')

        with open(directory + 'rtt_dif', 'w') as file_write:
            for node in route:
                file_write.write(str(node['rtt_dif']) + '\n')

        with open(directory + 'outliers', 'w') as file_write:
            for outlier in outliers:
                for node in route:
                    if node['rtt_dif'] == outlier:
                        file_write.write(str(outlier) + ', ' + str(node['ip']) + '\n')

        with open(directory + 'pruned_outliers', 'w') as file_write:
            for outlier in pruned_outliers:
                for node in route:
                    if node['rtt_dif'] == outlier:
                        file_write.write(str(outlier) + ', ' + str(node['ip']) + '\n')

        with open(directory + 'country_continent', 'w') as file_write:
            for node in route:
                print (str(node['ip']))
                location = geolite2.lookup(str(node['ip']))
                if location is not None:
                    file_write.write(location.country + ', ' + location.continent + ', ' + str(node['ip']) + '\n')

    # Printea usando las dos estrategias de busqueda de ouliers
    def printCheckingOutliers(self, route):
        pruned_outliers = cimbala_outliers_removing_samples_in_iterations(route)
        outliers = cimbala_outliers(route)

        print("--------- Simple Cimbala Outliers Check ---------")
        for node in route:
            if(node['rtt_dif'] in outliers):
                # print "%d Is outlier" % node['ttl']
                print(node, " is Outlier")
            else:
                print(node)
        print("outliers", outliers)
        print("-------------------------------------------------")

        print("--------- Pruned Cimbala Outliers Check ---------")
        for node in route:
            if(node['rtt_dif'] in pruned_outliers):
                # print "%d Is outlier" % node['ttl']
                print(node, " is Outlier")
            else:
                print(node)
        print("outliers", pruned_outliers)
        print("-------------------------------------------------")

        return outliers, pruned_outliers


    # Agrego a los paquetes el rout trip time diference
    def addRoundTripTimeDifference(self, route):
        route[0]['rtt_dif'] = route[0]['rtt']
        for i in range(1,len(route)):
            difference = np.absolute(route[i]['rtt'] - route[i-1]['rtt'])
            route[i]['rtt_dif'] = difference

    def getProbableRouteNode(self, probableNodes, ttl):
        node = None
        if(len(probableNodes) > 0):
            ip = self.probableSource(probableNodes)
            node = {'ip':ip, 'ttl': ttl}
            count = 0
            rtt = 0
            intermediate_node = None            
            for n in probableNodes:
                if(n['ip'] == ip):
                    count += 1
                    rtt += n['rtt']
                    intermediate_node = n['intermediate_node']
            node['count'] = count
            node['rtt'] = rtt / count
            node['intermediate_node'] = intermediate_node
        return node

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

    def traceNode(self, hostname, ttl):
        node = None
        rtt, src, intermediate_node = self.trace(hostname, ttl)
        if(src):
            node = {'ip':src, 'rtt': rtt, 'intermediate_node': intermediate_node, 'ttl': ttl}
        return node

    def trace(self, hostname, ttl):
        intermediate_node = True
        src = None
        rtt, reply = self.sendTrace(hostname,ttl)
        if rtt < 0:
            rtt = 0

        if reply is None: # Si no hubo respuesta
            print("No hubo respuesta intentando sync...")
            rtt, retry = self.sendSync(hostname, ttl)
            if(self.syncWasSuccess(retry)): # Alguien respondio por lo cual se esta escuchando el puerto y hay alguien
                src = retry.src
                print("Alcanzado con el syn! " + str(src))
                intermediate_node = False
        elif reply.type == 0: # Chequeo si llegue al destino (Obtuve un Echo Reply)
            src = reply.src
            print("Done! " + str(src))
            intermediate_node = False
        elif reply.type == 11: # Estoy en un nodo intermedio
            src = reply.src
            print("%d Estoy paseando por un nodo intermedio: " % ttl, src)
        else: # Es un nodo desconocido
            print("%d Nodo desconocido" % ttl)
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

    def probableSource(self, nodes):
        ips = []
        for node in nodes:
            ips.append(node['ip'])
        return self.most_common(ips)

