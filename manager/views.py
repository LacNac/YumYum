import requests
from flask import render_template, redirect, url_for, request
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

@manager_bp.route('/dondeli/chitiet')
def deli_chitiet():
    try:
        res = requests.get(f"{BASE_API}/dsdel/chitiet")
        data = res.json()
    except Exception:
        data = []
    return render_template('deli_detail.html', details=data)

@manager_bp.route('/doneatin')
def eatin():
    try:
        res = requests.get(f"{BASE_API}/dseatin")
        data = res.json()
    except Exception:
        data = []
    return render_template('eatin_list.html', orders=data)

@manager_bp.route('/doneatin/chitiet')
def eatin_chitiet():
    try:
        res = requests.get(f"{BASE_API}/dseatin/chitiet")
        data = res.json()
    except Exception:
        data = []
    return render_template('eatin_detail.html', details=data)

@manager_bp.route('/update_status_deli/<int:id_don>', methods=['POST'])
def update_status_deli(id_don):
    try:
        requests.post(f"{BASE_API}/hoan_thanh_deli/{id_don}")
    except Exception:
        pass
    return redirect(url_for('manager.deli'))

@manager_bp.route('/update_status_eatin/<int:id_don>', methods=['POST'])
def update_status_eatin(id_don):
    try:
        requests.post(f"{BASE_API}/hoan_thanh_eatin/{id_don}")
    except Exception:
        pass
    return redirect(url_for('manager.eatin'))

@manager_bp.route('/monan')
def monan():
    try:
        res = requests.get(f"{BASE_API}/monan")
        data = res.json()
    except Exception:
        data = []
    return render_template('listfood.html', foods=data)

@manager_bp.route('/themmon', methods=['GET', 'POST'])
def themmon():
    if request.method == 'POST':
        data = {
            "ten": request.form.get("ten"),
            "gia": request.form.get("gia"),
            "danhmuc": request.form.get("danhmuc"),
            "anh": request.form.get("anh")
        }
        try:
            requests.post(f"{BASE_API}/themmon", json=data)
        except Exception:
            pass
        return redirect(url_for('manager.monan'))

    return render_template('addfood.html')

@manager_bp.route('/xoamon/<int:id_mon>', methods=['POST'])
def xoamon(id_mon):
    try:
        res = requests.post(f"{BASE_API}/xoamon/{id_mon}")
        print("STATUS:", res.status_code)
        print("RESPONSE:", res.text)
    except Exception as e:
        print("ERROR:", e)

    return redirect(url_for('manager.monan'))