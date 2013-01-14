from bottle import TEMPLATE_PATH, route, request, get, post, jinja2_template as template
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
		#return self.label
		return hash(('label', self.label))

	def __contains__(self, key):
		return key == self.label

	def append(self, node):
		self.children.append(node)
		#print node.label + " ---- appended to ----> " + self.label
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
			subtree = TreeNode(child_name)
			subtree.id = int(child.attrib['id'])
			subtree.children = []
			if subtree.id in map:
				print str(subtree.id) + " ALREADY IN MAP!!!!! "
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

def find_negative_nodes(uplist, random_bucket):
	print "Random bucket: " + str(random_bucket) + ", Corresp node: " + uplist[random_bucket].label
	node = uplist[random_bucket]
	children = node.children
	print "finding negative node for: " + node.label

	candidates = []
	for x in children:
		# Candidates should not appear in the uplist as well as
		# Eliminate nodes which have no children to pick (as this causes
		# infinite retries later on)
		print "Candidate Checking: " + x.label + ", Depth: " + str(find_depth(map[x.id]))
		if x not in uplist and find_depth(map[x.id]) > 2:
			candidates.append(x)
	for n in candidates:
		print "Candidate: " + n.label + ", Depth: " + str(find_depth(map[n.id]))
	
	final_candidates = []
	for n in candidates:
		bag = []
		final_candidates.append(n)
		final_candidates.extend(find_nodes_in_subtree(n, bag))

	results = []	
	results = [x for x in final_candidates if x.children != []]
	
	#for j in results:
	#	print "NEGATIVES NODES LIST: " + j.label + ", id=" + str(j.id)
	
	random.shuffle(results)
	tmp = []
	#tmp.append('None')
	if results  == []:
		print "UNABLE TO FIND -ve NODES"
		return results
	else:
		for n in results[0].children:
			# Prevent <item> product text from being returned
			if n.id <=20:
				return []
			#print "SUPPOSED TO ADD: " + n.label
			
			# len() check < 3, because 'None' is added later in the 
			# main while loop
			if len(tmp) < 3:
				tmp.append(n.label)
		return tmp	


# Class to represent Worker-Task record. This is written to the worker_task table in turk.db
class Worker_Task(object):
	def __init__(self, assignmentId=None, hitId=None, taskId=None, workerId=None, interfaceType=None, itemId=None, itemName=None, combination=None, choices=None, answers=None, creationTime=None):
		self.assignmentId = assignmentId
		self.hitId = hitId
		self.taskId = taskId
		self.workerId = workerId
		self.interfaceType = interfaceType
		self.itemId = itemId
		self.itemName = itemName
		self.combination = combination
		self.choices = choices
		self.answers = answers
		self.creationTime = creationTime

# Class to represent Task Distribution record. This is written to the TASKS_DISTRIBUTION table in turk.db
class Task_Distribution(object):
	def __init__(self, Combination=None, ProductName=None, BucketNode=None, Count=0):
		self.Combination = Combination
		self.ProductName = ProductName
		self.BucketNode = BucketNode
		self.Count = Count

# List of Worker-Task records. Used to store intermediate info before posting to mech turk
worker_tasks = []

# Dictionary that stores the products/items to be categorized
products = {}

# To store tree node mappings
map = {}

# To create the database and table to store worker-task info
def create_db():
	con = lite.connect(os.getcwd() + '/app/db/turk.db')
	with con:
		cur = con.cursor()
    		cur.execute("CREATE TABLE WORKER_TASKS(AssignmentId TEXT, HitId TEXT, TaskId INT, WorkerId TEXT, InterfaceType INT, ItemId INT, ItemName TEXT, Combination TEXT, Choices TEXT, Answers TEXT, BucketId, CreationTime DATETIME)")
    		cur.execute("INSERT INTO WORKER_TASKS VALUES('assign1', 'hit1', 'task1', 'worker1', 1, 1, 'scarf', '1.1.1', '{a,b,c}', '{x,y,z}', 'p2', '')")

# To read products into a dictionary for meta-data lookup
def load_items():
	tree = et.parse(os.getcwd() + '/app/db/taxonomy.xml')
	root = tree.getroot()
	for item in root.iter('item'):
		item_name = item.text
		item_id = item.attrib["id"]
		products[int(item_id)] = {'id': item_id, 'title': item_name}
		#print "Id: " + item_id + ", Title: " + item_name
	
def print_dictionary(d):
	for key, value in d.iteritems():
		print key, value		

def table_empty(table):
	con = lite.connect(os.getcwd() + '/app/db/turk.db')
	with con:
		cur = con.cursor()
		cur.execute("SELECT COUNT(*) FROM TASKS_DISTRIBUTION")
		rows = cur.fetchall()
		print "# of Rows in Tasks Distribution Table: " + str(rows[0][0])

	if int(rows[0][0]) == 0:
		return True
	else:
		return False

