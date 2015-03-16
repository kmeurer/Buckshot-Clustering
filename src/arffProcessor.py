import codecs
import re
import utils as util
import settings

# readArff( fileSrc ): takes a file path for an arff and returns a list of dictionaries as well as a d
def readArff(fileSrc):
	# main variables to be returned
	relation = ""									# relation		
	attributes = []									# attribute list
	rawData = []									# main data storage
	reverseLookup = {}								# store by value for reverse lookup
	continuousVariables = {}
	categoricalVariables = {}
	classIdx = None
	dataFile = codecs.open(fileSrc, 'rb', 'utf-8') 	# specify utf-8 encoding
	print "Reading file..."
	lines = dataFile.readlines() 					# read all lines
	if settings.PROGRESS_BAR == True:
		util.updateProgress(0)					# create a progress bar
	# test every line and extract its relevant information
	for idx, line in enumerate(lines):				# test each line
		if settings.PROGRESS_BAR == True:
			util.updateProgress(float(idx) / float(len(lines)))
		if line[0] == '%':							# ignore comments
			continue
		elif line[0] == '@':						# if is metadata
			if '@relation' in line:					# if relation
				arrayLine = line.split(" ")
				relation = arrayLine[1]
			elif "@attribute" in line:				# if attribute
				arrayLine = line.split(" ")
				attributes.append([arrayLine[1]])
				if arrayLine[1] == settings.CLASSIFIER_NAME:
					classIdx = len(attributes) - 1
				if "real" not in arrayLine[2]:		# if attribute is not real (is categorical)
					attrs = re.search('\{(.*?)\}', line).group()	# select text between brackets
					attrs = re.sub('[\{\}]', "", attrs)				# remove brackets
					newAttrs = attrs.split(", ")					
					options = []
					for attr in newAttrs:
						options.append(attr)
					attributes[len(attributes) - 1].append(options)
				else: 							# if it is real
					attributes[len(attributes) - 1].append('real')
		elif line[0] == " ":
				continue
		else:
			line = line.replace(" ", "")
			line = line.replace("\n", "")
			line = line.split(",")
			newDataEntry = {}							# create a new object to store our row data
			for idx, value in enumerate(line):			# for every column of data
				attribute = attributes[idx]
				if util.isNumber(value):						# convert string to float if it's a number
					value = float(value)
				# Add value to our reverse lookup under the key "attributeName attributeValue"
				rlKey = attribute[0] + " " + str(value) 	# create key for our reverseLookup data structure
				if rlKey in reverseLookup:
					reverseLookup[rlKey].append(len(rawData)) # append index of our current row (the length of data) for quick lookup later
				else:
					reverseLookup[rlKey] = [len(rawData)]	# create a new arrayList to store our indices if one does not already exist
				# fill our newData Entry
				newDataEntry[attribute[0]] = value 			# store the value under its proper key
				# add variables to our bins
				if attribute[1] == 'real':  				# if the attribute is real, we place it in a continuous bin
					if attribute[0] in continuousVariables:
						continuousVariables[attribute[0]].add(value, line[classIdx])							# add our value to our continuous bin
					else:
						continuousVariables[attribute[0]] = util.continuousBin(attribute[0])	# instantiate a continuous bin to hold our variable
						continuousVariables[attribute[0]].add(value, line[classIdx])
				else:									# if the attribute is categorical, we place it in a categorical bin
					# Get class value for this entry:
					if attribute[0] in categoricalVariables:
						categoricalVariables[attribute[0]].add(value, line[classIdx])
					else:
						categoricalVariables[attribute[0]] = util.categoricalBin(attribute[1])
						categoricalVariables[attribute[0]].add(value, line[classIdx])
			rawData.append(newDataEntry)					# append data entry to all of our data
	# END OF FOR LOOP
	results = {}
	results['data'] = rawData
	results['attributes'] = attributes
	results['relation'] = relation
	results['lookup'] = reverseLookup
	results['continuousVariables'] = continuousVariables
	results['categoricalVariables'] = categoricalVariables
	if settings.PROGRESS_BAR == True:
		util.updateProgress(1)
	print "\nFile read complete \n"
	return results
