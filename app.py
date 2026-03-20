from flask import Flask, request, redirect
import mysql.connector

app = Flask(__name__)

# CONNECT TO MYSQL
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",   # put your MySQL password here
        database="library_db"
    )

# SHARED CSS - applies to every page
STYLE = """
<style>
    body { font-family: Arial, sans-serif; background: #f0f0f0; margin: 0; }
    nav { background: #2c3e50; padding: 14px 24px; display: flex; gap: 16px; align-items: center; }
    nav a { color: white; text-decoration: none; font-size: 14px; }
    nav a:hover { text-decoration: underline; }
    nav .brand { font-weight: bold; font-size: 16px; margin-right: 16px; }
    .container { max-width: 1000px; margin: 30px auto; padding: 0 20px; }
    .card { background: white; border-radius: 8px; padding: 24px; margin-bottom: 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }
    h1 { font-size: 22px; margin-bottom: 20px; }
    .btn { display: inline-block; padding: 8px 16px; border-radius: 6px; border: none; cursor: pointer; font-size: 13px; text-decoration: none; }
    .btn-blue  { background: #2980b9; color: white; }
    .btn-green { background: #27ae60; color: white; }
    .btn-red   { background: #e74c3c; color: white; }
    .btn-gray  { background: #95a5a6; color: white; }
    .btn:hover { opacity: 0.85; }
    table { width: 100%; border-collapse: collapse; font-size: 13px; }
    th { background: #f8f8f8; text-align: left; padding: 10px 12px; border-bottom: 2px solid #e0e0e0; font-size: 12px; color: #555; text-transform: uppercase; }
    td { padding: 10px 12px; border-bottom: 1px solid #f0f0f0; vertical-align: middle; }
    tr:hover td { background: #fafafa; }
    .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
    .form-group { display: flex; flex-direction: column; gap: 5px; }
    label { font-size: 12px; font-weight: bold; color: #555; }
    input { padding: 8px 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 13px; width: 100%; }
    input:focus { outline: none; border-color: #2980b9; }
    select { padding: 8px 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 13px; }
    .alert-green { background: #d4edda; color: #155724; padding: 10px 14px; border-radius: 6px; margin-bottom: 16px; }
    .alert-red   { background: #f8d7da; color: #721c24; padding: 10px 14px; border-radius: 6px; margin-bottom: 16px; }
    .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
    .stat { background: white; border-radius: 8px; padding: 20px; text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }
    .stat-number { font-size: 32px; font-weight: bold; }
    .stat-label  { font-size: 12px; color: #888; margin-top: 4px; }
</style>
"""

# NAV BAR - appears on every page
NAV = """
<nav>
    <span class="brand">Library</span>
    <a href="/">Dashboard</a>
    <a href="/books">All Books</a>
    <a href="/add">Add Book</a>
    <a href="/search">Search</a>
</nav>
"""

