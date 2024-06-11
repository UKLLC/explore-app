import stylesheet as ss

labels = ["NHS England", "Geospatial", "None", "NHS England, Geospatial"]

label_colours = {
    "NHS England" : str(ss.cyan[0]),
    "Geospatial" : str(ss.green[0]),
    "None" : str(ss.peach[0]),
    "NHS England, Geospatial": str(ss.lime[0]),
    }
print("debug 2")
print([x for x in labels])

print(label_colours["NHS England"])
colours = [label_colours[x] for x in labels]
print("debug: ",colours)