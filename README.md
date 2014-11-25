categorize
==========

Set up categorization experiments based on a taxonomy of items (eg: shopping) and post mechanical turk tasks to collect user responses for evaluation.

Idea is to evaluate various user interfaces used in classifying items and come up with theoretical guarantees based on observing user responses.

##### Overall Design of the system and its various components:
The taxonomy has been hand-crafted (based on Amazon’s shopping catalog) in the form of a mind map file (.mm). Mindmap format is easy to view, expand, collapse nodes and also useful during debugging. Use FreeMind software to open this file to view the taxonomy.

A python (bottle-based) web application has been used to create the questions by sampling different nodes in the taxonomy. This application starts off by reading the taxonomy from an xml file (an xml file was created for the same .mm file) and storing it into a sqlite database table. Another table called tasks_distribution stores the various combinations of the products, items, etc that form the task. It also records the number of times it was shown to the user along with the response.

Mechanical Turk allows creation of various types of tasks. In this case, we point the mechanical task experiment to use an External web site as the source for interaction. Then, on starting the mechanical turk experiment, our external website loads up inside a frame in the mechanical turk environment itself. Python’s Boto library has been used to create a HIT programatically as an ExternalQuestion type. Although I was able to create a HIT and see that our website gets loaded as an embedded page, the frames were messed up badly. The website was not fully visible and buttons got hidden below. Basically UI needed to be fixed. I have not got past that stage.
