import mysql.connector

cnx = mysql.connector.connect(user='root', password='ubuntu2020', database="crashes_2015")
cursor = cnx.cursor()

cursor.execute("SHOW TABLES")
for x in cursor:
    print(x)

cursor.execute("delete from accidents")
for x in cursor:
    print(x)

accident = {
    "status": "Final",
    "weekday": "Friday",
    "day": 2,
    "month": 1,
    "year": 2015,
    "aircraft_type": "Saab 340B",
    "operator": "Flybe",
    "country": "United Kingdom",
    "location": "Stornoway's Airport (SYY)"
}

# keys, values = zip(*accident.items())
# keys, values = list(keys), list(values)
# keys.append("id")
# values.append(None)
# temp = ", ".join(['%s'] * len(keys))
# keys = ", ".join(keys)
#
# #
# # values = [f"'{x}'" for x in accident.values()]
# # values = ", ".join(values + ["NULL"])
#
# sql_command = f"INSERT INTO accidents ({keys}) VALUES ({temp})"
# print(sql_command)
# cursor.execute(sql_command, values)

cursor.execute("select * from accidents")
for x in cursor:
    print(x)

cursor.close()
cnx.close()
