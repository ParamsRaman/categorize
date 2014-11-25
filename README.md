categorize
==========

Set up categorization experiments based on a taxonomy of items (eg: shopping) and post mechanical turk tasks to collect user responses for evaluation.

Idea is to evaluate various user interfaces used in classifying items and come up with theoretical guarantees based on observing user responses.

##### Overall Design of the system and its various components:

The taxonomy has been hand-crafted (based on Amazon’s shopping catalog) in the form of a mind map file (.mm). Mindmap format is easy to view, expand, collapse nodes and also useful during debugging. Use FreeMind software to open this file to view the taxonomy.

A python (bottle-based) web application has been used to create the questions by sampling different nodes in the taxonomy. This application starts off by reading the taxonomy from an xml file (an xml file was created for the same .mm file) and storing it into a sqlite database table. Another table called tasks_distribution stores the various combinations of the products, items, etc that form the task. It also records the number of times it was shown to the user along with the response.

Mechanical Turk allows creation of various types of tasks. In this case, we point the mechanical task experiment to use an External web site as the source for interaction. Then, on starting the mechanical turk experiment, our external website loads up inside a frame in the mechanical turk environment itself. Python’s Boto library has been used to create a HIT programatically as an ExternalQuestion type. Although I was able to create a HIT and see that our website gets loaded as an embedded page, the frames were messed up badly. The website was not fully visible and buttons got hidden below. Basically UI needed to be fixed. I have not got past that stage.

##### Description of the Code/Resources in the archive:

The source code root directory looks like below:

categorize - 

      * app (contains the bootle web application project)

                 * db (contains all sqlite db related stuff)
                         * turk.db (this is the database binary file)
                         * taxonomy.xml (this is xml equivalent of the mindmap file which is loaded into the db). I had to remove duplicate nodes at some point.
                 * templates (contains all the html files for the interfaces used. We mainly looked at three types of interfaces, them should explain themselves when viewed, but if not, please contact me)
                 * create_tables.py (to create the sqlite db and tables from scratch. this is done only once and then tables are updated. **It is also useful if you accidently delete the turk.db sqlite file**).
                 * views.py (this is the MAIN source code file that contains most of the logic. **I have described the important methods in this file in a separate section below!**
                 * taxonomy_tree.py (contains a custom definitoin of TreeNode class used by views.py. I could not find a python based tree implementation, so defined one myself. Advantage of this was that I could write my own methods to traverse the tree in ways to suit our experiment).

        * mechanical_turk (contains boto library and createHIT.py - which is the python boto code to create an ExternalQuestion type task in mechanical turk). This works, but the frame issue **has to be fixed**.
        * media (contains the css files used, javascript and importantly all the images for the products etc which are pulled by the html files when displayed). I think at this point, we restricted ourselves to only 20 products (leaf level nodes).
        * packages (contains bottle which is the web framework, jinja which is the templating engine for all the UI stuff)
        * app.yaml, index.yaml (are bottle specific files that need to be present)

