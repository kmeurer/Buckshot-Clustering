import cluster as c
import entry as e
import numpy as np
import utils as util
import settings as ENV
import tabulate

# Main clustering class
class BuckshotClusters:
	# Constructor
	def __init__(self):
		self.resultsLog = []

	# Main clustering function
	def clusterEntries(self, entries):
		# STEP 1: Randomly select sqrt(n) adults and let them serve as our initial cluster centroids
		n = float(len(entries))			# store number of entries
		sqrtN = np.floor(np.sqrt(n))	# find the square root of our total number of entries
		clusters = []					# create a list to store our clusters
		iterator = 0					# create an iterator to manage while loop
		while iterator < sqrtN:
			iterator += 1
			entry = util.chooseOneWithoutReplacement(entries)
			clusters.append( c.Cluster(entry, [e.Entry( entry.getValues().copy() )] ) )
		while len(clusters) > ENV.K:
			# calculate a comparison matrix
			matrixInfo = self.createSimilarityMatrix(clusters)
			minimumDistance = matrixInfo[1]
			# Regardless of our method, we care most about our minimum distance clusters.  We merge those using the indices provided by the similarity matrix function
			if minimumDistance[0] < ENV.MAX_SIMILARITY_THRESHOLD:
				newCluster = c.mergeClusters(clusters[minimumDistance[1]], clusters[minimumDistance[2]])
			else:
				break
			# pop the larger index first
			if minimumDistance[1] > minimumDistance[2]:
				clusters.pop(minimumDistance[1]).printClusterData()
				clusters.pop(minimumDistance[2]).printClusterData()
			else:
				clusters.pop(minimumDistance[2])
				clusters.pop(minimumDistance[1])
			# add the new cluster to our list of clusters
			clusters.append(newCluster)
		# We now have our K clusters.  Now, we can assign the remaining entries to them and we're done
		count = 0
		print "Assigning remaining values to nearest cluster"
		if ENV.PROGRESS_BAR == True:
			util.updateProgress(0)
		for idx, entry in enumerate(entries):
			if ENV.PROGRESS_BAR == True:
				util.updateProgress(float(idx) / float(len(entries)))
			self.assignEntryToNearestCluster(entry, clusters)
			count += 1
		if ENV.PROGRESS_BAR == True:
			util.updateProgress(1)
		print "\nAssigned remaining " + str(count) + " entries to nearest clusters."
		self.computeAndDisplayResults(clusters)

	# Calculates error metrics and displays the results of the operation
	def computeAndDisplayResults(self, clusters):
		headers = ["Cluster Number", "Cluster Size", "Centroid Class Value", "Max Intra-Dist", "Sum of Squares Error"]
		resultsStore = []
		for idx, cluster in enumerate(clusters):
			data = [idx + 1, cluster.getSize()]
			cluster.recalculateCentroid()
			#  add centroid class value
			data.append(cluster.getCentroid().getValues()[ENV.CLASSIFIER_NAME])
			cluster.printClusterData()
			
			# Intra cluster distance calculation
			print "Calculating Max Intra Cluster Distance"
			micd = cluster.maxIntraClusterDistance()
			data.append(micd)
			print "\nMax intra-cluster distance: " + str(micd)
			
			# Sum of Squares Error calculation
			print "Calculating Sum of Squares Error"
			sse = cluster.sumOfSquaresError()
			data.append(sse)
			# Print sse
			print "\nSum of Squares Error: " + str(sse)
			
			# Add to our results store for result output later
			resultsStore.append(data)
		# Print and display results
		print "\nRESULTS:"
		print "K-Value: " + str(ENV.K) + "\nClassifier Name: " + str(ENV.CLASSIFIER_NAME)
		if ENV.USE_RANDOM_SAMPLE == True:
			print "SampleSize: " + str(ENV.SAMPLE_SIZE) + "\n"
		# Print a table of our results
		print tabulate(resultsStore, headers, tablefmt="grid")

	def assignEntryToNearestCluster(self, entry, clusters):
		minCluster = [clusters[0], entry.euclidianDist(clusters[0].getCentroid())]
		for cluster in clusters:
			dist = entry.euclidianDist(cluster.getCentroid())
			if dist < minCluster[1]:
				minCluster[0] = cluster
				minCluster[1] = dist
		minCluster[0].addEntry(entry)

	# Creates a similarity matrix.  Tracks the minimum and maximum values in the matrix. Returns in format[matrix, [minValue, idx1, idx2], [maxValue, idx1, idx2]]
	def createSimilarityMatrix(self, clusters):
		print "Constructing Similarity Matrix for " + str(len(clusters)) + " clusters using the " + ENV.MERGING_CRITERIA + " merging criteria."
		# Create a matrix full of None values of size equal to the length of clusters
		matrix = []
		count1 = 0
		minSimilarity = None
		maxSimilarity = None
		# Initialize matrix with all none values
		while count1 < len(clusters):
			count2 = 0
			matrix.append([])
			while count2 < len(clusters):
				matrix[count1].append(None)
				count2 += 1
			count1 += 1
		util.updateProgress(0)
		# for every single row
		for rowIdx, row in enumerate(matrix):
			util.updateProgress(float(rowIdx) / float(len(matrix)))
			# for each column
			for colIdx, col in enumerate(matrix):
				# we leave the value as None if 
				if rowIdx == colIdx:
					continue
				else:
					distance = None
					if ENV.MERGING_CRITERIA == "single-link":
						distance = clusters[rowIdx].singleLinkDist(clusters[colIdx])
					elif ENV.MERGING_CRITERIA == "complete-link":
						distance = clusters[rowIdx].completeLinkDist(clusters[colIdx])
					elif ENV.MERGING_CRITERIA == "centroid":
						distance = clusters[rowIdx].centroidDist(clusters[colIdx])
					if minSimilarity == None:
						minSimilarity = [distance, rowIdx, colIdx]
						maxSimilarity = [distance, rowIdx, colIdx]
					if distance < minSimilarity[0]:
						minSimilarity[0] = distance
						minSimilarity[1] = rowIdx
						minSimilarity[2] = colIdx
					if distance > maxSimilarity[0]:
						maxSimilarity[0] = distance
						maxSimilarity[1] = rowIdx
						maxSimilarity[2] = colIdx
					matrix[rowIdx][colIdx] = distance
		util.updateProgress(1)
		print "\nMatrix construction complete.\n"
		return [matrix, minSimilarity, maxSimilarity]

		