import json, re, urllib3, sys, os, enum
import _pickle as pickle
import numpy as np
import pandas as pd
from copy import deepcopy
from sklearn.metrics.pairwise import cosine_similarity

class SPARQLOperator(object):
	def __init__(self, config_filename=None, query_filename=None):
		if config_filename:
			self.config_details = self.read_json(config_filename)
			self.prefix_header = self.set_prefix_header(self.config_details["prefixes"])
		if query_filename:
			self.queries = self.read_json(query_filename)

	def read_json(self, filename):
		with open(filename) as config:
			details = json.load(config)
		return details

	def getPredicate(self, term):
		predicateParts = re.split('[^0-9a-zA-Z_\-]+', term)
		return predicateParts[len(predicateParts)-1]

	def getId(self, uri):
		uriParts = uri.split(":")
		return uriParts[len(uriParts)-1]

	def getLabel(self, label):
		labelParts = label.split("@")
		if len(labelParts) > 1:
			ref_label = labelParts[0][1:-1]
			return ref_label
		else:
			return label

	def set_prefix_header(self, prefixes):
		prefix_header = ""
		for prefix in prefixes:
			prefix_header = prefix_header + "PREFIX " + prefix + ": <" + prefixes[prefix] + "> "
		return prefix_header

	def get_endpoint(self, datasource, endpoints):
		# maybe modify this
		g = rdflib.Graph('TPFStore')
		g.open(endpoints[datasource]["link"])
		return g

	def get_simple_results(self, ontology, query_type):
		g = self.get_endpoint(ontology, self.config_details["endpoints"])
		query =  self.prefix_header + "".join(self.queries[ontology][query_type])
		results = g.query(query)
		return results

class MatrixIO(object):
	def save_matrix(self, x, filename):
		with open(filename, 'wb') as outfile:
			pickle.dump(x, outfile)

	def load_matrix(self, filename):
		with open(filename, 'rb') as infile:
			x = pickle.load(infile)
		return x

	def save_matrix_txt(self, x, filename):
		np.savetxt(filename, x, delimiter="\t")

	def load_matrix_txt(self, filename):
		return np.matrix(np.loadtxt(filename, delimiter="\t"))

class FileUtils(object):
	def get_reqd_fileset(self, folder_path, exclusion_criteria=None):
		"A class of navigators on the file system"
		fileset = None
		for root, dirs, files in os.walk(folder_path):
			fileset = [x for x in files if not exclusion_criteria(x)] if exclusion_criteria else files
		return fileset

	def assign_filesize(self, folder_path, exclusion_criteria=None):
		'''Returns a dict with file name as key and its size (bytes) as value'''
		fileset = self.get_reqd_fileset(folder_path, exclusion_criteria)
		file_dict = {}
		for _file in fileset:
			size = os.stat(folder_path + _file).st_size
			file_dict[_file] = size
		return file_dict


class SIZE_UNIT(enum.Enum):
	BYTES = 1
	KB = 2
	MB = 3
	GB = 4

def convert_unit(size_in_bytes, unit):
	""" Convert the size from bytes to other units like KB, MB or GB"""
	if unit == SIZE_UNIT.KB:
		return size_in_bytes/1024
	elif unit == SIZE_UNIT.MB:
		return size_in_bytes/(1024*1024)
	elif unit == SIZE_UNIT.GB:
		return size_in_bytes/(1024*1024*1024)
	else:
		return size_in_bytes

class FrameUtils(object):
	def convertdf(self, df, column):
		''' this is a new way to convert a dataframe into a dictionary, such that values of a column end up becoming the keys in the dictionary
		This function should be moved to Utils'''
		# such that values in one column become the keys
		dfc = deepcopy(df)
		dfc = dfc.set_index(column) 
		return dfc.to_dict(orient="index")


class HTTPUtils(object):
	def get_json(self, url, headers=None):
		try:
			opener = urllib3.build_opener()
			if headers:
				opener.addheaders = headers
			return json.loads(opener.open(url).read())
		except urllib3.HTTPError:
			print ('Error Encountered')
			return None

def get_rel_uuid(uri):
	urip = uri.split("/")
	return urip[len(urip)-1]
