#!/usr/bin/env python
# encoding: utf-8

import sqlite3

db = 'cameras.sqlite'

conn = sqlite3.connect(db)
c = conn.cursor()
cameras = c.execute('select * from cameras order by make')
print "Columns: ", c.description

insert_sql = """INSERT INTO cameras (make, model, ccd_width, type) VALUES (?, ?, ?, ?)"""
insert = False
if insert:
	#values = ['Microsoft', 'XBox Live Vision', 5.08, '1/3.2']
	values = ['Logitech', 'C510', '4.25', '1/3.6"']
	c.execute(insert_sql, values)
	conn.commit()
for camera in cameras:
	print camera