def find_next_qn():
	con = lite.connect(os.getcwd() + '/app/db/turk.db')
	with con:
		cur = con.cursor()
		cur.execute("SELECT Combination FROM TASKS_DISTRIBUTION order by cast(count as numeric) LIMIT 1")
		rows = cur.fetchall()
		print "Retrieving next combination from Tasks Distribution Table: " + str(rows[0][0])
	return str(rows[0][0])	

def incr_task_distribution(qn_id):
	con = lite.connect(os.getcwd() + '/app/db/turk.db')
	with con:
		cur = con.cursor()
		cur.execute("UPDATE TASKS_DISTRIBUTION SET count=count+1 WHERE Combination=?", (qn_id,))
		print "Updating Tasks Distribution Table: " + qn_id 
		con.commit()
	
#To handle the landing page
@route('/')
def landing_page():
	# Retrive GET data passed from Mechanical Turk
	assignmentId = request.GET.get('assignmentId')
	hitId = request.GET.get('hitId')

	int_type = config['INTERFACE_TYPE']

	# Read product items into lookup table
	load_items()

	# Read the taxonomy and create tree nodes, populate map lookup table, 
	tax = TreeNode('ROOT')
	map[331] = tax
	tax.parent = None
	tree = et.parse(os.getcwd() + '/app/db/taxonomy.xml')
	root = tree.getroot()
	result = populate_tree(tax, root)
	
	# Populate TASKS_DISTRIBUTION table
	if table_empty("TASKS_DISTRIBUTION"):	
		print "Tasks Distribution Table Empty"
		td_list = []

		for key in products:
			uplist = find_uplist(int(key))
			length = len(uplist)
			print "Product id: " + str(key) + ", Uplist length: " + str(length)
			for n in range(0, length-3):
				col1_a = str(key) + "." + str(n) + ".1"
				col1_b = str(key) + "." + str(n) + ".2"
				col2 = products[key]['title']
				col3 = uplist[n].label
				col4 = 0
				td_list.append(Task_Distribution(str(col1_a), str(col2), str(col3), str(col4)))
				td_list.append(Task_Distribution(str(col1_b), str(col2), str(col3), str(col4)))

		# Shuffle the list if needed
		random.shuffle(td_list)
		length = len(td_list)

		con = lite.connect(os.getcwd() + '/app/db/turk.db')
		with con:
			cur = con.cursor()
			for i in range(0, length):
				t = td_list[i]
				cur.execute("INSERT INTO TASKS_DISTRIBUTION VALUES(?,?,?,?)", (t.Combination, t.ProductName, t.BucketNode, t.Count))
				print "[TASKS_DISTRIBUTION] Inserting record: " + str(t.Combination) + ", " + str(t.ProductName) + ", " + str(t.BucketNode) + ", " + str(t.Count)
		con.commit()
	else:
		print "Tasks Distribution Table Not Empty"

        if int_type == 1:
		return template('instructions_1.html')
        elif int_type == 2:
		return template('instructions_2.html')
        elif int_type == 3:
		return template('instructions_3.html')

