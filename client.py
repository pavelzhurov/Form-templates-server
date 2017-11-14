import requests
import request_generator
import argparse
import re
import json


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Client for forms server')
	parser.add_argument("N", type=int, help="Number of requests, which client will do")
	parser.add_argument("-f", "--file", help="Take all output into file")
	parser.add_argument("-a", "--add_manually", help="Add request manually")
	parser.add_argument("-g", "--generate_database", help="Generate new database before sending \
						requests", action="store_true")
	args = parser.parse_args()
	if args.generate_database:
		answ = requests.get("http://localhost/generate")
		if re.match("<h1>Error occurred while generating database:.*", str(answ.text)):
			with open('generator.log', 'w') as f:
				f.write(str(answ.text))
			raise Exception("Error occurred while generating database!!!\nCheck generator.log file")
		else:
			print("Database created")
	if args.file is not None:
		with open(args.file, 'w') as f:
			pass
	if args.N < 1:
		raise Exception("Wrong N argument! It must be 1 or more")
	for i in range(args.N):
		if args.add_manually is not None and (i == 0):
			request = args.add_manually
		else:
			request = request_generator.generate_request()
		r = requests.post("http://localhost/get_form", data=request)
		found_message = False
		if re.match("Template found: .*", r.text):
			text = re.sub("Template found: (.*)", r"\1", r.text)
			found_message = True
		else:
			text = r.text
		dictionary = json.loads(text.replace("'", '"'))
		content = json.dumps(dictionary, indent=4)
		if args.file is not None:
			try:
				# Get all output to it
				with open(args.file, 'a+') as f:
					f.write("Request nunmber " + str(i) + "\n")
					f.write(request + "\n")
					if found_message:
						f.write("Template was found!" + "\n")
					else:
						f.write("No such template" + "\n")
					f.write(content + "\n")
					f.write("\n")
			except Exception as err:
				raise Exception("Error: something occurred while writing in the file!")
		else:
			print("Request nunmber " + str(i))
			print(request)
			if found_message:
				print("Template was found!")
			else:
				print("No such template")
			print(content)

