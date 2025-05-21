from flask import Flask, render_template
from flask import request
import json
from scripts.generate import Sostituzioni
from scripts.parse_data import parse_data


with open("resources/parsed_names.json", "r") as f:
    teachernames = json.load(f)
with open("resources/parsed_classnames.json", "r") as f:
    classnames = json.load(f)


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/api/get_sostituzioni", methods=["POST"])
def get_sostituzioni():
    
    data = request.get_json()
    absent_full_day = data.get("absent_full_day")
    absent_some_periods = data.get("absent_some_periods")
    credit_list = data.get("credit_list")
    class_trips = data.get("class_trips")
    weekday = data.get("weekday")

    # Process the data as needed
    missing_teachers = []
    for absent in absent_full_day:
        teacher_name = teachernames[absent-1]["name"]
        missing_teachers.append(teacher_name)
    
    partially_missing = {}
    for absent in absent_some_periods:
        teacher_name = teachernames[absent["teacherId"]-1]["name"]
        partially_missing[teacher_name] = [period-1 for period in absent["periods"]]
    
    credits = []
    for credit in credit_list:
        teacher_name = teachernames[int(credit["teacherId"])-1]["name"]
        credits.append(teacher_name)
    
    full_class_trips = []
    partial_class_trips = []
    for trip in class_trips:
        if trip["tripType"] == "full-class":
            class_name = classnames[trip["classId"]-1]["name"]
            full_class_trips.append(class_name)
        else:
            class_name = classnames[trip["classId"]-1]["name"]
            partial_class_trips.append(class_name)

    print(weekday)
    numeric_weekday = int(weekday) - 1

    with open("data.json", "w") as f:
        json.dump({
            "missing_teachers": missing_teachers,
            "partially_missing": partially_missing,
            "credits": credits,
            "full_class_trips": full_class_trips,
            "partial_class_trips": partial_class_trips,
            "weekday": weekday
        }, f, indent=4)
    
    # Call the Sostituzioni class to generate substitutions
    sostituzioni = Sostituzioni()
    result = sostituzioni.generate_sostituzioni(
        missing_teachers=missing_teachers,
        partially_missing=partially_missing,
        credits=credits,
        full_class_trip=full_class_trips,
        partial_class_trip=partial_class_trips,
        weekday=numeric_weekday,
    )

    # Parse the result into a string
    parsed_result = parse_data(result)

    parsed_string = "&".join(parsed_result)

    return json.dumps(parsed_string)

@app.route('/results')
def results():
    return render_template('output.html')

if __name__ == '__main__':
    app.run(debug=True)
