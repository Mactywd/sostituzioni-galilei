import json

def compile_timetable(teachers_timetables):
    teachers_timetables = teachers_timetables
    classes_timetables = {}
    
    # Loop through all teachers in the nested object
    for teacher, weekdays in teachers_timetables.items():
        for weekday_index, weekday in enumerate(weekdays):
            for class_index, classname in enumerate(weekday):
                print(f"Teacher: {teacher}, Weekday: {weekday_index}, Class: {classname}")
                
                # Add info to the classes timetables
                if classname not in ["R", "C", "D", "P", ""]:
                    if classname not in classes_timetables:
                        classes_timetables[classname] = [
                            ["", "", "", "", "", "", "", ""],  # monday
                            ["", "", "", "", "", "", "", ""],  # tuesday
                            ["", "", "", "", "", "", "", ""],  # ...
                            ["", "", "", "", "", "", "", ""],
                            ["", "", "", "", "", "", "", ""],
                            ["", "", "", "", "", "", "", ""],
                        ]
                    print(f"Teacher: {teacher}, Classname: {classname}, Weekday index: {weekday_index}, Class index: {class_index}")
                    print(classes_timetables[classname][weekday_index][class_index])
                    classes_timetables[classname][weekday_index][class_index] = teacher
    
    print(classes_timetables)
    return classes_timetables

if __name__ == "__main__":
    with open("resources/teachers_timetables.json", "r") as f:
        teachers_timetables = json.load(f)

    classes_timetables = compile_timetable(teachers_timetables)
    with open("resources/classes_timetables.json", "w") as f:
        json.dump(classes_timetables, f, indent=4)