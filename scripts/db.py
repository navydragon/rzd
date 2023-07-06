import sqlite3

conn = sqlite3.connect('database.db')

c = conn.cursor()
c.execute(
    '''CREATE TABLE IF NOT EXISTS cargo_variants (id INTEGER PRIMARY KEY AUTOINCREMENT, variant text, name text, path text, description text)''')

# c = conn.cursor()
# c.execute(
#     ''' DROP TABLE IF EXISTS cargo_variants'''
# )

c = conn.cursor()
c.execute(
    "INSERT INTO cargo_variants (variant,name,path,description) VALUES ('Фин.план','Фин. план базовый', '/data/initial/fin_pan.xlxs','...')")
conn.commit()

conn.close()
