import sqlite3 as lite, xml.etree.ElementTree as et, os
import xml.dom.minidom as minidom
#from xml.dom.minidom import parseString

class TaxonomyTree(object):
	"""
	Class to read from taxonomy and populate a tree out of it.
	Also has functions for basic tree operations.
	"""

	def __init__(self, xml_file):
		tree = et.parse(os.getcwd() + '/db/taxonomy.xml')
		root = tree.getroot()
		self.root = root
		TaxonomyTree.pretty_print_node(root)
		
	@staticmethod
	def pretty_print_node(node):
		text = et.tostring(node)
		print minidom.parseString(text).toprettyxml()	

	def get_pos_buckets(self, node_id):
		found = self.root.findall(".//item[@id='%s']" % node_id)
    		if found:
        		print found[0].text
			print found[0].find('..')
		else:
			print "not found"

		#for target in self.root.findall(".")
		#	print target._children	
		

if __name__ == "__main__":
	t = TaxonomyTree("abc")
	buckets = []
	
	buckets = t.get_pos_buckets("10")
	buckets = t.get_pos_buckets("18")
		
		
						
		
