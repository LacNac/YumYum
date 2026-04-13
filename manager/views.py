import requests
from flask import render_template, redirect, url_for
from . import manager_bp

BASE_API = "http://127.0.0.1:5001"

@manager_bp.route('/')
@manager_bp.route('/doanhthu')
def doanhthu():
    try:
        res = requests.get(f"{BASE_API}/doanhthu")
        data = res.json()
    except Exception:
        data = []
    return render_template('total.html', total=data)

@manager_bp.route('/dondeli')
def deli():
    try:
        res = requests.get(f"{BASE_API}/dsdeli")
        data = res.json()
    except Exception:
        data = []
    return render_template('deli_list.html', orders=data)

# 3. Trang chi tiết đơn giao hàng
@manager_bp.route('/dondeli/chitiet')
def deli_chitiet():
    try:
        res = requests.get(f"{BASE_API}/dsdel/chitiet")
        data = res.json()
    except Exception:
        data = []
    return render_template('deli_detail.html', details=data)

# 4. Trang danh sách đơn ăn tại chỗ (Eatin)
@manager_bp.route('/doneatin')
def eatin():
    try:
        res = requests.get(f"{BASE_API}/dseatin")
        data = res.json()
    except Exception:
        data = []
    return render_template('eatin_list.html', orders=data)

# 5. Trang chi tiết đơn ăn tại chỗ
@manager_bp.route('/doneatin/chitiet')
def eatin_chitiet():
    try:
        res = requests.get(f"{BASE_API}/dseatin/chitiet")
        data = res.json()
    except Exception:
        data = []
    return render_template('eatin_detail.html', details=data)

# 6. Xử lý nút bấm Hoàn thành đơn Deli
@manager_bp.route('/update_status_deli/<int:id_don>', methods=['POST'])
def update_status_deli(id_don):
    try:
        requests.post(f"{BASE_API}/hoan_thanh_deli/{id_don}")
    except Exception:
        pass
    return redirect(url_for('manager.deli'))

# 7. Xử lý nút bấm Hoàn thành đơn Eatin
@manager_bp.route('/update_status_eatin/<int:id_don>', methods=['POST'])
def update_status_eatin(id_don):
    try:
        requests.post(f"{BASE_API}/hoan_thanh_eatin/{id_don}")
    except Exception:
        pass
    return redirect(url_for('manager.eatin'))
