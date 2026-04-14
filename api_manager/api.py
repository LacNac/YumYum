from flask import Flask, jsonify
import sqlite3

DATABASE = 'quan-an.db'
app = Flask(__name__)

@app.route('/dsdeli')
def dulieu():
     conn = sqlite3.connect(DATABASE)
     conn.row_factory = sqlite3.Row
     cur = conn.cursor()

     cur.execute("""
        SELECT 
            Khach_hang.id_kh AS "Mã KH",
            Don_deli.id_don AS "Mã Đơn",
            Khach_hang.dia_chi AS "Địa chỉ",
            Khach_hang.sdt AS "SĐT",
            SUM(chitiet_deli.soluong * Mon_an.Gia) AS "Tổng tiền đơn",
            CASE 
                WHEN Don_deli.trang_thai = 0 THEN 'Chưa làm'
                WHEN Don_deli.trang_thai = 1 THEN 'Đã làm'
                ELSE 'Khác'
            END AS "Trạng thái"
        FROM Khach_hang
        JOIN Don_deli ON Khach_hang.id_kh = Don_deli.id_kh
        JOIN chitiet_deli ON Don_deli.id_don = chitiet_deli.id_don
        JOIN Mon_an ON chitiet_deli.id_mon = Mon_an.id_mon
        GROUP BY 
            Don_deli.id_don, 
            Khach_hang.id_kh, 
            Khach_hang.dia_chi, 
            Khach_hang.sdt, 
            Don_deli.trang_thai;
     """)

     rows = cur.fetchall()
     conn.close()

     result = [dict(row) for row in rows]
     return jsonify(result)

@app.route('/dsdel/chitiet')
def dschitiet_deli():
     conn = sqlite3.connect(DATABASE)
     conn.row_factory = sqlite3.Row
     cur = conn.cursor()
     cur.execute("""
        SELECT 
            chitiet_deli.id_don AS "Mã Đơn",
            Mon_an.Ten_mon AS "Tên món",
            chitiet_deli.soluong AS "Số lượng",
            Mon_an.Gia AS "Giá 1 món",
            (chitiet_deli.soluong * Mon_an.Gia) AS "Tổng tiền"
        FROM chitiet_deli
        JOIN Mon_an ON chitiet_deli.id_mon = Mon_an.id_mon
        ORDER BY chitiet_deli.id_don;   
                 """)
     rows = cur.fetchall()
     conn.close()
     result = [dict(row) for row in rows]
     return jsonify(result)

@app.route('/dseatin')
def dseatin():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            don_eatin.id_don AS "Mã đơn",
            Khach_hang.ten_kh AS "Tên khách hàng",
            Khach_hang.sdt AS "Số điện thoại",
            don_eatin.thoi_gian AS "Thời gian",
            SUM(chi_tiet_eatin.tong_tien) AS "Tổng tiền",
            CASE 
                WHEN don_eatin.trang_thai = 0 THEN 'Chưa làm'
                WHEN don_eatin.trang_thai = 1 THEN 'Đã làm'
                ELSE 'Khác'
            END AS "Trạng thái"
        FROM don_eatin
        JOIN Khach_hang ON don_eatin.id_khach = Khach_hang.id_kh
        JOIN chi_tiet_eatin ON don_eatin.id_don = chi_tiet_eatin.id_don
        GROUP BY 
            don_eatin.id_don, 
            Khach_hang.ten_kh, 
            Khach_hang.sdt, 
            don_eatin.thoi_gian,
            don_eatin.trang_thai;
    """)

    rows = cur.fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])

@app.route('/dseatin/chitiet')
def chitiet_eatin():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            chi_tiet_eatin.id_don AS "Mã đơn",
            Mon_an.Ten_mon AS "Tên món",
            chi_tiet_eatin.soluong AS "Số lượng",
            Mon_an.Gia AS "Giá 1 sp",
            chi_tiet_eatin.tong_tien AS "Tổng tiền 1 sp"
        FROM chi_tiet_eatin
        JOIN Mon_an ON chi_tiet_eatin.id_mon = Mon_an.id_mon;
    """)

    rows = cur.fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])

@app.route('/hoan_thanh_deli/<int:id_don>', methods=['POST'])
def hoan_thanh_deli(id_don):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("UPDATE don_deli SET trang_thai = 1 WHERE id_don = ?", (id_don,))
    conn.commit() # Quan trọng: Phải có dòng này
    conn.close()
    return jsonify({"message": "OK"}), 200

@app.route('/hoan_thanh_eatin/<int:id_don>', methods=['POST'])
def hoan_thanh_eatin(id_don):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("UPDATE don_eatin SET trang_thai = 1 WHERE id_don = ?", (id_don,))
    conn.commit()
    conn.close()
    return jsonify({"message": "OK"}), 200

@app.route('/doanhthu')
def doanh_thu():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            'Tai cho' AS "Loai don",
            don_eatin.id_don AS "Ma don",
            don_eatin.thoi_gian AS "Thoi gian",
            SUM(chi_tiet_eatin.tong_tien) AS "Tong doanh thu",
            don_eatin.trang_thai AS "Trang thai"
        FROM don_eatin
        JOIN chi_tiet_eatin ON don_eatin.id_don = chi_tiet_eatin.id_don
        GROUP BY don_eatin.id_don

        UNION ALL

        SELECT 
            'Giao hang' AS "Loai don",
            Don_deli.id_don AS "Ma don",
            Don_deli.thoi_gian AS "Thoi gian",
            SUM(chitiet_deli.soluong * Mon_an.Gia) AS "Tong doanh thu",
            Don_deli.trang_thai AS "Trang thai"
        FROM Don_deli
        JOIN chitiet_deli ON Don_deli.id_don = chitiet_deli.id_don
        JOIN Mon_an ON chitiet_deli.id_mon = Mon_an.id_mon
        GROUP BY Don_deli.id_don

        ORDER BY "Thoi gian" DESC;
    """)

    rows = cur.fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])
if __name__ == '__main__':
    app.run(port=5001 ,debug=True)