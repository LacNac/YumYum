from flask import Flask, render_template, request, redirect, jsonify
from livereload import Server
import sqlite3

app = Flask(__name__)

@app.route('/')
@app.route('/Manager')

@app.route('/home')
def home():
    return render_template('base_user.html')

def get_db():
    conn = sqlite3.connect("quan-an.db")
    conn.row_factory = sqlite3.Row  # để truy cập kiểu user['Ten_kh']
    return conn

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

    id_don = 1

    # lấy loại đơn
    cursor.execute("SELECT Loai_don FROM Don_hang WHERE id_don = ?", (id_don,))
    row = cursor.fetchone()
    loai = row["Loai_don"] if row else "eat_in"

    # lấy thời gian
    cursor.execute("SELECT Loai_don, Thoi_gian FROM Don_hang WHERE id_don = 1")
    row = cursor.fetchone()

    loai = row["Loai_don"] if row else "eat_in"
    thoigian = row["Thoi_gian"] if row else ""

    if thoigian:
        thoigian = thoigian.replace(" ", "T")[:16]

    # lấy giỏ hàng
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

    return render_template(
        'cart.html',
        items=cart_items,
        total=total,
        loai=loai, thoigian=thoigian
    )
@app.route("/update_time", methods=["POST"])
def update_time():
    data = request.get_json()
    thoigian = data.get("thoigian")

    conn = sqlite3.connect('quan-an.db')
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Don_hang
        SET Thoi_gian = ?
        WHERE id_don = 1
    """, (thoigian,))

    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

@app.route("/update_service", methods=["POST"])
def update_service():
    data = request.get_json()
    loai_don = data.get("loai_don")

    conn = sqlite3.connect('quan-an.db')
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Don_hang
        SET Loai_don = ?
        WHERE id_don = 1
    """, (loai_don,))

    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

@app.route('/about_us')
def about_us():
    return render_template('about_us.html')

@app.route("/profile", methods=["GET", "POST"])
def profile():
    db = get_db()

    if request.method == "POST":
        ten = request.form["ten"]
        email = request.form["email"]
        sdt = request.form["sdt"]
        gioitinh = request.form["gioitinh"]
        diachi = request.form["diachi"]
        avatar = request.form["avatar"]

        db.execute("""
            UPDATE Khach_hang
            SET Ten_kh=?, email=?, Sdt=?, Gioi_tinh=?, Dia_chi=?, avatar=?
            WHERE id_kh=1
        """, (ten, email, sdt, gioitinh, diachi, avatar))
        db.commit()

    user = db.execute("SELECT * FROM Khach_hang WHERE id_kh=1").fetchone()

    return render_template("profile_user.html", user=user)

@app.route('/myorders')
def myorders():
    conn = sqlite3.connect('quan-an.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    id_kh = 1  # tạm fix

    cursor.execute("""
        SELECT *
        FROM Don_hang
        WHERE id_kh = ?
        ORDER BY id_don DESC
    """, (id_kh,))

    orders = cursor.fetchall()

    order_list = []

    for order in orders:
        # lấy món trong từng đơn
        cursor.execute("""
            SELECT m.Ten_mon, m.Gia, c.So_luong, m.Anh, m.id_mon
            FROM Chi_tiet_don c
            JOIN Mon_an m ON c.id_mon = m.id_mon
            WHERE c.id_don = ?
        """, (order["id_don"],))

        items = cursor.fetchall()

        total = 0
        item_list = []

        for item in items:
            subtotal = item["Gia"] * item["So_luong"]
            total += subtotal

            item_list.append({
                "id": item["id_mon"],
                "ten": item["Ten_mon"],
                "qty": item["So_luong"],
                "anh": item["Anh"]
            })

        order_list.append({
            "id": order["id_don"],
            "loai": order["Loai_don"],
            "time": order["Thoi_gian"],
            "status": order["Trang_thai"],
            "total": total,
            "items": item_list
        })

    conn.close()

    return render_template("myorder_profile.html", orders=order_list)


@app.route('/submit-evaluation', methods=['POST'])
def submit_evaluation():
    product_id = request.form['product_id']
    rating = int(request.form['rating'])

    conn = sqlite3.connect('quan-an.db')
    cursor = conn.cursor()

    # lấy rating hiện tại
    cursor.execute("""
        SELECT rating, so_luot FROM Mon_an WHERE id_mon = ?
    """, (product_id,))

    row = cursor.fetchone()

    if row:
        current_rating, so_luot = row

        if current_rating is None:
            current_rating = 0
        if so_luot is None:
            so_luot = 0

        # tính trung bình mới
        new_so_luot = so_luot + 1
        new_rating = (current_rating * so_luot + rating) / new_so_luot

        # update DB
        cursor.execute("""
            UPDATE Mon_an
            SET rating = ?, so_luot = ?
            WHERE id_mon = ?
        """, (new_rating, new_so_luot, product_id))

    conn.commit()
    conn.close()

    return redirect('/myorders')

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