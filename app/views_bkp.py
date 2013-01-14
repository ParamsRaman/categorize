from bottle import TEMPLATE_PATH, route, get, post, jinja2_template as template
from models import *
from bottle import static_file
from config import config
from datetime import datetime
import random
import sqlite3 as lite, xml.etree.ElementTree as et, os
import xml.dom.minidom as minidom

TEMPLATE_PATH.append("./app/templates")

class TreeNode(object):
	def __init__(self, label=None, id=None, children=[]):
		self.label = label
		self.id = id
		self.children = children

	def __eq__(self, other):
		if not isinstance(other, TreeNode):
			return False
		if self.label != other.label:
			return False
		return True

	def __hash__(self):
		return self.label

	def __contains__(self, key):
		return key == self.label

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

def find_uplist(node_id):
	uplist= []
	node = map[node_id]
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

"""def find_negative_nodes(results):
	choices = []
	choices.append('None')
	while results[0].id <= 20:
		random.shuffle(results)
	choices.append(results[0].label
		
				
	
	for n in final_candidates:
		print "Final Candidate: " + n.label

	return final_candidates	
"""
def find_negative_nodes(node, uplist):
	children = node.children
	print "finding negative node for: " + node.label
	candidates = [x for x in children if x not in uplist]
	for n in candidates:
		print "Candidate: " + n.label
	
	final_candidates = []
	for n in candidates:
		bag = []
		final_candidates.append(n)
		final_candidates.extend(find_nodes_in_subtree(n, bag))

	results = []	
	results = [x for x in final_candidates if x.children != []]
	
	for n in results:
		print "Final Candidate: " + n.label

	for j in results:
		print "NEGATIVES NODES LIST: " + j.label + ", id=" + str(j.id)
	random.shuffle(results)
	choices = []
	choices.append('None')
	if results  == []:
		print "UNABLE TO FIND -ve NODES"
		return results
	else:
		for n in results[0].children:
			print "SUPPOSED TO ADD: " + n.label
			choices.append(n.label)
		return choices	


# Class to represent Worker-Task record. This is written to the Worker_Task table in turk.db
class Worker_Task(object):
	def __init__(self, assignmentId=None, hitId=None, taskId=None, workerId=None, interfaceType=None, itemId=None, itemName=None, choices=None, answers=None, creationTime=None):
		self.assignmentId = assignmentId
		self.hitId = hitId
		self.taskId = taskId
		self.workerId = workerId
		self.interfaceType = interfaceType
		self.itemId = itemId
		self.itemName = itemName
		self.choices = choices
		self.answers = answers
		self.creationTime = creationTime

# List of Worker-Task records. Used to store intermediate info before posting to mech turk
worker_tasks = []

# Dictionary that stores the products/items to be categorized
products = {}

bucket_store = {}

# To store tree node mappings
map = {}

###################################################################################
# 	HELPER METHODS ARE DEFINED BELOW 					  #
###################################################################################

# To create the database and table to store worker-task info
def create_db():
	con = lite.connect(os.getcwd() + '/app/db/turk.db')
	with con:
		cur = con.cursor()
    		cur.execute("CREATE TABLE Worker_Tasks(AssignmentId TEXT, HitId TEXT, TaskId INT, WorkerId TEXT, InterfaceType INT, ItemId INT, ItemName TEXT, Choices TEXT, Answers TEXT, BucketId, CreationTime DATETIME)")
    		cur.execute("INSERT INTO Worker_Tasks VALUES('assign1', 'hit1', 'task1', 'worker1', 1, 1, 'scarf', '{a,b,c}', '{x,y,z}', 'p2', '')")

# To read items the taxonomy into dictionary
def load_items():
	tree = et.parse(os.getcwd() + '/app/db/taxonomy.xml')
	print "here1"
	root = tree.getroot()
	for item in root.iter('item'):
		item_name = item.text
		item_id = item.attrib["id"]
		products[int(item_id)] = {'id': item_id, 'title': item_name}
		print "Id: " + item_id + ", Title: " + item_name

"""def load_buckets():
	lines = open(os.getcwd() + '/app/db/buckets.psv')
	for line in lines:
		parts = line.strip().split('||')
		item_id = parts[0]
		bucket_id = parts[1]
		buckets = parts[2:]
		#For now, only picking buckets with values >= 3 
		if len(buckets) < 3:
			continue
		record_key = item_id + "." + bucket_id
		if record_key in bucket_store:
			bucket_store[record_key]['buckets'].extend(buckets)
		else:
			bucket_store[record_key] = dict({'item_id': item_id, 'bucket_id': bucket_id, 'buckets': buckets})
	print_dictionary(bucket_store)
	print "Count of bucket_store: " + str(len(bucket_store))
"""
	
def print_dictionary(d):
	for key, value in d.iteritems():
		print key, value		
	
###################################################################################
# 	ROUTES USED ARE DEFINED BELOW 						  #
###################################################################################

