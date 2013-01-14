import sqlite3 as lite, xml.etree.ElementTree as et, os
import xml.dom.minidom as minidom

map = {}

class TreeNode(object):
	def __init__(self, label=None, id=None, children=[]):
		self.label = label
		self.id = id
		self.children = children

	def append(self, node):
		self.children.append(node)
		print node.label + " ---- appended to ----> " + self.label
		node.parent = self

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

def populate_tree(tax, node):
	children = node.getchildren()
	if len(children) > 0:
		for child in children:
			if child.tag == 'category':
				child_name = child.attrib['name']
			elif child.tag == 'item':
				child_name = child.text
			#print "child: " + child_name
			subtree = TreeNode(child_name)
			subtree.id = int(child.attrib['id'])
			subtree.children = []
			if subtree.id in map:
				print child_name + " ALREADY IN MAP!!!!! "
			map[subtree.id] = subtree
			tax.append(subtree)
			#print "subtree - " + subtree.label + " (" + str(subtree.children) + ") " + "-----APPENDED TO---->" + "tax node - " + tax.label + " (" + str(tax.children) + ")"
			populate_tree(subtree, child)
	else:
		return tax

def find_uplist(node_label):
	uplist= []
	node = map[node_label]
	while node is not None:
		uplist.append(node)
		node = node.parent

	#print "uplist: " + str(uplist)
	#return reversed(uplist)
	return uplist[::-1] #returns reversed list

def find_depth(node):
	if node is None:
		return 0
	max = 0
	for n in node.children:
		ht = find_depth(n)
		if find_depth(n) > max:
			#print "depth passed: " + n.label + " with height: " + str(ht)
			max = ht
	return max+1			

def find_nodes_in_subtree(node, results):
	children = node.children
	#print "Node is: " + node.label + ", children are: " + str(children)
	#for n in children:
	#	print "CHILDREN: " + n.label
	if len(children) > 0:
		bag = []
		for child in children:
			if child.id > 20:
				results.append(child)
				bag.append(child)
				results.extend(find_nodes_in_subtree(child, results))
				bag.extend(find_nodes_in_subtree(child, results))
		return bag
	else:
		return []

def print_dictionary(d):
    for key, value in d.iteritems():
        print key, value.label

if __name__ == "__main__":
	tax = TreeNode('ROOT')
	map['ROOT'] = tax
	tax.parent = None
	
	tree = et.parse(os.getcwd() + '/db/taxonomy.xml')
	root = tree.getroot()

	result = populate_tree(tax, root)

	print "<<<<<<<<<<<<<<< PRINTING PREORDER >>>>>>>>>>>>>>>"
	#preorder(result)
	#print map["shoe bags"].label
	#print map["shoe bags"].parent.label
	#print map["shoe bags"].parent.parent.label
	#print len(map["shoe bags"].parent.parent.children)

	#for n in tax.children[0].children[0].children:
	#	print "result children: " + n.label
	
	#nodes = find_uplist('Samsonite Luggage 2 Pack Vinyl ID Tag')
	#nodes = find_uplist('SANUS SYSTEMS BF-31B Wood Speaker Stands')
	
	#n = map['clothing accessories']
	#print "clothign accessoreis node: " + n.label
	#for i in n.children:
	#	print "clothign children: " + i.label	

	print_dictionary(map)	

	results = []
	tmp = find_nodes_in_subtree(map[208], results)
	print "Results outside: " + str(tmp)
	for j in tmp:
		print "FINAL CANDIDATES: " + j.label + ", id=" + str(j.id)

	print "Depth: " + str(find_depth(map[346]))
	print "Depth: " + str(find_depth(map[347]))
	print "Depth: " + str(find_depth(map[1]))
	
	#for n in nodes:
	#	print n.label

	#print find_depth(map["shot glasses"])

	#print map["shoe bags"].parent.parent.label
	#print map["shoe bags"].parent.parent.parent.label
	#print map["shoe bags"].parent.parent.parent.parent.label
	#print map["shoe bags"].parent.parent.parent.parent.parent.label

	#self.root = root
	#TaxonomyTree.pretty_print_node(root)
	
