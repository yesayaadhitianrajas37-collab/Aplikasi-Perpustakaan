from flask import Flask, render_template, request, redirect, url_for, flash
import uuid

app = Flask(__name__)
app.secret_key = "secret_perpus_uas"

# In-memory "database"
books = []
log_stack = []  # Stack for admin activity

# -------------------------
# ALGORITMA: BUBBLE SORT
# -------------------------
def bubble_sort_by_title(data):
    arr = data.copy()
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j]["title"].lower() > arr[j+1]["title"].lower():
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

# -------------------------
# ALGORITMA: LINEAR SEARCH
# -------------------------
def linear_search_by_keyword(data, keyword):
    k = keyword.lower()
    return [b for b in data if k in b["title"].lower() or k in b["author"].lower()]

# -------------------------
# ROUTES
# -------------------------

@app.route("/")
def index():
    latest = books[-5:][::-1]
    return render_template("index.html", latest=latest)


@app.route("/books")
def list_books():
    return render_template("books.html", books=books)


@app.route("/add", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        year = request.form.get("year", "").strip()

        if not title:
            flash("Judul buku wajib diisi.", "danger")
            return redirect(url_for("add_book"))

        new_book = {
            "id": str(uuid.uuid4()),
            "title": title,
            "author": author,
            "year": year,
            "status": "Tersedia"
        }
        books.append(new_book)
        log_stack.append(f"Tambah buku: {title}")
        flash("Buku berhasil ditambahkan.", "success")
        return redirect(url_for("list_books"))

    return render_template("form.html", action="Tambah", book=None)


@app.route("/edit/<book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        flash("Buku tidak ditemukan.", "warning")
        return redirect(url_for("list_books"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        year = request.form.get("year", "").strip()

        if not title:
            flash("Judul buku wajib diisi.", "danger")
            return redirect(url_for("edit_book", book_id=book_id))

        old_title = book["title"]
        book["title"] = title
        book["author"] = author
        book["year"] = year

        log_stack.append(f"Edit buku: {old_title} -> {title}")
        flash("Buku berhasil diperbarui.", "success")
        return redirect(url_for("list_books"))

    return render_template("form.html", action="Edit", book=book)


@app.route("/delete/<book_id>", methods=["POST"])
def delete_book(book_id):
    global books
    book = next((b for b in books if b["id"] == book_id), None)

    if book:
        books = [b for b in books if b["id"] != book_id]
        log_stack.append(f"Hapus buku: {book['title']}")
        flash("Buku berhasil dihapus.", "success")
    else:
        flash("Buku tidak ditemukan.", "warning")

    return redirect(url_for("list_books"))


# -------------------------
# PEMINJAMAN BUKU
# -------------------------
@app.route("/borrow/<book_id>")
def borrow_book(book_id):
    book = next((b for b in books if b["id"] == book_id), None)

    if not book:
        flash("Buku tidak ditemukan.", "warning")
        return redirect(url_for("list_books"))

    if book["status"] == "Dipinjam":
        flash("Buku ini sudah dipinjam.", "danger")
        return redirect(url_for("list_books"))

    book["status"] = "Dipinjam"
    log_stack.append(f"Peminjaman buku: {book['title']}")
    flash("Buku berhasil dipinjam.", "success")
    return redirect(url_for("list_books"))


# -------------------------
# PENGEMBALIAN BUKU
# -------------------------
@app.route("/return/<book_id>")
def return_book(book_id):
    book = next((b for b in books if b["id"] == book_id), None)

    if not book:
        flash("Buku tidak ditemukan.", "warning")
        return redirect(url_for("list_books"))

    if book["status"] == "Tersedia":
        flash("Buku ini belum dipinjam.", "info")
        return redirect(url_for("list_books"))

    book["status"] = "Tersedia"
    log_stack.append(f"Pengembalian buku: {book['title']}")
    flash("Buku berhasil dikembalikan.", "success")
    return redirect(url_for("list_books"))


@app.route("/search", methods=["GET", "POST"])
def search():
    results = []
    keyword = ""
    if request.method == "POST":
        keyword = request.form.get("keyword", "").strip()
        if keyword:
            results = linear_search_by_keyword(books, keyword)
            log_stack.append(f"Pencarian: {keyword}")
        else:
            flash("Masukkan kata kunci pencarian.", "warning")

    return render_template("search.html", results=results, keyword=keyword)


@app.route("/sorted")
def sorted_view():
    sorted_books = bubble_sort_by_title(books)
    log_stack.append("Mengurutkan data buku (bubble sort).")
    return render_template("sorted.html", books=sorted_books)


@app.route("/log")
def show_log():
    return render_template("log.html", log=log_stack[::-1])


# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    if not books:
        sample = [
            {"id": str(uuid.uuid4()), "title": "Pemrograman Python", "author": "Andi", "year": "2020", "status": "Tersedia"},
            {"id": str(uuid.uuid4()), "title": "Algoritma & Struktur Data", "author": "Budi", "year": "2019", "status": "Tersedia"},
            {"id": str(uuid.uuid4()), "title": "Basis Data", "author": "Citra", "year": "2018", "status": "Tersedia"},
        ]
        books.extend(sample)

    app.run(debug=True)