#To handle interface1
@post('/interface1')
def load_interface1(name='Stranger'):
	
	# To retrive the POST data
	multi_dict = request.forms 
        values = multi_dict.keys()

	if values != []:
        	print "POST data: " + str(values)
		qn_response = str(multi_dict.dict['selected_choice'][0])
		print "POST data for selected_choice: " + qn_response

	""" BEGIN while loop """
	choices = []
	while choices == []:
		print "{{{{{{{{{{{{{{{{{{{{{{{{ INSIDE WHILE LOOP }}}}}}}}}}}}}}}}}}"

		# Find next question from TASKS_DISTRIBUTION table
		qn_id = find_next_qn()
		#qn_id = '16.0.1'	
		#qn_id = '17.2.2'
		#qn_id = '13.0.1'	
		#qn_id = '2.3.2'
		parts = qn_id.split('.')
		
		# Find random product
		random_item = int(parts[0])
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

		random_bucket = int(parts[1])
		#print "Random bucket: " + str(random_bucket) + ", Corresp node: " + uplist[random_bucket].label
		random_pos_node = uplist[random_bucket]
		print "Random pos node (finding positive nodes for): " + random_pos_node.label

		# Generate positive bucket qn
		#choices = []
		if int(parts[2]) == 1:
			print "<<<<<<<<<<<<<<<<<<< RANDOM +VE QN >>>>>>>>>>>>>>>>>"
			options = []
			options.extend(random_pos_node.children)
			choices[:] = []
			if len(options) <= 3:
				choices.extend([x.label for x in options])
			else:
				random.shuffle(options)
				options = list(set(options)) # To fix the list duplication problem
				for x in options:
					if x in uplist:
						choices.append(x.label)
				
				tmp = []
				for x in options:
					if x not in uplist:
						tmp.append(x.label)
				choices.append(tmp[0])
				choices.append(tmp[1])
			print "Choices for positive buckets: " + '||'. join(choices)
			
		# Generate negative bucket qn
		elif int(parts[2]) == 2:
			print "<<<<<<<<<<<<<<<<<<< RANDOM -VE QN >>>>>>>>>>>>>>>>>"
			choices[:] = []
			choices = find_negative_nodes(uplist, random_bucket)
			print "Choices for negative buckets: " + '||'. join(choices)
		# Increment this combination by 1, so that it doesn't repeat until 
		# the others are chosen
		incr_task_distribution(qn_id)
	""" END while loop """
	# Add 'None' after the while loop, so that while loop termination condition
	# can be choices being empty
	choices.append('None')
	
	#incr_task_distribution(qn_id)
	
	current_task_id = config['CURRENT_TASK_ID']
	if current_task_id > 0:
		worker_tasks[current_task_id-1].answers = qn_response
	if current_task_id == config['NUM_TASKS']:
		#Submit to mech turk
		
		#Update turk.db with the records
		con = lite.connect(os.getcwd() + '/app/db/turk.db')
		c = con.cursor()
		for task in worker_tasks:
    			c.execute("INSERT INTO WORKER_TASKS VALUES (?,?,?,?,?,?,?,?,?,?,?)", (task.assignmentId, task.hitId, task.taskId, task.workerId, task.interfaceType, task.itemId, task.itemName, task.combination, task.choices, task.answers, task.creationTime))
		con.commit()
		c.close()	
		config['CURRENT_TASK_ID'] = 0
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
		task = Worker_Task('blabla', 'blabla', 'xyz', 'pqr', 1, random_item, products[random_item]['title'], qn_id, '||'. join(choices), '', datetime.now())
		worker_tasks.append(task)
    		return template('interface1.html', task_id=current_task_id, total_num_tasks=config['NUM_TASKS'], item_image='/images/' + str(random_item) + '.jpg', item_id=random_item, item_name=products[random_item]['title'], choices_string='||'. join(choices)) 

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
	html_formatter = "<p><b>Database: turk.db </b><br/><br/><b>Table: WORKER_TASKS</b><br/>"
	con = lite.connect(os.getcwd() + '/app/db/turk.db')
	with con:
		cur = con.cursor()
		cur.execute("SELECT * from WORKER_TASKS")
		rows = cur.fetchall()
		html_formatter += "<table border='1'><tr bgcolor='#6699FF'><th>AssignmentId</td><td>HitId</td><td>TaskId</td><td>WorkerId</td><td>InterfaceType</td><td>ItemId</td><td>ItemName</td><td>Combination</td><td>Choices</td><td>Answers</td><td>CreationTime</td></tr>"
		for row in rows:
			#html_formatter = html_formatter + "<br/>" + str(row)
			html_formatter = html_formatter + "<tr>"
			html_formatter = html_formatter + "<td>" + str(row[0]) + "</td>"
			html_formatter = html_formatter + "<td>" + str(row[1]) + "</td>"
			html_formatter = html_formatter + "<td>" + str(row[2]) + "</td>"
			html_formatter = html_formatter + "<td>" + str(row[3]) + "</td>"
			html_formatter = html_formatter + "<td>" + str(row[4]) + "</td>"
			html_formatter = html_formatter + "<td>" + str(row[5]) + "</td>"
			html_formatter = html_formatter + "<td>" + str(row[6]) + "</td>"
			html_formatter = html_formatter + "<td>" + str(row[7]) + "</td>"
			html_formatter = html_formatter + "<td>" + str(row[8]) + "</td>"
			html_formatter = html_formatter + "<td>" + str(row[9]) + "</td>"
			html_formatter = html_formatter + "<td>" + str(row[10]) + "</td>"
			html_formatter = html_formatter + "</tr>"
		html_formatter += "</table>"	
		html_formatter += "<br/>Total rows: " + str(len(rows)) + "</p>"
		
		html_formatter += "<hr/><b>Table: TASKS_DISTRIBUTION</b><br/>"
		html_formatter += "<i>Combination:</i> a.b.c<br/>"
		html_formatter += "a = Product Item Id (1-20)<br/>"
		html_formatter += "b = Bucket Node Id (this is computed on the fly depending on depth of the product item node)<br/>"
		html_formatter += "c = 1 for +ve bucket, 2 for -ve bucket<br/>"
		cur.execute("SELECT * from TASKS_DISTRIBUTION")
		rows = cur.fetchall()
		html_formatter += "<table border='1'><tr bgcolor='#6699FF'><th>Combination</td><td>ProductName</td><td>BucketNode</td><td>Count</td></tr>"
		for row in rows:
			html_formatter = html_formatter + "<tr>"
			html_formatter = html_formatter + "<td>" + str(row[0]) + "</td>"
			html_formatter = html_formatter + "<td>" + str(row[1]) + "</td>"
			html_formatter = html_formatter + "<td>" + str(row[2]) + "</td>"
			html_formatter = html_formatter + "<td>" + str(row[3]) + "</td>"
			html_formatter = html_formatter + "</tr>"
		html_formatter += "</table>"	
		html_formatter += "<br/>Total rows: " + str(len(rows)) + "</p>"
		
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
