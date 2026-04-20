from flask import Flask, render_template, request, redirect, jsonify, session, flash, url_for
import sqlite3
import re

app = Flask(__name__)
app.secret_key = "abc123"  # bắt buộc để dùng session

@app.route('/Manager')


@app.route('/')
def index():
    return redirect('/home')

@app.route('/home')
def home():
    return render_template('base_user.html')

def get_db():
    conn = sqlite3.connect("quan-an.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return render_template('login.html', error="Vui lòng nhập đầy đủ thông tin")

        conn = get_db()
        user = conn.execute("""
            SELECT * FROM Khach_hang 
            WHERE user_name=? AND password=?
        """, (username, password)).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id_kh']
            session['ten_kh'] = user['Ten_kh']
            return redirect('/home')
        else:
            return render_template('login.html', error="Sai tài khoản hoặc mật khẩu")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear() # Xóa toàn bộ dữ liệu trong session
    return redirect('/home') # Quay về trang đăng nhập

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

def get_current_order(id_kh):
    conn = sqlite3.connect('quan-an.db')
    cursor = conn.cursor()

    # tìm đơn chưa thanh toán
    cursor.execute("""
        SELECT id_don FROM Don_hang
        WHERE id_kh=? AND Trang_thai='cart'
        LIMIT 1
    """, (id_kh,))

    row = cursor.fetchone()

    if row:
        return row[0]

    # chưa có → tạo mới
    cursor.execute("""
        INSERT INTO Don_hang (id_kh, Trang_thai)
        VALUES (?, 'cart')
    """, (id_kh,))

    conn.commit()
    return cursor.lastrowid

@app.route('/add_to_cart/<int:id_mon>')
def add_to_cart(id_mon):
    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('quan-an.db')
    cursor = conn.cursor()

    id_kh = session.get('user_id')
    id_don = get_current_order(id_kh)

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
    if 'user_id' not in session:
        return redirect('/login')

    page = request.args.get('page', 1, type=int)
    danh_muc = request.args.get('category')
    keyword = request.args.get('keyword')

    ds_mon = update_menu(page=page, danh_muc=danh_muc, keyword=keyword)

    return render_template('menu.html', ds_mon=ds_mon, page=page, danh_muc=danh_muc, keyword=keyword)


@app.route('/decrease/<int:id_mon>')
def decrease(id_mon):
    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('quan-an.db')
    cursor = conn.cursor()

    id_kh = session.get('user_id')
    id_don = get_current_order(id_kh)

    cursor.execute("""
        UPDATE Chi_tiet_don
        SET So_luong = So_luong - 1
        WHERE id_don = ? AND id_mon = ? AND So_luong > 1
    """, (id_don, id_mon))

    conn.commit()
    conn.close()

    return redirect('/cart')

@app.route('/increase/<int:id_mon>')
def increase(id_mon):
    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('quan-an.db')
    cursor = conn.cursor()

    id_kh = session.get('user_id')
    id_don = get_current_order(id_kh)

    cursor.execute("""
        UPDATE Chi_tiet_don
        SET So_luong = So_luong + 1
        WHERE id_don = ? AND id_mon = ?
    """, (id_don, id_mon))

    conn.commit()
    conn.close()

    return redirect('/cart')

@app.route('/remove/<int:id_mon>')
def remove_item(id_mon):
    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('quan-an.db')
    cursor = conn.cursor()

    id_kh = session.get('user_id')
    id_don = get_current_order(id_kh)

    cursor.execute("""
        DELETE FROM Chi_tiet_don
        WHERE id_don = ? AND id_mon = ?
    """, (id_don, id_mon))

    conn.commit()
    conn.close()

    return redirect('/cart')


@app.route('/cart')
def cart():
    if 'user_id' not in session:
        return redirect('/login')

    id_kh = session.get('user_id')
    id_don = get_current_order(id_kh)

    conn = get_db()

    # 1. Lấy thông tin loại đơn và thời gian
    order_info = conn.execute("SELECT Loai_don, Thoi_gian FROM Don_hang WHERE id_don = ?", (id_don,)).fetchone()
    loai = order_info["Loai_don"] if order_info else "eat_in"
    thoigian = (order_info["Thoi_gian"].replace(" ", "T")[:16]) if order_info and order_info["Thoi_gian"] else ""

    # 2. Lấy danh sách món ăn trong giỏ
    items = conn.execute("""
        SELECT m.Ten_mon, m.Gia, c.So_luong, m.Anh, m.id_mon, m.Danh_muc
        FROM Chi_tiet_don c
        JOIN Mon_an m ON c.id_mon = m.id_mon
        WHERE c.id_don = ?
    """, (id_don,)).fetchall()

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

    bank_id = "MSB"
    account_number = "96886693010391"

    import urllib.parse
    description = urllib.parse.quote(f"YUMMYOrder{id_don}")

    qr_url = f"https://img.vietqr.io/image/{bank_id}-{account_number}-compact.jpg?amount={total}&addInfo={description}"

    conn.close()

    return render_template('cart.html', items=cart_items, total=total, loai=loai, thoigian=thoigian, qr_url=qr_url, amount=total, order_id = id_don)


@app.route("/update_time", methods=["POST"])
def update_time():
    data = request.get_json()
    thoigian = data.get("thoigian")

    conn = sqlite3.connect('quan-an.db')
    cursor = conn.cursor()

    id_kh = session.get('user_id')
    id_don = get_current_order(id_kh)

    cursor.execute("""
        UPDATE Don_hang
        SET Thoi_gian = ?
        WHERE id_don = ?
    """, (thoigian, id_don))

    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

@app.route("/update_service", methods=["POST"])
def update_service():
    data = request.get_json()
    loai_don = data.get("loai_don")

    conn = sqlite3.connect('quan-an.db')
    cursor = conn.cursor()

    id_kh = session.get('user_id')
    id_don = get_current_order(id_kh)

    cursor.execute("""
        UPDATE Don_hang
        SET Loai_don = ?
        WHERE id_don = ?
    """, (loai_don, id_don))

    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

@app.route('/about_us')
def about_us():
    return render_template('about_us.html')

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if 'user_id' not in session:
        return redirect('/login')

    id_kh = session.get('user_id')
    db = get_db()

    if request.method == "POST":
        # Dùng .get() để an toàn
        ten = request.form.get("ten")
        email = request.form.get("email")
        sdt = request.form.get("sdt")
        gioitinh = request.form.get("gioitinh")
        diachi = request.form.get("diachi")
        avatar = request.form.get("avatar")

        db.execute("""
            UPDATE Khach_hang
            SET Ten_kh=?, email=?, Sdt=?, Gioi_tinh=?, Dia_chi=?, avatar=?
            WHERE id_kh=?
        """, (ten, email, sdt, gioitinh, diachi, avatar, id_kh))
        db.commit()

    # Sửa chỗ này: Lấy theo id_kh của người dùng hiện tại
    user = db.execute("SELECT * FROM Khach_hang WHERE id_kh=?", (id_kh,)).fetchone()
    db.close()

    return render_template("profile_user.html", user=user)

@app.route('/myorders')
def myorders():
    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('quan-an.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    id_kh = session.get('user_id')

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


@app.route('/webhook/sepay', methods=['POST'])
def sepay_webhook():
    print("WEBHOOK HIT")

    data = request.get_json(silent=True)
    print("DATA:", data)

    if not data:
        return "NO DATA", 200

    description = (
        data.get('description')
        or data.get('data', {}).get('description')
        or data.get('content')
        or ""
    )

    print("DESCRIPTION:", description)

    match = re.search(r'YUMMYOrder(\d+)', description)

    if match:
        order_id = int(match.group(1))

        db = get_db()
        db.execute(
            "UPDATE Don_hang SET Trang_thai = 'Chưa xong' WHERE id_don = ?",
            (order_id,)
        )
        db.commit()
        db.close()

        print("UPDATED:", order_id)
    else:
        print("KHÔNG TÌM THẤY ORDER ID")

    return "OK"

SEPAY_SECRET = "86RU0UDOJS4A8UZDYGYPJVETB2LLBRTYM0II3U5WKQXOJ1FCPYCGCRXNSFXOXK3V"

@app.route('/check_payment/<int:order_id>')
def check_payment(order_id):
    db = get_db()
    order = db.execute(
        "SELECT Trang_thai FROM Don_hang WHERE id_don = ?",
        (order_id,)
    ).fetchone()

    return jsonify({
        "status": order['Trang_thai']
    })

@app.route('/cancel_order/<int:order_id>')
def cancel_order(order_id):
    if 'user_id' not in session:
        return redirect('/login')

    db = get_db()

    try:
        db.execute("""
            UPDATE Don_hang
            SET Trang_thai = 'cancelled'
            WHERE id_don = ? 
            AND Trang_thai IN ('cart', 'Chưa xong')
        """, (order_id,))
        db.commit()
    finally:
        db.close()

    return redirect('/myorders')


@app.route('/confirm_payment/<int:order_id>', methods=['POST'])
def confirm_payment(order_id):
    if 'user_id' not in session:
        return redirect('/login')

    db = get_db()

    try:
        # 1. Tính tổng tiền
        order_data = db.execute("""
            SELECT SUM(m.Gia * c.So_luong) as tong 
            FROM Chi_tiet_don c 
            JOIN Mon_an m ON c.id_mon = m.id_mon 
            WHERE c.id_don = ?
        """, (order_id,)).fetchone()

        tong_tien = order_data['tong'] if order_data['tong'] else 0

        # 2. Update trạng thái đơn cũ
        db.execute("""
            UPDATE Don_hang 
            SET Trang_thai = 'Chưa xong' 
            WHERE id_don = ?
        """, (order_id,))

        # 3. Lưu hóa đơn
        db.execute("""
            INSERT INTO Hoa_don (id_don, Tong_tien, Ngay) 
            VALUES (?, ?, datetime('now', 'localtime'))
        """, (order_id, tong_tien))

        # tạo giỏ mới
        db.execute("""
            INSERT INTO Don_hang (id_kh, Trang_thai)
            VALUES (?, 'cart')
        """, (session.get('user_id'),))

        db.commit()

    except:
        db.rollback()
        return "Lỗi thanh toán"

    finally:
        db.close()

    return redirect('/cart')

@app.route('/password_manager', methods=['GET', 'POST'])
def password_manager():
    if 'user_id' not in session:
        return redirect('/login')

    id_kh = session.get('user_id')
    db = get_db()
    message = ""

    if request.method == "POST":
        new_user = request.form.get("new_username")
        cur_pass = request.form.get("current_password")
        new_pass = request.form.get("new_password")
        conf_pass = request.form.get("confirm_password")

        # 1. Kiểm tra mật khẩu cũ có đúng không
        user = db.execute("SELECT password FROM Khach_hang WHERE id_kh=?", (id_kh,)).fetchone()

        if user['password'] != cur_pass:
            message = "Mật khẩu hiện tại không chính xác!"
        elif new_pass != conf_pass:
            message = "Mật khẩu mới không khớp nhau!"
        else:
            # 2. Cập nhật vào DB
            db.execute("UPDATE Khach_hang SET user_name=?, password=? WHERE id_kh=?",
                       (new_user, new_pass, id_kh))
            db.commit()
            message = "Cập nhật tài khoản thành công!"

    user = db.execute("SELECT * FROM Khach_hang WHERE id_kh=?", (id_kh,)).fetchone()
    db.close()
    return render_template('password_manager.html', user=user, message=message)


if __name__ == '__main__':
    app.run(debug=True)
