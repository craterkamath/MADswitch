from flask.wrappers import Request
from app import app
from flask import flash, render_template, jsonify, request, redirect
from datetime import datetime, timedelta
import random
import csv


# Class in-memory DB
NUM_CLASSES = 100
validated = False
class_list = ["maths", "english", "hindi", "english", "economics", "biology"]
grade_list = [5, 6, 7, 8, 9, 10, 11, 12]
class_db = []
TS_template = '%b %d %Y %I:%M%p'
comments_db = [
	("Jithin C Nedumala", datetime.strptime('Jun 12 2021  1:33PM', '%b %d %Y %I:%M%p').strftime(TS_template),
	"Hello Everyone, I want to congratulate the old fellow team for all the phenomenal work they have done. My wishes are with the cohort of 2021-22!"),
	("Mannat Anand",datetime.strptime('Jul 08 2021  5:10PM', '%b %d %Y %I:%M%p').strftime(TS_template),
	"If anyone is interested in being part of our snapchat campaign and want to contribute by making videos please reach out to mannat@makeadiff.in. Thank you.")
]

for id in range(NUM_CLASSES):
	tmp = datetime.now() + timedelta(days=id * 4)
	class_db.append({
		"id":id,
		"title": random.choice(class_list),
		"url":"/ask-help?id=" + str(id),
		"sub": "noneed " + str(id),
		"class": "event",
		"grade": random.choice(grade_list),
		"start": tmp.timestamp() * 1000,
		"end": (tmp + timedelta(hours = 1)).timestamp() * 1000
	})


@app.route('/', methods=['GET', 'POST'])
def home():
	if validated == False:
		return redirect("/login", code=302)
	return render_template('index.html')

@app.route('/login')
def login():
	global validated
	validated = True
	return render_template('login.html')

@app.route("/caremore")
def reroute():
	if validated == False:
		return redirect("/login", code=302)
	name = request.args.get("name")
	comment = request.args.get("comment")
	comments_db.append((name, datetime.now().strftime(TS_template), comment))
	print(comments_db)
	return redirect("/", code=302)

@app.route("/resource-central")
def fetchComments():
	if validated == False:
		return redirect("/login", code=302)
	return render_template("resource_central.html", db = comments_db)

@app.route('/offerhelp')
def helppage():
	output = []
	with open("DATA_SHEET.csv", "r") as db_file:
		reader = csv.reader(db_file)
		_ = next(reader)
		for row in reader:
			output.append(row)
	
	return render_template('search.html', db = output)

@app.route('/substitution')
def subpage():
	if validated == False:
		return redirect("/login", code=302)
	return render_template('calendar_events.html')

@app.route('/calendar-events')
def calendar_events():
	resp = jsonify({'success' : 1, 'result' : [ item for item in class_db ]})
	resp.status_code = 200
	return resp

@app.route('/ask-help')
def view_class_for_sub():
	id_val = int(request.args.get("id"))
	data = class_db[id_val]
	return render_template("reserve_popup.html", name=data["grade"],
							timings = "{} to {}".format(datetime.fromtimestamp(data["start"]/1000).strftime('%H:%M'), datetime.fromtimestamp(data["end"]/1000).strftime('%H:%M')),
							id=id_val)

@app.route('/get-help', methods=['POST'])
def set_class_for_sub():
	sub_val = request.form["sub"]
	if "noneed" in sub_val:
		id_val = int(sub_val.split(" ")[-1])
		class_db[id_val]["sub"] = "noneed " + str(id_val)
		class_db[id_val]["class"] = "event"
	else:
		id_val = int(sub_val.split(" ")[-1])
		class_db[id_val]["sub"] = "need " + str(id_val)
		class_db[id_val]["class"] = "event-important"
	uploaded_file = request.files['filename']
	if uploaded_file.filename != '':
		uploaded_file.save(uploaded_file.filename)
	return "<body style='overflow:hidden;'><img src='static/img/kid_img.jpg')></img></body>"


@app.route('/logout')
def logout():
	validated = False
	return redirect("/login", code=302)

if __name__ == "__main__":
    app.run(debug=True)