# DASHBOARD PAGE
@app.route("/")
def index():
    conn = get_db()
    cur  = conn.cursor(dictionary=True)
    cur.execute("SELECT COUNT(*) AS v FROM books")
    total = cur.fetchone()["v"]
    cur.execute("SELECT COALESCE(SUM(quantity), 0) AS v FROM books")
    copies = cur.fetchone()["v"]
    cur.execute("SELECT COALESCE(SUM(available), 0) AS v FROM books")
    available = cur.fetchone()["v"]
    cur.execute("SELECT COUNT(*) AS v FROM books WHERE available = 0")
    out_of_stock = cur.fetchone()["v"]
    cur.execute("SELECT * FROM books ORDER BY book_id DESC LIMIT 5")
    recent = cur.fetchall()
    cur.close()
    conn.close()

    rows = ""
    for b in recent:
        rows += "<tr>"
        rows += "<td>#" + str(b['book_id']) + "</td>"
        rows += "<td><b>" + b['title'] + "</b></td>"
        rows += "<td>" + b['author'] + "</td>"
        rows += "<td>" + b['category'] + "</td>"
        rows += "<td>" + str(b['available']) + "</td>"
        rows += "<td>"
        rows += "<a href='/edit/" + str(b['book_id']) + "' class='btn btn-blue' style='font-size:12px;padding:5px 10px;margin-right:4px'>Edit</a>"
        rows += "<a href='/delete/" + str(b['book_id']) + "' class='btn btn-red' style='font-size:12px;padding:5px 10px' onclick=\"return confirm('Delete this book?')\">Delete</a>"
        rows += "</td></tr>"

    page = STYLE + NAV + "<div class='container'>"
    page += "<h1>Dashboard</h1>"
    page += "<div class='stats'>"
    page += "<div class='stat'><div class='stat-number'>" + str(total) + "</div><div class='stat-label'>Total Titles</div></div>"
    page += "<div class='stat'><div class='stat-number'>" + str(copies) + "</div><div class='stat-label'>Total Copies</div></div>"
    page += "<div class='stat'><div class='stat-number' style='color:#2980b9'>" + str(available) + "</div><div class='stat-label'>Available</div></div>"
    page += "<div class='stat'><div class='stat-number' style='color:#e74c3c'>" + str(out_of_stock) + "</div><div class='stat-label'>Out of Stock</div></div>"
    page += "</div>"
    page += "<div class='card'>"
    page += "<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:16px'>"
    page += "<b>Recent Additions</b>"
    page += "<a href='/add' class='btn btn-green'>+ Add Book</a>"
    page += "</div>"
    page += "<table><thead><tr><th>ID</th><th>Title</th><th>Author</th><th>Category</th><th>Available</th><th>Actions</th></tr></thead>"
    page += "<tbody>" + rows + "</tbody></table>"
    page += "</div></div>"
    return page


