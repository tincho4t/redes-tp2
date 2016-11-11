import statistics
from statistics import cimbala_outliers_removing_samples_in_iterations
from statistics import cimbala_outliers

directory = "sydney_data/"
route = []
first = True
with open(directory + 'sydney.edu.au_rtt_dif', 'r') as file_rtts:
  with open(directory + 'sydney.edu.au_ips', 'r') as file_ips:

    for rtt, ip in zip(file_rtts, file_ips):

      if first:
        first = False
        pass

      else: 

        node = {'rtt_dif': float(rtt[:-1]), 'ip': ip[:-1]}
        route.append(node)
    
    print (route)
    pruned_outliers = cimbala_outliers_removing_samples_in_iterations(route)
    outliers = cimbala_outliers(route)
    print (outliers)
    print (pruned_outliers)

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
