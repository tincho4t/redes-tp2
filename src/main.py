from Tracer import Tracer
import argparse
from math import log
from sets import Set

############## Parse de argumentos #####################

parser = argparse.ArgumentParser(description='TP 2 de Redes')
parser.add_argument('--hostname', metavar='hostname', type=str, required=True, help='Host al que se le quiere rutear')
parser.add_argument('--maxTtl', metavar='maxTtl', type=int, default=36,help='Cantidad maxima de ttls que se van a intentar')
parser.add_argument('--traceAmount', metavar='traceAmount', type=int, default=100, help='Cantidad de veces que se va realizar el trace para luego promediar')
parser.add_argument('--timeout', metavar='timeout', type=int, default=5, help='Timeout por cada request. En segundos.')
args = parser.parse_args()

########################################################

# hostname = "sydney.edu.au"
#hostname = "www.google.com"
# hostname = "www.u-tokyo.ac.jp"
# hostname = "www.indian-host.com"
# hostname = "www.bandainamco.co.jp"

t = Tracer(timeout=args.timeout)
#t.traceEachStepRoute(hostname, 36, 5)
t.traceEachRoute(args.hostname, args.maxTtl, timesForTtl=args.traceAmount)
