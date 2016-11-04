import scapy

from scapy import route
from scapy.all import *
from statistics import cimbala_outliers
from Tracer import Tracer
import time

# hostname = "www.u-tokyo.ac.jp"
# hostname = "www.clarin.com" # Clarin no responde el trace pero si el sync
# hostname = "www.indian-host.com" # Clarin no responde el trace pero si el sync
hostname = "www.bandainamco.co.jp"

t = Tracer(timeout=1)
t.traceRoute(hostname)