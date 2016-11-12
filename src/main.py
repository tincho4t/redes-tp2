from Tracer import Tracer

# hostname = "sydney.edu.au"
#hostname = "www.google.com"
hostname = "www.u-tokyo.ac.jp"
# hostname = "www.indian-host.com"
# hostname = "www.bandainamco.co.jp"

t = Tracer(timeout=5)
#t.traceEachStepRoute(hostname, 36, 5)
t.traceEachRoute(hostname, 36, timesForTtl=100)
