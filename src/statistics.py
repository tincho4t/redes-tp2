import scipy, numpy

from scipy import stats
from numpy import mean
from numpy import std

def getRttDifferences(route):
	samples = []
	# for node in route:
	for i in range(1, len(route) - 1):
		samples.append(route[i]['rtt_dif'])
	return samples

def cimbala_outliers_removing_samples_in_iterations(route):
	outliers = []

	if (len(route) > 0):
		still_outliers = True
		samples = getRttDifferences(route)
                print (samples)

		#no hay do-while en python?
		while (still_outliers):
			still_outliers = False
			
			#calcular la media
			mean = numpy.mean(samples)
			
			#calcular el desvio standard
			std_deviation = numpy.std(samples)
			
			#calcula el chirimbolo "r"
			thompson_gamma = calculate_thompson_gamma(samples)
			outlier = None
			#busca outliers
                        print ("umbral: ", thompson_gamma * std_deviation)
			for sample in samples:
				delta = numpy.absolute(sample - mean)
                                print ("delta: ", delta)
				if (delta > thompson_gamma * std_deviation):
					outlier = sample
					break
			if(outlier):
				samples.remove(sample)
				outliers.append(sample)
				still_outliers = True

	return outliers

def cimbala_outliers(route):
	outliers = []

	if (len(route) > 0):
		still_outliers = True
		samples = getRttDifferences(route)

		#calcular la media
		mean = numpy.mean(samples)
		
		#calcular el desvio standard
		std_deviation = numpy.std(samples)
		
		#calcula el chirimbolo "r"
		thompson_gamma = calculate_thompson_gamma(samples)

		#busca outliers
		for sample in samples:
			delta = numpy.absolute(sample - mean)
			if (delta > thompson_gamma * std_deviation):
				outliers.append(sample)

	return outliers

#Usa los nombres de variables como los que estan en las formulas del paper
def calculate_thompson_gamma(rtts):
	n = len(rtts)
	
	#Studnt, n=999, p<0.05, 2-tail
	#equivalent to Excel TINV(0.05,999)
	t_a_2	= stats.t.ppf(1-0.025, n - 2)
	n_root = numpy.sqrt(n)

	numerator	 = t_a_2 * (n - 1)
	denominator = n_root * numpy.sqrt( n - 2 + numpy.power(t_a_2, 2) )

	return numerator / denominator
