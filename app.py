import re

from flask import render_template
from flask import Flask
from flask import abort
from flask import request

from pymongo import MongoClient

from db_generator import generate_db
from db_generator import names


app = Flask(__name__)
client = MongoClient("mongodb://mongo:27017")
db = client.test


@app.route('/clear')
def clear():
	""" Clear database """
	try:
		db.inventory.delete_many({})
	except Exception as err:
		return "<h1>Error occurred while clearing database: {}</h1>".format(err)
	else:
		return "<h1>Clearing complete</h1>"


@app.route('/generate')
def generate_defualt():
	""" Generate database with default parameters """

	try:
		db.inventory.delete_many({})
		generate_db()
	except Exception as err:
		return "<h1>Error occurred while generating database: {}</h1>".format(err)
	else:
		return "<h1>Generation complete</h1>"


@app.route('/generate<db_size>_<max_temp_size>')
def generate(db_size, max_temp_size):
	""" Generate database with custom parameters db_size and max_temp_size"""
	# Max temp size shouldn't be more then 12!!!
	try:
		if int(max_temp_size) > 12:
			raise OverflowError("Too big size for template") 
		db.inventory.delete_many({})
		generate_db(db_size=int(db_size), max_temp_size=int(max_temp_size))
	except Exception as err:
		return "<h1>Error occurred while generating database: {}</h1>".format(err)
	else:
		return "<h1>Generation complete</h1>"


@app.route('/show-database')
def show():
	""" Show database content without ids """ 

	items = db.inventory.find(
		{"$and":
			[
				{"worker_name":  {'$exists': True}}, 
			 	{"client_phone":  {'$exists': True}},
			 	{"purchase_date":  {'$exists': True}}
			]
		}
	)
	# items = db.inventory.find({})
	page = ""
	for item in items:
		item.pop('_id')
		page += str(item) + "<br>"
	if len(page) == 0:
		return "<h1>Database empty</h1>"
	return page


@app.route('/get_form', methods=['POST'])
def get_form():
	""" Main function which return template form or form in necessary view """

	def value_type(value):
		if re.match("\+7 \d{3} \d{3} \d\d \d\d", value):
			return "phone"
		elif re.match("(\d\d\.){2}\d{4}", value):
			day, month, year = tuple(value.split("."))
		elif re.match("\d\d(\d\d-){2}\d\d", value):
			year, month, day = tuple(value.split("-"))
		elif re.match("[-_\da-zA-Z]*?@[-_\da-zA-Z]*?\.[-_\da-zA-Z]*$", value):
			return "email"
		else:
			return "text"
		check = True
		day = int(day)
		month = int(month)
		year = int(year)
		if year >= 1970 and year <= 2017:
			if month != 2:
				if (month < 8 and month % 2 == 1) or (month > 7 and month % 2 == 0):
					if day >= 31:
						check = False
				elif day >= 30:
					chack = False
			else:
				if ((year % 4 == 0) and (year % 100 != 0)) or (year % 400 == 0):
					if day >= 29:
						check = False
				elif day >= 28:
					check = False
		if check:
			return 'date'
		# If wrong date, it will be returned as text type
		return 'text'

	def make_query(values):
		items = list()
		for value in values:
			items.append({ value: { '$exists': True } })
		return { "$and": items }

	fields = (request.data.decode("utf-8")).split("&")
	wrong_field = False
	template_found = False
	fields_dict = {}
	for field in fields:
		if not re.match(".*?=.*", field):
			return "Error: wrong request!"
		if re.match(".*?=.*?=", field):
			return "Error: wrong request!"
		
		field_name, field_value = tuple(field.split("="))

		fields_dict[field_name] = value_type(field_value)

		if field_name not in names:
			wrong_field = True
	
	# If we catch at least one field name which is not in names tuple,
	# we return request as field name-value type dictionary
	if wrong_field:
		return str(fields_dict)

	# Get necessary items from database
	import sys
	items = db.inventory.find(make_query(list(fields_dict.keys())))
	'''for item in items:
		print(item, file=sys.stderr)'''
	max_len = 0
	for choosen_item in items:
		if len(choosen_item.keys()) > max_len:
			max_len = len(choosen_item.keys())
			choosen_item.pop("_id")
			result_item = choosen_item

	if max_len != 0: 
		return "Template found: " + str(result_item)
	
	return str(fields_dict)
		
@app.route('/')
def home_page():
	return "<h1>Welcome to the Form templates server! All instructions conclude in READ.me \
			file.</h1>"

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def another_page(path):
	""" Return 404 error for any other pages """
	abort(404)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
