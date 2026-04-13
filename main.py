from flask import Flask, render_template, request, redirect
from livereload import Server
import sqlite3

app = Flask(__name__)

@app.route('/')
@app.route('/Manager')

@app.route('/home')
def home():
    return render_template('base_user.html')

def update_menu(page=1, per_page=10, danh_muc=None, keyword=None):
    conn = sqlite3.connect('quan-an.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    offset = (page - 1) * per_page

    query = "SELECT * FROM Mon_an WHERE 1=1"
    params = []

    # lọc theo danh mục
    if danh_muc:
        query += " AND Danh_muc = ?"
        params.append(danh_muc)

    # tìm kiếm theo tên món
    if keyword:
        query += " AND Ten_mon LIKE ?"
        params.append(f"%{keyword}%")

    query += " LIMIT ? OFFSET ?"
    params.extend([per_page, offset])

    cursor.execute(query, params)
    data = cursor.fetchall()

    conn.close()
    return data

@app.route('/add_to_cart/<int:id_mon>')
def add_to_cart(id_mon):
    conn = sqlite3.connect('quan-an.db')
    cursor = conn.cursor()

    id_don = 1  # fix cứng

    # kiểm tra món đã có trong giỏ chưa
    cursor.execute("""
        SELECT So_luong FROM Chi_tiet_don
        WHERE id_don = ? AND id_mon = ?
    """, (id_don, id_mon))

    row = cursor.fetchone()

    if row:
        # đã có → tăng số lượng
        cursor.execute("""
            UPDATE Chi_tiet_don
            SET So_luong = So_luong + 1
            WHERE id_don = ? AND id_mon = ?
        """, (id_don, id_mon))
    else:
        # chưa có → thêm mới
        cursor.execute("""
            INSERT INTO Chi_tiet_don (id_don, id_mon, So_luong)
            VALUES (?, ?, 1)
        """, (id_don, id_mon))

    conn.commit()
    conn.close()

    return redirect('/menu')

@app.route('/menu')
def menu():
    page = request.args.get('page', 1, type=int)
    danh_muc = request.args.get('category')
    keyword = request.args.get('keyword')

    ds_mon = update_menu(page=page, danh_muc=danh_muc, keyword=keyword)

    return render_template('menu.html', ds_mon=ds_mon, page=page, danh_muc=danh_muc, keyword=keyword)


@app.route('/decrease/<int:id_mon>')
def decrease(id_mon):
    conn = sqlite3.connect('quan-an.db')
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Chi_tiet_don
        SET So_luong = So_luong - 1
        WHERE id_don = 1 AND id_mon = ? AND So_luong > 1
    """, (id_mon,))

    conn.commit()
    conn.close()

    return redirect('/cart')

@app.route('/increase/<int:id_mon>')
def increase(id_mon):
    conn = sqlite3.connect('quan-an.db')
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Chi_tiet_don
        SET So_luong = So_luong + 1
        WHERE id_don = 1 AND id_mon = ?
    """, (id_mon,))

    conn.commit()
    conn.close()

    return redirect('/cart')

@app.route('/remove/<int:id_mon>')
def remove_item(id_mon):
    conn = sqlite3.connect('quan-an.db')
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM Chi_tiet_don
        WHERE id_don = 1 AND id_mon = ?
    """, (id_mon,))

    conn.commit()
    conn.close()

    return redirect('/cart')

@app.route('/cart')
def cart():
    conn = sqlite3.connect('quan-an.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    id_don = 1  # user hiện tại

    cursor.execute("""
        SELECT m.*, c.So_luong
        FROM Chi_tiet_don c
        JOIN Mon_an m ON c.id_mon = m.id_mon
        WHERE c.id_don = ?
    """, (id_don,))

    items = cursor.fetchall()

    total = 0
    cart_items = []

    for item in items:
        subtotal = item["Gia"] * item["So_luong"]
        total += subtotal

        cart_items.append({
            "mon": item,
            "qty": item["So_luong"],
            "subtotal": subtotal
        })

    conn.close()

    return render_template('cart.html',
                           items=cart_items,
                           total=total)

@app.route('/about_us')
def about_us():
    return render_template('about_us.html')

@app.route('/profile')
def profile():
    return render_template('profile_user.html')

@app.route('/myorders')
def myorders():
    return render_template('myorder_profile.html')

@app.route('/payment')
def payment():
    return render_template('payment_method.html')

@app.route('/password_manager')
def password_manager():
    return render_template('password_manager.html')

if __name__ == '__main__':
    app.run(debug=True)

server = Server(app.wsgi_app)
server.serve(debug=True)