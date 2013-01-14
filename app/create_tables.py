import sqlite3 as lite
import sys,os

con = lite.connect(os.getcwd() + '/db/turk.db')
with con:
	cur = con.cursor()
	cur.execute("CREATE TABLE IF NOT EXISTS WORKER_TASKS(AssignmentId TEXT, HitId TEXT, TaskId INT, WorkerId TEXT, InterfaceType INT, ItemId INT, ItemName TEXT, Combination TEXT, Choices TEXT, Answers TEXT, CreationTime DATETIME)")
	print "WORKER_TASKS table created.."
	cur.execute("CREATE TABLE IF NOT EXISTS TASKS_DISTRIBUTION(Combination TEXT, ProductName TEXT, BucketNode TEXT, count INT)")
	print "TASKS_DISTRIBUTION table created.."
	con.commit()

    
