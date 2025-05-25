from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# 📌 Veritabanını oluştur ve hazırla
def init_db():
    with sqlite3.connect("notlar.db") as database:
        cursor = database.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY, 
                content TEXT, 
                category TEXT
            )
        """)
        database.commit()

init_db()

# 📌 Ana sayfa - Tüm notları listeleme
@app.route('/')
def index():
    with sqlite3.connect("notlar.db") as database:
        cursor = database.cursor()
        cursor.execute("SELECT id, content, category FROM notes")
        notes = cursor.fetchall()
    return render_template("index.html", notes=notes)

# 📌 Genel not ekleme
@app.route('/add', methods=['POST'])
def add_note():
    note_content = request.form.get("note", "").strip()
    note_category = request.form.get("category", "").strip()

    if not note_content or not note_category:
        return redirect("/")

    with sqlite3.connect("notlar.db") as database:
        cursor = database.cursor()
        cursor.execute("INSERT INTO notes(content, category) VALUES(?, ?)", (note_content, note_category))
        database.commit()

    return redirect("/")

# 📌 Not silme
@app.route('/delete/<int:id>')
def delete_notes(id):
    with sqlite3.connect("notlar.db") as database:
        cursor = database.cursor()
        cursor.execute("DELETE FROM notes WHERE id=?", (id,))
        database.commit()
    return redirect("/")

# 📌 Genel not güncelleme (Bu rota, ana sayfadaki notları güncellemek için kullanılır)
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_note(id):
    with sqlite3.connect("notlar.db") as database:
        cursor = database.cursor()
        cursor.execute("SELECT content, category FROM notes WHERE id=?", (id,)) # Kategori bilgisini de çekiyoruz
        note = cursor.fetchone()

    if request.method == "POST":
        new_content = request.form.get("note", "").strip()
        if not new_content:
            return redirect("/")

        with sqlite3.connect("notlar.db") as database:
            cursor = database.cursor()
            cursor.execute("UPDATE notes SET content=? WHERE id=?", (new_content, id))
            database.commit()

        return redirect("/")
    
    # GET isteği için, update.html şablonuna notu ve ID'yi gönderiyoruz
    # note[0] içeriği, note[1] kategoriyi temsil eder
    return render_template("update.html", note=note, id=id)

# 📌 Kategoriye özel not ekleme formu (GET isteği)
@app.route('/add_category/<kategori>', methods=['GET'])
def add_note_form_by_category(kategori):
    # Bu sayfa sadece kategoriye özel not ekleme formunu göstermek içindir.
    # Gönderme işlemi '/add/<kategori>' POST rotasına yapılacak.
    return render_template("add_category.html", kategori=kategori)

# 📌 Kategoriye özel not ekleme (POST isteği)
@app.route('/add/<kategori>', methods=['POST'])
def add_note_by_category(kategori):
    note_content = request.form.get("note", "").strip()

    if not note_content:
        return redirect(f"/category/{kategori}")  # Eğer içerik boşsa kategoriye geri dön

    with sqlite3.connect("notlar.db") as database:
        cursor = database.cursor()
        cursor.execute("INSERT INTO notes(content, category) VALUES(?, ?)", (note_content, kategori))
        database.commit()

    return redirect(f"/category/{kategori}")  # Not eklendikten sonra kategoriye geri dön

# 📌 Kategoriye göre not listeleme
@app.route('/category/<kategori>')
def filter_notes(kategori):
    with sqlite3.connect("notlar.db") as database:
        cursor = database.cursor()
        cursor.execute("SELECT id, content FROM notes WHERE category=?", (kategori,))
        notes = cursor.fetchall()

    return render_template("category.html", notes=notes, kategori=kategori)

# 📌 Kategoriye göre not güncelleme formu (GET isteği)
@app.route('/update_category/<kategori>/<int:id>', methods=['GET'])
def update_note_form_by_category(kategori, id):
    with sqlite3.connect("notlar.db") as database:
        cursor = database.cursor()
        cursor.execute("SELECT content FROM notes WHERE id=? AND category=?", (id, kategori))
        note = cursor.fetchone()
        if not note: # Not bulunamazsa hata sayfasına yönlendirme veya ana sayfaya dönme
            return redirect(f"/category/{kategori}")
    # Bu sayfa sadece kategoriye özel not güncelleme formunu göstermek içindir.
    # Gönderme işlemi '/update/<kategori>/<int:id>' POST rotasına yapılacak.
    return render_template("update_category.html", note=note, id=id, kategori=kategori)

# 📌 Kategoriye göre not güncelleme (POST isteği)
@app.route('/update/<kategori>/<int:id>', methods=['POST'])
def update_note_by_category(kategori, id):
    new_content = request.form.get("note", "").strip()

    if not new_content:
        return redirect(f"/category/{kategori}")  # Eğer içerik boşsa geri dön

    with sqlite3.connect("notlar.db") as database:
        cursor = database.cursor()
        cursor.execute("UPDATE notes SET content=? WHERE id=? AND category=?", (new_content, id, kategori))
        database.commit()

    return redirect(f"/category/{kategori}")  # Güncellemeden sonra kategoriye geri dön

if __name__ == "__main__":
    app.run(debug=True)