#To handle the landing page
@route('/')
def landing_page():
        int_type = config['INTERFACE_TYPE']
	#create_db()
	load_items()

	#read the taxonomy and create tree nodes
	tax = TreeNode('ROOT')
	map['ROOT'] = tax
	tax.parent = None
	tree = et.parse(os.getcwd() + '/app/db/taxonomy.xml')
	root = tree.getroot()
	result = populate_tree(tax, root)

        if int_type == 1:
		return template('instructions_1.html')
        elif int_type == 2:
		return template('instructions_2.html')
        elif int_type == 3:
		return template('instructions_3.html')

#To handle interface1
@post('/interface1')
def load_interface1(name='Stranger'):
	# Find random product
	random_item = random.randint(1, 20)
	print "Random item: " + str(random_item)
	random_item_name = products[random_item]['title']
	random_item_id = products[random_item]['id']
	print "Random item name: " + random_item_name
	print "Random item id: " + random_item_id
	depth_random_item = find_depth(map[int(random_item_id)]) 
	print "Depth: " + str(depth_random_item)
				
	# Calculate uplist for this product
	uplist = find_uplist(int(random_item_id))
	for n in uplist:
		print n.label
	print "uplist len: " + str(uplist)

	print "<<<<<<<<<<<<<<<<<<< RANDOM +VE QN >>>>>>>>>>>>>>>>>"
	#method to get a random postive qn at this level
	random_bucket = random.randint(3, len(uplist)-3)
	print "Random bucket: " + str(random_bucket) + ", Corresp node: " + uplist[random_bucket].label
	random_pos_node = uplist[random_bucket]
	options = random_pos_node.children
	choices = []
	if len(options) <= 3:
		choices.extend([x.label for x in options])
		choices.append('None')
	else:
		random.shuffle(options)
		choices.append(options[0].label)
		choices.append(options[1].label)
		choices.append(options[2].label)
		choices.append('None')
	print "Choices for positive buckets: " + str(choices)					
	print "<<<<<<<<<<<<<<<<<<< RANDOM -VE QN >>>>>>>>>>>>>>>>>"
	#method to get a random negative qn at this level		
	random_pos_node = uplist[random_bucket]
	print "Random bucket node: " + random_pos_node.label
	return	
	negative_nodes_list = []
	while negative_nodes_list == []:
		print "Negative Nodes List Empty, Retrying.."
		negative_nodes_list = find_negative_nodes(random_pos_node, uplist)

	print '||'. join(negative_nodes_list)
	print "Choices for negative buckets: " + str(choices)					
	current_task_id = config['CURRENT_TASK_ID']
	if current_task_id == config['NUM_TASKS']:
		#Submit to mech turk
		
		#Update turk.db with the records
		conn = lite.connect('turk.db')
		c = conn.cursor()
		for task in worker_tasks:
    			c.execute("INSERT INTO Worker_Tasks VALUES (?,?,?,?,?,?,?,?,?,?)", (task.assignmentId, task.hitId, task.taskId, task.workerId, task.interfaceType, task.itemId, task.itemName, task.choices, task.answers, task.creationTime))
		conn.commit()
		c.close()	
		return '<b>Maximum tasks reached as set by config..<br/> Tasks will be posted to mechanical turk and turk.db will be updated..</b>'
	else:
		current_task_id += 1
		config['CURRENT_TASK_ID'] = current_task_id
		current_item_id = config['CURRENT_ITEM_ID']
		if current_item_id == 20:
			config['CURRENT_ITEM_ID'] = 0
		else:
			current_item_id += 1
			config['CURRENT_ITEM_ID'] = current_item_id
		#task = Worker_Task('blabla', 'blabla', 'xyz', 1, current_task_id, products[random_item_id]['title'], "||".join(selected_choices), 'response', datetime.now())
		task = Worker_Task('blabla', 'blabla', 'xyz', 1, current_task_id, "bla bla", "answers", 'response', datetime.now())
		worker_tasks.append(task)
    		return template('interface1.html', task_id=current_task_id, total_num_tasks=config['NUM_TASKS'], item_image='/images/' + str(current_item_id) + '.jpg', item_id=current_item_id, item_name=products[current_item_id]['title']) 

#To handle interface2
@post('/interface2')
def load_interface1(name='Stranger'):
    	return template('interface2.html', name=name) 

#To handle interface3
@post('/interface3')
def load_interface1(name='Stranger'):
    	return template('interface3.html', name=name) 

#To display contents of the database
@route('/db')
def view_db():
	html_formatter = "<p>Database: turk.db <br/>Table: Worker_Tasks<br/>"
	con = lite.connect('turk.db')
	with con:
		cur = con.cursor()
		cur.execute("SELECT * from Worker_Tasks")
		rows = cur.fetchall()
		for row in rows:
			html_formatter = html_formatter + "<br/>" + str(row)
		html_formatter = html_formatter + "<br/><br/> Total rows: " + str(len(rows)) + "</p>"
	return html_formatter

#To handle static resource - images
@route('/images/:filename#.*#')
def server_static(filename):
    	return static_file(filename, root='./media/images/')

#To handle static resource - .js files
@route('/js/:filename#.*#')
def server_static(filename):
    	return static_file(filename, root='./media/js/')

#To handle static resource - .css files
@route('/css/:filename#.*#')
def server_static(filename):
    	return static_file(filename, root='./media/css/')
