import json

def parse_data(data):
    """
    Parse the output of the generate_sostituzioni function and return a dictionary with the parsed data.
    
    Example data:
    { 
        "late_enter": {"3I": "9:20", ...},
        "early_exit": {"3I": "12:20", ...},
        "substitutions": {
            "3I": {"9:20": "VALENTINI (D), "10:20": "PARIGI (P)", ...},
            ...
                
    }

    Example output:
    3I: la classe entra alle 9:20, ore 9:20 con prof. Valentini (D), ore 10:20 con prof. Parigi (P), la classe esce alle 12:20
    4F: ...
    """

    parsed_strings = []
    per_class_substitutions = {}

    # Check late enters
    for class_name, count in data["late_enter"].items():
        if class_name in per_class_substitutions.keys():
            per_class_substitutions[class_name]["late_enter"] = count
        else:
            per_class_substitutions[class_name] = {"late_enter": count}

    # Check early exits
    for class_name, count in data["early_exit"].items():
        if class_name in per_class_substitutions.keys():
            per_class_substitutions[class_name]["early_exit"] = count
        else:
            per_class_substitutions[class_name] = {"early_exit": count}
    
    # Check substitutions
    for class_name, substitutions in data["substitutes"].items():
        if class_name in per_class_substitutions.keys():
            per_class_substitutions[class_name]["substitutions"] = substitutions
        else:
            per_class_substitutions[class_name] = {"substitutions": substitutions}
    
    
    # Sort the classes dictionary by class name
    per_class_substitutions = {key: per_class_substitutions[key] for key in sorted(per_class_substitutions.keys())}

    # Create the output string
    for class_name in per_class_substitutions:
        class_data = per_class_substitutions[class_name]
        output = f"{class_name}: "
        
        if "late_enter" in class_data:
            output += f"la classe entra alle ore {class_data['late_enter']}, "
        
        if "substitutions" in class_data:
            for time, prof in class_data["substitutions"].items():
                output += f"ore {time} con prof. {prof}, "
        
        if "early_exit" in class_data:
            output += f"la classe esce alle {class_data['early_exit']}, "

        # Remove the last comma and space and add a period
        output = output.rstrip(", ") + "."
        parsed_strings.append(output)

    print("Parsed strings:")
    for parsed_string in parsed_strings:
        print(parsed_string)
        print("")
    return parsed_strings
        



if __name__ == "__main__":
    with open("output.json", "r") as f:
        example_data = json.load(f)
    
    with open("parsed_output.txt", "w") as f:
        f.write("\n".join(parse_data(example_data)))