# ALL BOOKS PAGE
@app.route("/books")
def books():
    conn = get_db()
    cur  = conn.cursor(dictionary=True)
    page_num = max(1, request.args.get("page", 1, type=int))
    per_page = 8
    offset   = (page_num - 1) * per_page
    sort = request.args.get("sort", "title")
    if sort not in ["title", "author", "category", "book_id", "available"]:
        sort = "title"
    cur.execute("SELECT COUNT(*) AS v FROM books")
    total = cur.fetchone()["v"]
    total_pages = max(1, -(-total // per_page))
    cur.execute("SELECT * FROM books ORDER BY " + sort + " ASC LIMIT %s OFFSET %s", (per_page, offset))
    all_books = cur.fetchall()
    cur.close()
    conn.close()

    rows = ""
    for b in all_books:
        rows += "<tr>"
        rows += "<td>#" + str(b['book_id']) + "</td>"
        rows += "<td><b>" + b['title'] + "</b></td>"
        rows += "<td>" + b['author'] + "</td>"
        rows += "<td>" + b['category'] + "</td>"
        rows += "<td>" + str(b['publisher'] or "") + "</td>"
        rows += "<td>" + str(b['year'] or "") + "</td>"
        rows += "<td>" + str(b['quantity']) + "</td>"
        rows += "<td>" + str(b['available']) + "</td>"
        rows += "<td>"
        rows += "<a href='/edit/" + str(b['book_id']) + "' class='btn btn-blue' style='font-size:12px;padding:5px 10px;margin-right:4px'>Edit</a>"
        rows += "<a href='/delete/" + str(b['book_id']) + "' class='btn btn-red' style='font-size:12px;padding:5px 10px' onclick=\"return confirm('Delete this book?')\">Delete</a>"
        rows += "</td></tr>"

    pag = "Page " + str(page_num) + " of " + str(total_pages) + " &nbsp; "
    for p in range(1, total_pages + 1):
        color = "#2980b9" if p == page_num else "#ccc"
        pag += "<a href='/books?sort=" + sort + "&page=" + str(p) + "' style='padding:4px 10px;margin:0 2px;background:" + color + ";color:white;border-radius:4px;text-decoration:none;font-size:12px'>" + str(p) + "</a>"

    t_sel  = "selected" if sort == "title"     else ""
    a_sel  = "selected" if sort == "author"    else ""
    c_sel  = "selected" if sort == "category"  else ""
    av_sel = "selected" if sort == "available" else ""

    page = STYLE + NAV + "<div class='container'>"
    page += "<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:20px'>"
    page += "<h1 style='margin:0'>All Books</h1>"
    page += "<div style='display:flex;gap:8px;align-items:center'>"
    page += "<select onchange=\"window.location='/books?sort='+this.value\">"
    page += "<option value='title' "     + t_sel  + ">Sort: Title</option>"
    page += "<option value='author' "    + a_sel  + ">Sort: Author</option>"
    page += "<option value='category' "  + c_sel  + ">Sort: Category</option>"
    page += "<option value='available' " + av_sel + ">Sort: Available</option>"
    page += "</select>"
    page += "<a href='/add' class='btn btn-green'>+ Add Book</a>"
    page += "</div></div>"
    page += "<div class='card' style='padding:0;overflow:hidden'>"
    page += "<table><thead><tr><th>ID</th><th>Title</th><th>Author</th><th>Category</th><th>Publisher</th><th>Year</th><th>Qty</th><th>Available</th><th>Actions</th></tr></thead>"
    page += "<tbody>" + rows + "</tbody></table>"
    page += "<div style='padding:12px 16px;border-top:1px solid #f0f0f0;text-align:right'>" + pag + "</div>"
    page += "</div></div>"
    return page


# ADD BOOK PAGE
@app.route("/add", methods=["GET", "POST"])
def add_book():
    msg = ""
    if request.method == "POST":
        title     = request.form["title"].strip()
        author    = request.form["author"].strip()
        category  = request.form["category"].strip()
        isbn      = request.form["isbn"].strip()
        publisher = request.form["publisher"].strip()
        year      = request.form["year"].strip()
        quantity  = request.form["quantity"].strip()

        if not title or not author or not category or not isbn or not quantity.isdigit() or int(quantity) < 1:
            msg = "<div class='alert-red'>Please fill in all required fields correctly.</div>"
        else:
            conn = get_db()
            cur  = conn.cursor(dictionary=True)
            cur.execute("SELECT book_id FROM books WHERE isbn = %s", (isbn,))
            if cur.fetchone():
                msg = "<div class='alert-red'>A book with this ISBN already exists.</div>"
            else:
                cur.execute(
                    "INSERT INTO books (title, author, category, isbn, publisher, year, quantity, available) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    (title, author, category, isbn, publisher,
                     int(year) if year.isdigit() else None,
                     int(quantity), int(quantity))
                )
                conn.commit()
                msg = "<div class='alert-green'>Book added successfully!</div>"
            cur.close()
            conn.close()

    page = STYLE + NAV + "<div class='container'>"
    page += "<h1>Add New Book</h1>" + msg
    page += "<div class='card'><form method='POST'>"
    page += "<div class='form-row'>"
    page += "<div class='form-group'><label>Book Title *</label><input type='text' name='title' placeholder='e.g. Clean Code' required></div>"
    page += "<div class='form-group'><label>Author *</label><input type='text' name='author' placeholder='e.g. Robert C. Martin' required></div>"
    page += "</div>"
    page += "<div class='form-row'>"
    page += "<div class='form-group'><label>Category *</label><input type='text' name='category' placeholder='e.g. Computer Science' required></div>"
    page += "<div class='form-group'><label>ISBN *</label><input type='text' name='isbn' placeholder='e.g. 978-0132350884' required></div>"
    page += "</div>"
    page += "<div class='form-row'>"
    page += "<div class='form-group'><label>Publisher</label><input type='text' name='publisher' placeholder='e.g. Prentice Hall'></div>"
    page += "<div class='form-group'><label>Year</label><input type='number' name='year' placeholder='e.g. 2008'></div>"
    page += "</div>"
    page += "<div class='form-row'>"
    page += "<div class='form-group'><label>Quantity *</label><input type='number' name='quantity' placeholder='e.g. 5' min='1' required></div>"
    page += "</div>"
    page += "<div style='display:flex;gap:8px;padding-top:16px;border-top:1px solid #f0f0f0'>"
    page += "<button type='submit' class='btn btn-green'>Add Book</button>"
    page += "<button type='reset'  class='btn btn-gray'>Clear</button>"
    page += "<a href='/books'      class='btn btn-gray'>Cancel</a>"
    page += "</div></form></div></div>"
    return page


# EDIT BOOK PAGE
@app.route("/edit/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    conn = get_db()
    cur  = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
    book = cur.fetchone()
    if not book:
        return redirect("/books")

    msg = ""
    if request.method == "POST":
        title     = request.form["title"].strip()
        author    = request.form["author"].strip()
        category  = request.form["category"].strip()
        isbn      = request.form["isbn"].strip()
        publisher = request.form["publisher"].strip()
        year      = request.form["year"].strip()
        quantity  = request.form["quantity"].strip()
        available = request.form["available"].strip()

        if not title or not author or not category or not quantity.isdigit() or int(quantity) < 1:
            msg = "<div class='alert-red'>Please fill in all required fields correctly.</div>"
        elif available.isdigit() and int(available) > int(quantity):
            msg = "<div class='alert-red'>Available cannot be more than quantity.</div>"
        else:
            cur.execute(
                "UPDATE books SET title=%s, author=%s, category=%s, isbn=%s, publisher=%s, year=%s, quantity=%s, available=%s WHERE book_id=%s",
                (title, author, category, isbn, publisher,
                 int(year) if year.isdigit() else None,
                 int(quantity),
                 int(available) if available.isdigit() else 0,
                 book_id)
            )
            conn.commit()
            cur.close()
            conn.close()
            return redirect("/books")

    cur.close()
    conn.close()

    page = STYLE + NAV + "<div class='container'>"
    page += "<h1>Edit Book #" + str(book['book_id']) + "</h1>" + msg
    page += "<div class='card'><form method='POST'>"
    page += "<div class='form-row'>"
    page += "<div class='form-group'><label>Book Title *</label><input type='text' name='title' value='" + book['title'] + "' required></div>"
    page += "<div class='form-group'><label>Author *</label><input type='text' name='author' value='" + book['author'] + "' required></div>"
    page += "</div>"
    page += "<div class='form-row'>"
    page += "<div class='form-group'><label>Category *</label><input type='text' name='category' value='" + book['category'] + "' required></div>"
    page += "<div class='form-group'><label>ISBN</label><input type='text' name='isbn' value='" + book['isbn'] + "'></div>"
    page += "</div>"
    page += "<div class='form-row'>"
    page += "<div class='form-group'><label>Publisher</label><input type='text' name='publisher' value='" + str(book['publisher'] or '') + "'></div>"
    page += "<div class='form-group'><label>Year</label><input type='number' name='year' value='" + str(book['year'] or '') + "'></div>"
    page += "</div>"
    page += "<div class='form-row'>"
    page += "<div class='form-group'><label>Total Quantity *</label><input type='number' name='quantity' value='" + str(book['quantity']) + "' min='1' required></div>"
    page += "<div class='form-group'><label>Available Copies</label><input type='number' name='available' value='" + str(book['available']) + "' min='0'></div>"
    page += "</div>"
    page += "<div style='display:flex;gap:8px;padding-top:16px;border-top:1px solid #f0f0f0'>"
    page += "<button type='submit' class='btn btn-blue'>Save Changes</button>"
    page += "<a href='/books' class='btn btn-gray'>Cancel</a>"
    page += "</div></form></div></div>"
    return page


# DELETE BOOK
@app.route("/delete/<int:book_id>")
def delete_book(book_id):
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/books")


# SEARCH PAGE
@app.route("/search")
def search():
    query     = request.args.get("q", "").strip()
    search_by = request.args.get("by", "all")
    results   = []

    if query:
        conn = get_db()
        cur  = conn.cursor(dictionary=True)
        like = "%" + query + "%"
        if search_by == "title":
            cur.execute("SELECT * FROM books WHERE title LIKE %s", (like,))
        elif search_by == "author":
            cur.execute("SELECT * FROM books WHERE author LIKE %s", (like,))
        elif search_by == "category":
            cur.execute("SELECT * FROM books WHERE category LIKE %s", (like,))
        elif search_by == "isbn":
            cur.execute("SELECT * FROM books WHERE isbn LIKE %s", (like,))
        else:
            cur.execute("SELECT * FROM books WHERE title LIKE %s OR author LIKE %s OR category LIKE %s OR isbn LIKE %s", (like, like, like, like))
        results = cur.fetchall()
        cur.close()
        conn.close()

    all_sel = "selected" if search_by == "all"      else ""
    t_sel   = "selected" if search_by == "title"    else ""
    a_sel   = "selected" if search_by == "author"   else ""
    c_sel   = "selected" if search_by == "category" else ""
    i_sel   = "selected" if search_by == "isbn"     else ""

    rows = ""
    for b in results:
        rows += "<tr>"
        rows += "<td>#" + str(b['book_id']) + "</td>"
        rows += "<td><b>" + b['title'] + "</b></td>"
        rows += "<td>" + b['author'] + "</td>"
        rows += "<td>" + b['category'] + "</td>"
        rows += "<td>" + b['isbn'] + "</td>"
        rows += "<td>" + str(b['available']) + "</td>"
        rows += "<td>"
        rows += "<a href='/edit/" + str(b['book_id']) + "' class='btn btn-blue' style='font-size:12px;padding:5px 10px;margin-right:4px'>Edit</a>"
        rows += "<a href='/delete/" + str(b['book_id']) + "' class='btn btn-red' style='font-size:12px;padding:5px 10px' onclick=\"return confirm('Delete?')\">Delete</a>"
        rows += "</td></tr>"

    if not rows:
        rows = "<tr><td colspan='7' style='text-align:center;padding:40px;color:#aaa'>"
        rows += "No results found" if query else "Enter a search query above"
        rows += "</td></tr>"

    page = STYLE + NAV + "<div class='container'>"
    page += "<h1>Search Books</h1>"
    page += "<div class='card'>"
    page += "<form method='GET' style='display:flex;gap:10px;flex-wrap:wrap;align-items:flex-end'>"
    page += "<div class='form-group' style='flex:1;min-width:200px'><label>Search Query</label><input type='text' name='q' value='" + query + "' placeholder='Type here'></div>"
    page += "<div class='form-group'><label>Search By</label>"
    page += "<select name='by'>"
    page += "<option value='all' "      + all_sel + ">All Fields</option>"
    page += "<option value='title' "    + t_sel   + ">Title</option>"
    page += "<option value='author' "   + a_sel   + ">Author</option>"
    page += "<option value='category' " + c_sel   + ">Category</option>"
    page += "<option value='isbn' "     + i_sel   + ">ISBN</option>"
    page += "</select></div>"
    page += "<button type='submit' class='btn btn-blue'>Search</button>"
    if query:
        page += "<a href='/search' class='btn btn-gray'>Clear</a>"
    page += "</form></div>"
    if query:
        page += "<p style='font-size:13px;color:#888;margin-bottom:12px'>" + str(len(results)) + " result(s) found for <b>" + query + "</b></p>"
    page += "<div class='card' style='padding:0;overflow:hidden'>"
    page += "<table><thead><tr><th>ID</th><th>Title</th><th>Author</th><th>Category</th><th>ISBN</th><th>Available</th><th>Actions</th></tr></thead>"
    page += "<tbody>" + rows + "</tbody></table>"
    page += "</div></div>"
    return page


# START THE APP
if __name__ == "__main__":
    app.run(debug=True)