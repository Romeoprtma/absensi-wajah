from flask import request, jsonify
from datetime import datetime
from db import get_db_connection

def cek_jadwal_absensi():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        hari_sekarang = konversi_hari_ke_indonesia(datetime.now().strftime("%A"))
        waktu_sekarang = datetime.now().time()  # Simpan sebagai objek time()

        query = "SELECT jam_mulai, jam_selesai FROM jadwal_absensi WHERE hari = ? AND aktif = 1"
        cursor.execute(query, (hari_sekarang,))
        jadwal = cursor.fetchone()

        if jadwal:
            jam_mulai, jam_selesai = jadwal

            # Ubah string waktu menjadi objek time()
            jam_mulai = parse_waktu(jam_mulai)
            jam_selesai = parse_waktu(jam_selesai)

            if jam_mulai <= waktu_sekarang <= jam_selesai:
                return jsonify({"status": "success", "message": "Absensi diperbolehkan."}), 200
            else:
                return jsonify({"status": "failed", "message": f"Absensi hanya diperbolehkan antara {jam_mulai} - {jam_selesai}."}), 403
        
        return jsonify({"status": "failed", "message": f"Tidak ada jadwal absensi untuk hari {hari_sekarang}."}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


def parse_waktu(waktu_str):
    """Fungsi untuk mengubah string waktu ke format time Python"""
    try:
        return datetime.strptime(waktu_str, "%H:%M:%S").time()
    except ValueError:
        return datetime.strptime(waktu_str, "%H:%M").time()


def update_jadwal(id):
    data = request.get_json()
    
    if not all(k in data for k in ["hari", "jam_mulai", "jam_selesai", "aktif"]):
        return jsonify({"error": "Data tidak lengkap"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "UPDATE jadwal_absensi SET hari = ?, jam_mulai = ?, jam_selesai = ?, aktif = ? WHERE id = ?",
            (data["hari"], data["jam_mulai"], data["jam_selesai"], data["aktif"], id),
        )
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Jadwal tidak ditemukan"}), 404

        return jsonify({"message": "Jadwal berhasil diupdate"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


def add_jadwal():
    data = request.get_json()
    
    if not all(k in data for k in ["hari", "jam_mulai", "jam_selesai", "aktif"]):
        return jsonify({"error": "Data tidak lengkap"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO jadwal_absensi (hari, jam_mulai, jam_selesai, aktif) VALUES (?, ?, ?, ?)",
            (data["hari"], data["jam_mulai"], data["jam_selesai"], data["aktif"]),
        )
        conn.commit()
        new_id = cursor.lastrowid

        return jsonify({"message": "Jadwal berhasil ditambahkan", "id": new_id}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


def konversi_hari_ke_indonesia(hari_inggris):
    hari_indonesia = {
        "Monday": "Senin",
        "Tuesday": "Selasa",
        "Wednesday": "Rabu",
        "Thursday": "Kamis",
        "Friday": "Jumat",
        "Saturday": "Sabtu",
        "Sunday": "Minggu"
    }
    return hari_indonesia.get(hari_inggris, hari_inggris)
