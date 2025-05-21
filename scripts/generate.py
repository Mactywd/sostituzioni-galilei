import json
import random

class Sostituzioni:
	def __init__(self, teachers_timetables=None, classes_timetables=None, compresenza=None, religione=None):
		# Teachers timetables
		if teachers_timetables is None:
			with open("resources/teachers_timetables.json", "r") as f:
				self.teachers_timetables = json.load(f)
		else:
			self.teachers_timetables = teachers_timetables
		
		# Classes timetables
		if classes_timetables is None:
			with open("resources/classes_timetables.json", "r") as f:
				self.classes_timetables = json.load(f)
		else:
			self.classes_timetables = classes_timetables

		# Compresenza
		if compresenza is None:
			with open("resources/teachers_compresenza.json", "r") as f:
				self.compresenza = json.load(f)
		else:
			self.compresenza = compresenza
		
		# Religione
		if religione is None:
			with open("resources/teachers_religione.json", "r") as f:
				self.religione = json.load(f)
		else:
			self.religione = religione


	# unused, just load them from file
	# GENERATE PER-CLASS TIMETABLES
	# def compile_timetable(self):
	# 	teachers_timetables = self.teachers_timetables
	# 	classes_timetables = {}
		
	# 	# Loop through all teachers in the nested object
	# 	for teacher, weekdays in teachers_timetables.items():
	# 		for weekday_index, weekday in enumerate(weekdays):
	# 			for class_index, classname in enumerate(weekday):
	# 				print(f"Teacher: {teacher}, Weekday: {weekday_index}, Class: {classname}")
					
	# 				# Add info to the classes timetables
	# 				if classname not in ["R", "C", "D", "P", ""]:
	# 					if classname not in classes_timetables:
	# 						classes_timetables[classname] = [
	# 							["", "", "", "", "", "", "", ""],  # monday
	# 							["", "", "", "", "", "", "", ""],  # tuesday
	# 							["", "", "", "", "", "", "", ""],  # ...
	# 							["", "", "", "", "", "", "", ""],
	# 							["", "", "", "", "", "", "", ""],
	# 							["", "", "", "", "", "", "", ""],
	# 						]
	# 					print(f"Teacher: {teacher}, Classname: {classname}, Weekday index: {weekday_index}, Class index: {class_index}")
	# 					print(classes_timetables[classname][weekday_index][class_index])
	# 					classes_timetables[classname][weekday_index][class_index] = teacher
		
	# 	print(classes_timetables)
	# 	return classes_timetables
	
	def parse_times(self, period_to_convert):
		'''
		convert period to time
		'''

		periods = {
			0: "8:20",
			1: "9:20",
			2: "10:20",
			3: "11:20",
			4: "12:20",
			5: "13:20",
			6: "14:20",
			7: "15:20",
			8: "16:20"
		}

		return periods[period_to_convert]



	def generate_sostituzioni(self, missing_teachers, partially_missing, credits, full_class_trip, partial_class_trip, weekday):
		'''
		missing_teachers: teachers who will be absent the whole day
		partially_missing: teachers who will be absent only for a few periods e.g. {"name": [1, 2, 3]}
		credits: teachers who owe some hours and need to do it back
		weekday: day of the week
		'''

		teachers_timetables = self.teachers_timetables
		classes_timetables = self.classes_timetables
		
		teachers_list = list(teachers_timetables.keys())
		
		late_enter = {} # e.g. {"4L": 1}
		early_exit = {} # e.g. {"3C": 1}
		substitutes = {} # e.g. {"4B": {1: "SELIS PATRIZIA", 2: "SILVESTRI SILVIA"}}
		
		# Get all teachers with: hour at disposition (D) and with hour at payment (P)
		# and teachers whose class is on a school trip

		disposition = [[], [], [], [], [], [], [], []] # one list per period, will be populated with teachers
		payment = [[], [], [], [], [], [], [], []]     # who have hour at disposition or payment
		class_on_trip = [[], [], [], [], [], [], [], []]

		empty_classes = []
		
		print(full_class_trip)
		print(partial_class_trip)
		print(f"{weekday=}")

		# get disposition/payment teachers from timetables
		for teacher in teachers_list:
			classes = teachers_timetables[teacher][weekday]

			for i, classname in enumerate(classes):
				if classname == "D":
					disposition[i].append(teacher)
				elif classname == "P":
					payment[i].append(teacher)

		# get teachers whose class is on a school trip
		missing_classes = full_class_trip + partial_class_trip

		for classname in missing_classes:
			# if class is empty do not generate substitutions
			if classname in full_class_trip:
				empty_classes.append(classname)
			
			for i, teachers in enumerate(classes_timetables[classname][weekday]):
				for teacher in teachers:
					if teacher not in self.compresenza: # make sure its not []
						class_on_trip[i].append(teacher)
			
		


		print(f"Disposition: {disposition}")
		print(f"Payment: {payment}")
		print(f"Class_on_trip: {class_on_trip}")
		print(f"Empty_classes: {empty_classes}")
		print(f"Missing teachers: {missing_teachers}")

		# sort classes_timetables by CLASS ALPHABETICAL ORDER
		classes_timetables = dict(sorted(classes_timetables.items(), key=lambda item: item[0]))

		# Check if each class has a missing teacher
		for classname, weekdays in classes_timetables.items():

			if classname in full_class_trip:
				continue

			periods = weekdays[weekday]
			missing_periods = []
			missing_partial_periods = []
			
			# Find periods whose teacher is absent
			for i, teachers in enumerate(periods):
				absent_num = 0
				
				if teachers == []: # if teachers==[] just skip the rest, they are empty anyways
					break
			
				for teacher in teachers:
					if (teacher in missing_teachers) or\
						((teacher in partially_missing) and (i in partially_missing[teacher])): # consider whole day absences and partial absences
						absent_num += 1

				if absent_num == len(teachers): # if all teachers are absent
					missing_periods.append(i)
				elif absent_num > 0: # must write that the teacher is missing regardless even if its not considered
					missing_partial_periods.append(i)
			
			print(f"{classname=}, {missing_periods=}")


			# Get class' last period
			last_period = i -1 if i > 0 else 0
			print(f"{classname=}, {last_period=}")
			
			if missing_periods:
				########################################
				####   ACTUAL IMPORTANT CODE HERE   ####
				########################################

				# find if class enters late, exits early or needs a substitute and, if the latter, find it.

				# Check if first (and second) period is missing
				if 0 in missing_periods:
					late_enter[classname] = self.parse_times(1)
					missing_periods.remove(0)

					if 1 in missing_periods:
						# check if a class's teacher has a disposition hour at that time
						found_teacher = False
						for teacher in disposition[1]:
							if teacher not in missing_teachers and teacher not in partially_missing:
								# make sure that the class has that teacher
								for school_day in range(len(teachers_timetables[teacher])):
									print(f"{teacher=}, {weekday=}")
									if classname in teachers_timetables[teacher][school_day]:
										substitutes[classname] = {self.parse_times(2): f"{teacher} (D)"}
										disposition[1].remove(teacher)
										found_teacher = True
										missing_periods.remove(1)
										break
						
						if not found_teacher:
							late_enter[classname] = self.parse_times(1)
							missing_periods.remove(1)
				
				# Check if last (and second-last) period is missing
				print(f"{classname=}, {last_period=}, {missing_periods=}")
				if last_period in missing_periods:
					early_exit[classname] = self.parse_times(last_period)
					missing_periods.remove(last_period)

					if (last_period - 1) in missing_periods:
						# check if a class's teacher has a disposition hour at that time
						found_teacher = False
						for teacher in disposition[last_period - 1]:
							if teacher not in missing_teachers and teacher not in partially_missing:
								# make sure that the class has that teacher
								for school_day in range(len(teachers_timetables[teacher])):
									print(f"{teacher=}, {weekday=}")
									if classname in teachers_timetables[teacher][school_day]:
										print("found teacher")
										substitutes[classname] = {self.parse_times(last_period - 1): f"{teacher} (D)"}
										disposition[last_period - 1].remove(teacher)
										found_teacher = True
										missing_periods.remove(last_period - 1)
										break

						if not found_teacher:
							early_exit[classname] = self.parse_times(last_period)
							missing_periods.remove(last_period - 1)
				

				# Check if there are missing periods in the middle
				for i in range(len(missing_periods)):

					period_time = self.parse_times(missing_periods[i])

					'''
					# Check if first period teacher can posticipate their hour
					# get the first teacher that is present (if the class enters late take the second)
					for teachers in classes_timetables[classname][weekday]:
						absent_teachers = 0
						for teacher in teachers:
							if teacher in missing_teachers or teacher in partially_missing:
								absent_teachers += 1
						
						if absent_teachers < len(teachers) - 1:
							break
					
					# check if the teacher is free at that time
					if teachers_timetables[teacher][weekday][missing_periods[i]] == "":
						substitutes[classname] = {period_time: f"{teacher} che posticipa"}
						if teacher in credits:
							credits.remove(teacher)
						late_enter[classname] = self.parse_times(1)
						continue

					# Check if last period teacher can anticipate their hour
					# get the last teacher that is present (if the class exits early take the second last)
					for teachers in classes_timetables[classname][weekday]:
						absent_teachers = 0
						for teacher in teachers:
							if teacher in missing_teachers or teacher in partially_missing:
								absent_teachers += 1
						
						if absent_teachers < len(teachers) - 1:
							break

					# check if the teacher is free at that time
					if teachers_timetables[teacher][weekday][missing_periods[i]] == "":
						substitutes[classname] = {period_time: f"{teacher} che anticipa"}
						if teacher in credits:
							credits.remove(teacher)
						early_exit[classname] = self.parse_times(last_period)
						continue
					'''

					# Check if there is a teacher with a credit hour who is free
					possible_choices = []
					for teacher in credits:
						
						# make sure that it isn't the teacher's free day
						teachers_periods = []
						for period in teachers_timetables[teacher][weekday]:
							if period not in ["", "D", "P", "C", "R"]:
								teachers_periods.append(period)
						if teachers_periods:

							# make sure that he doesn't have a class at that period
							if teachers_timetables[teacher][weekday][missing_periods[i]] == "":

								# make sure he doesn't have to get in earlier but also doesn't have
								# empty periods in the middle
								if teachers_timetables[teacher][weekday][missing_periods[i] - 1] != "":
									possible_choices.append(teacher)

							# it is also fine if the teacher has a payment hour at that time
							if teachers_timetables[teacher][weekday][missing_periods[i]] == "P":
								possible_choices.append(teacher)
								payment[missing_periods[i]].remove(teacher)

					if possible_choices:
						substitute = random.choice(possible_choices)
						if substitutes.get(classname):
							substitutes[classname][period_time] = f"{substitute} (R)"
						else:
							substitutes[classname] = {period_time: f"{substitute} (R)"}
						credits.remove(substitute)

					else: # no teacher with credit is found, look for teachers on a trip
						print(f"{classname=}, {weekday=}, {missing_periods[i]=} no credits")
						possible_choices = []
						for teacher in class_on_trip[missing_periods[i]]:
							if teacher not in missing_teachers and teacher not in partially_missing:
								possible_choices.append(teacher)

						if possible_choices:
							substitute = random.choice(possible_choices)
							if substitutes.get(classname):
								substitutes[classname][period_time] = f"{substitute} (G)"
							else:
								substitutes[classname] = {period_time: f"{substitute} (G)"}
							class_on_trip[missing_periods[i]].remove(substitute)

						else: # no teacher on trip is found, look for disposition
							print(f"{classname=}, {weekday=}, {missing_periods[i]=} no trips")
							possible_choices = []
							for teacher in disposition[missing_periods[i]]:
								if teacher not in missing_teachers and teacher not in partially_missing:
									possible_choices.append(teacher)

							if possible_choices:
								substitute = random.choice(possible_choices)
								if substitutes.get(classname):
									substitutes[classname][period_time] = f"{substitute} (D)"
								else:
									substitutes[classname] = {period_time: f"{substitute} (D)"}
								disposition[missing_periods[i]].remove(substitute)
							
							else: # no teacher with disposition is found, look for payment
								print(f"{classname=}, {weekday=}, {missing_periods[i]=} no disposition")
								possible_choices = []
								for teacher in payment[missing_periods[i]]:
									if teacher not in missing_teachers and teacher not in partially_missing:
										possible_choices.append(teacher)

								if possible_choices:
									substitute = random.choice(possible_choices)
									if substitutes.get(classname):
										substitutes[classname][period_time] = f"{substitute} (P)"
									else:
										substitutes[classname] = {period_time: f"{substitute} (P)"}
									payment[missing_periods[i]].remove(substitute)
								
								else:
									print(f"{classname=}, {weekday=}, {missing_periods[i]=} nothing found")
									if substitutes.get(classname):
										substitutes[classname][period_time] = "soli"
									else:
										substitutes[classname] = {period_time: "soli"}

			# write the teacher that is present as a substitute of the teacher that is missing
			for i in missing_partial_periods:
				period_time = self.parse_times(i)
				teachers = classes_timetables[classname][weekday][i]
				
				teacher = [teacher for teacher in teachers if teacher not in missing_teachers and teacher not in partially_missing]
				teacher = teacher[0]

				if substitutes.get(classname):
					substitutes[classname][period_time] = f"{teacher}"
				else:
					substitutes[classname] = {period_time: f"{teacher}"}

		return {
			"late_enter": late_enter,
			"early_exit": early_exit,
			"substitutes": substitutes
		}


if __name__ == '__main__':
	with open("resources/teachers_timetables.json", "r") as f:
		teachers_timetables = json.load(f)
	with open("resources/classes_timetables.json", "r") as f:
		classes_timetables = json.load(f)


	sostituzioni = Sostituzioni(teachers_timetables, classes_timetables)

	'''generated_sostituzioni = sostituzioni.generate_sostituzioni(
		missing_teachers=["BAIOCCHI FRANCESCA", "CIPRO ANNA", "D'ETTORE ANITA", "DI RISIO IVANA", "MESSINA MANUELA", "MINDT NINA", "SGUERRI ANDREA", "VALENTE BERNARDA"], 
		partially_missing={"COVINO AMALIA": [2, 3, 4]},
		credits=["IMBERGAMO MASSIMO"],
		full_class_trip=["3F"],
		partial_class_trip=["5B", "5F", "5O", "2F"],
		weekday=3
	)'''

	generated_sostituzioni = sostituzioni.generate_sostituzioni(
		missing_teachers=["MASI SILVIA"],
		partially_missing={},
		credits=[],
		full_class_trip=["4I"],
		partial_class_trip=[],
		weekday=0
	)

	with open("output.json", "w") as f:
		json.dump(generated_sostituzioni, f)