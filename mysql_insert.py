import mysql.connector

cnx = mysql.connector.connect(user='root', password='ubuntu2020', database="crashes_2015")
cursor = cnx.cursor()

cursor.execute("SHOW TABLES")
for x in cursor:
    print(x)

cursor.execute("select * from crashes")
for x in cursor:
    print(x)
#
# accident = {
#     "status": "Final",
#     "date": "2015-01-02",
#     "aircraft_type": "Saab 340B",
#     "operator": "Flybe",
#     "location": "Stornoway Airport (SYY) (  \u00a0  United Kingdom ) \r\n"
# }
#
# keys = ", ".join(list(accident.keys()) + ["id"])
# values = [f"'{x}'" for x in accident.values()]
# values = ", ".join(values + ["NULL"])
#
# sql_command = f"INSERT INTO crashes ({keys}) VALUES ({values})"
# print(sql_command)
# cursor.execute(sql_command)
#
# cursor.execute("select * from crashes")
# for x in cursor:
#     print(x)

cursor.close()
cnx.close()
