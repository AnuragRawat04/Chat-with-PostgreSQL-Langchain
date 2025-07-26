import psycopg2

# ✅ Connect to PostgreSQL database
connection = psycopg2.connect(
    dbname="Lancgchain",       # Your DB name
    user="postgres",         # Default user for PostgreSQL
    password="",         # Your password
    host="",        # Or IP address if remote
    port=""              # Default PostgreSQL port
)

# ✅ Create a cursor object to run SQL
cursor = connection.cursor()

# ✅ Create the STUDENT table (if not exists)
table_info = """
CREATE TABLE IF NOT EXISTS STUDENT (
    Name VARCHAR(25),
    class VARCHAR(25),
    Section VARCHAR(25),
    Marks INT
)
"""
cursor.execute(table_info)

# ✅ Insert records
cursor.execute("INSERT INTO STUDENT (Name, class, Section, Marks) VALUES ('Alice', '10', 'A', 92)")
cursor.execute("INSERT INTO STUDENT (Name, class, Section, Marks) VALUES ('Bob', '10', 'B', 85)")
cursor.execute("INSERT INTO STUDENT (Name, class, Section, Marks) VALUES ('Charlie', '9', 'A', 78)")
cursor.execute("INSERT INTO STUDENT (Name, class, Section, Marks) VALUES ('Diana', '9', 'C', 88)")
cursor.execute("INSERT INTO STUDENT (Name, class, Section, Marks) VALUES ('Ethan', '11', 'B', 95)")

# ✅ Display records
print("The inserted Records are:")
cursor.execute("SELECT * FROM STUDENT")
rows = cursor.fetchall()
for row in rows:
    print(row)

# ✅ Commit changes and close the connection
connection.commit()
cursor.close()
connection.close()
