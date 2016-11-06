from Tracer import Tracer

hostname = "www.u-tokyo.ac.jp"
# hostname = "www.clarin.com" # Clarin no responde el trace pero si el sync
# hostname = "www.indian-host.com" # Clarin no responde el trace pero si el sync
# hostname = "www.bandainamco.co.jp"

t = Tracer(timeout=2)
# t.traceEachStepRoute(hostname)
t.traceEachRoute(hostname, timesForTtl=100)