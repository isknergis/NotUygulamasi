from flask import Flask, render_template,request,redirect #redirct başka urlye yönlendirme

import sqlite3
app=Flask(__name__)

#veri tabanı oluşturma ve ekleme
def init_db():
	with sqlite3.connect("notlar.db") as database:
		cursor=database.cursor()
		cursor.execute("create table if not exists notes (id integer primary key, content text)")
		database.commit()
#uygulama başlarken veritabanını hazırlayalım.
init_db()

@app.route('/')
def index():
	with sqlite3.connect("notlar.db") as database:
		cursor =database.cursor()
		cursor.execute("select * from notes")
		notes = cursor.fetchall()
	return render_template("index.html", notes=notes)
	
	
	
@app.route('/add', methods=['POST'])
def add_note():
	note_content=request.form.get("note") #formdan not içeriğini al.
	
	with sqlite3.connect("notlar.db") as database:
		cursor=database.cursor()
		cursor.execute("insert into notes(content) values(?)",(note_content,))
		database.commit()
	return redirect ("/")
		
		
@app.route('/delete/<int:id>')
def delete_notes(id):
	with sqlite3.connect("notlar.db") as database:
		cursor=database.cursor()
		cursor=database.cursor()
		cursor.execute("delete from notes where id=?", (id,))
		database.commit()
	return redirect("/")
		
		
		
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_note(id):
    with sqlite3.connect("notlar.db") as database:
        cursor = database.cursor()
        cursor.execute("SELECT content FROM notes WHERE id=?", (id,))
        note = cursor.fetchone()

    if request.method == "POST":
        new_content = request.form.get("note")

        with sqlite3.connect("notlar.db") as database:
            cursor = database.cursor()
            cursor.execute("UPDATE notes SET content=? WHERE id=?", (new_content, id))
            database.commit()

        return redirect("/")

    return render_template("update.html", note=note, id=id)

		
		
if __name__ == "__main__":

	app.run(debug=True)
	
#Eğer with kullanmazsak, veritabanını manuel olarak kapatmalıyız!
#Otomatik kapanma sayesinde hataları önler!
