from bottle import route, run, template, view
import os

dict = {'name': 'xyz', 'age': 21};

@route('/')
@route('/hello/:name')
@view('hello_template')
def index(name='World'):
	#return template('<b>Hello {{name}}</b>!', name=name)
	#return template('hello_template', name=name)
	return dict(name=name)
run(host='localhost', port=8080)
