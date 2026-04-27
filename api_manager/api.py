from flask import Flask, jsonify, request
import sqlite3

DATABASE = '../quan-an.db'
app = Flask(__name__)

@app.route('/dsdeli')
def dsdeli():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            k.id_kh,
            d.id_don,
            k.Dia_chi,
            k.Sdt,
            SUM(c.So_luong * m.Gia) AS tong_tien,
            d.Trang_thai
        FROM Don_hang d
        JOIN Khach_hang k ON d.id_kh = k.id_kh
        JOIN Chi_tiet_don c ON d.id_don = c.id_don
        JOIN Mon_an m ON c.id_mon = m.id_mon
        WHERE d.Loai_don = 'deli'
          AND d.Trang_thai IN ('Chưa xong', 'Đã xong')
        GROUP BY d.id_don
    """)

    data = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(data)

@app.route('/dsdel/chitiet')
def dsdeli_chitiet():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            c.id_don,
            m.Ten_mon,
            c.So_luong,
            m.Gia,
            (c.So_luong * m.Gia) AS tong_tien
        FROM Chi_tiet_don c
        JOIN Mon_an m ON c.id_mon = m.id_mon
        ORDER BY c.id_don
    """)

    data = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(data)
@app.route('/dseatin')
def dseatin():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            d.id_don,
            k.Ten_kh,
            k.Sdt,
            d.Thoi_gian,
            SUM(c.So_luong * m.Gia) AS tong_tien,
            d.Trang_thai
        FROM Don_hang d
        JOIN Khach_hang k ON d.id_kh = k.id_kh
        JOIN Chi_tiet_don c ON d.id_don = c.id_don
        JOIN Mon_an m ON c.id_mon = m.id_mon
        WHERE d.Loai_don = 'eat_in'
          AND d.Trang_thai IN ('Chưa xong', 'Đã xong')
        GROUP BY d.id_don
    """)

    data = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(data)
@app.route('/dseatin/chitiet')
def eatin_chitiet():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            c.id_don,
            m.Ten_mon,
            c.So_luong,
            m.Gia,
            (c.So_luong * m.Gia) AS tong_tien
        FROM Chi_tiet_don c
        JOIN Mon_an m ON c.id_mon = m.id_mon
    """)

    data = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(data)

@app.route('/hoan_thanh_deli/<int:id_don>', methods=['POST'])
def hoan_thanh_deli(id_don):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    cur.execute("""
        UPDATE Don_hang
        SET Trang_thai = 'Đã xong'
        WHERE id_don = ?
    """, (id_don,))

    conn.commit()
    conn.close()
    return jsonify({"message": "OK"})

@app.route('/hoan_thanh_eatin/<int:id_don>', methods=['POST'])
def hoan_thanh_eatin(id_don):
    return hoan_thanh_deli(id_don)
@app.route('/doanhthu')
def doanhthu():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            d.Loai_don,
            d.id_don,
            d.Thoi_gian,
            SUM(c.So_luong * m.Gia) AS tong_doanh_thu,
            d.Trang_thai
        FROM Don_hang d
        JOIN Chi_tiet_don c ON d.id_don = c.id_don
        JOIN Mon_an m ON c.id_mon = m.id_mon
        WHERE d.Trang_thai = 'Đã xong'
        GROUP BY d.id_don
        ORDER BY d.Thoi_gian DESC
    """)

    data = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(data)
@app.route('/login', methods = ['GET'])
def dangnhap():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT username, password from Khach_hang
    """)
    users = cur.fetchall()
    conn.close()
    return jsonify([dict(user) for user in users])

@app.route('/signin', methods = ['POST'])
def dangki():
    user = request.json.get('username')
    pw = request.json.get('password')
    ten = request.json.get('ten')
    dc = request.json.get('address')
    sdt = request.json.get('sdt')
    
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        insert into Khach_hang (Ten_kh, Dia_chi, Sdt, username, password)
        values (?, ?, ?, ?, ?)
    """, (ten, dc, sdt, user, pw))
    conn.close()
    return jsonify({"message" : "ok"}), 201

@app.route('/monan')
def dsmonan():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
            select*from Mon_an
            where trang_thai = 1
        """)
    food = [dict(f) for f in cur.fetchall()] 
    conn.close()
    return jsonify(food)

@app.route('/xoamon/<int:id_mon>', methods=['POST'])
def xoamonan(id_mon):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("""UPDATE Mon_an
SET trang_thai = 0
where id_mon = ?""", (id_mon,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Deleted"})
    
@app.route('/themmon', methods=['POST'])
def themonan():
    data = request.json
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO Mon_an (Ten_mon, Gia, Danh_muc, Anh, rating, so_luot, trang_thai)
        VALUES (?, ?, ?, ?, 0, 0, 1)
    """, (data['ten'], data['gia'], data['danhmuc'], data['anh']))
    conn.commit()
    conn.close()
    return jsonify({"message": "Added"})
if __name__ == '__main__':
    app.run(port=5001 ,debug=True)