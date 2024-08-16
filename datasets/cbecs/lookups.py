# PBA
enumeration = """
1=Vacant
2=Office
4=Laboratory
5=Nonrefrigerated warehouse
6=Food sales
7=Public order and safety
8=Outpatient health care
11=Refrigerated warehouse
12=Religious worship
13=Public assembly
14=Education
15=Food service
16=Inpatient health care
17=Nursing
18=Lodging
23=Strip shopping center
24=Enclosed mall
25=Retail other than mall
26=Service
91=Other
"""

# Convert the enumeration to a dictionary
lookup_pba = {int(item.split("=")[0]): item.split("=")[1] for item in enumeration.strip().split("\n")}

# Print the dictionary
print(lookup_pba)


# PUBCLIM 
enumeration = """
1=Cold or very cold
2=Cool
3=Mixed mild
4=Warm
5=Hot or very hot
7=Withheld for confidentiality
"""
lookup_climate_zone = {int(item.split("=")[0]): item.split("=")[1] for item in enumeration.strip().split("\n")}
