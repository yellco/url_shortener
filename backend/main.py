from flask import Flask, render_template, request, redirect
import time, json
from datetime import datetime
import hashlib
import sys
import psycopg2
import validators

with open('./conf/config.json', 'r') as f:
	data = json.loads(f.read())
	user = data['user']
	host = data['host']
	port = data['port']
	database = data['database']

def database_request(req, records = []):
	conn = psycopg2.connect(dbname=database, user=user, host=host, port=port)
	cursor = conn.cursor()
	cursor.execute(req)
	records = cursor.fetchall()

	cursor.close()
	conn.commit()
	conn.close()

	return records

def unique():
# Генерим уникальное значения timestamp
	ts = time.time()
	
	ts = str(ts)
	ts_before = ts[ts.find(".") + 1 : ]
	ts_after = ts[0 : ts.find(".") - 1]
	ts_sum = hex(int(ts_before + ts_after))

	return ts_sum[2 : len(ts_sum)]

app = Flask(__name__)

@app.route('/r/<hashname>')
def red(hashname):
# Метод возвращает ссылку из базы для редиректа на фронте
	link = 'http://yellco.ru' + request.path
	rqst = database_request("select link from links where our_link='{}';".format(link))
	return redirect(rqst[0][0])

@app.route('/api/url')
def url():
	link = request.args.get('link')

    # Проверяем действительно ли ссылка к нам пришла
	if not validators.url(link):
		return "Указана неверная ссылка"

	hashname = unique()[2:8]
	new_url = 'http://yellco.ru/r/' + hashname
	requesttodb = ("select exists(select 1 from links where our_link='{}');".format(new_url))
	requesttodb2 = ("select exists(select 1 from links where link='{}');".format(link))
	if database_request(requesttodb2)[0][0]:
		return database_request("select our_link from links where link='{}';".format(link))[0][0]
	i=0
	while database_request(requesttodb)[0][0]:
		i+=1
		new_url = 'http://yellco.ru/r/' + hashname
		requesttodb = ("select exists(select 1 from links where link='{}');".format(new_url))
		if i==20:
			return 'Проблема с сервером'
	datenow = datetime.now()
	database_request(("insert into links (link, our_link, date) values ('{}', '{}', '{}') returning 1;".format(link, new_url, datenow)))
	return new_url

@app.route('/api/url/links')
def links():
	return database_request("select * from links;")

if __name__ == '__main__':
	app.run()