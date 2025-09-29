import sys, os
import sqlite3
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem

DB_PATH = os.path.join(os.path.dirname(__file__), 'com.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS computer(
                "รหัส" TEXT PRIMARY KEY NOT NULL,
                "รหัสคุรภัณฑ์" TEXT,
                "ชื่อคุรภัณฑ์" TEXT,
                "รายละเอียด" TEXT,
                "ห้อง" TEXT,
                "พิกัด" TEXT
            );
        """)
        conn.commit()
    finally:
        conn.close()

class comcs(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('comcs.ui', self)

        init_db()

        self.pushButton.clicked.connect(self.saveData)
        self.loadData()
        self.tableWidget.cellClicked.connect(self.on_row_clicked)
        self.pushButton_2.clicked.connect(self.update_record)
        self.pushButton_3.clicked.connect(self.delete_record)

    def on_row_clicked(self, row, column):
        def get_item(row, col):
            item = self.tableWidget.item(row, col)
            return item.text() if item else ""

        self.lineEdit.setText(get_item(row, 0))
        self.lineEdit_2.setText(get_item(row, 1))
        self.lineEdit_3.setText(get_item(row, 2))
        self.lineEdit_4.setText(get_item(row, 3))
        self.lineEdit_5.setText(get_item(row, 4))
        self.lineEdit_6.setText(get_item(row, 5))

    def saveData(self):
        id = self.lineEdit.text().strip()
        id_c = self.lineEdit_2.text().strip()
        n_c = self.lineEdit_3.text().strip()
        deta = self.lineEdit_4.text().strip()
        room = self.lineEdit_5.text().strip()
        locate = self.lineEdit_6.text().strip()

        if not all([id, id_c, n_c, deta, room, locate]):
            QMessageBox.warning(self, "ข้อมูลไม่ครบถ้วน", "กรุณากรอกข้อมูลให้ครบทุกช่อง")
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()

            # ตรวจสอบรหัสซ้ำ
            cur.execute('SELECT 1 FROM computer WHERE "รหัส" = ?', (id,))
            if cur.fetchone():
                QMessageBox.warning(self, "ข้อมูลซ้ำ", "รหัสนี้มีอยู่แล้วในระบบ")
                return

            cur.execute(
                'INSERT INTO computer ("รหัส", "รหัสคุรภัณฑ์", "ชื่อคุรภัณฑ์", "รายละเอียด", "ห้อง", "พิกัด") VALUES (?, ?, ?, ?, ?, ?)',
                (id, id_c, n_c, deta, room, locate)
            )
            conn.commit()
        except Exception as e:
            QMessageBox.critical(self, "บันทึกข้อมูลล้มเหลว", f"เกิดข้อผิดพลาด\n{e}")
            return
        finally:
            conn.close()

        QMessageBox.information(self, "สำเร็จ", "บันทึกข้อมูลสำเร็จ")
        self.loadData()

        QMessageBox.information(
            self,
            "ข้อมูลคุรภัณฑ์",
            f"รหัส: {id}\n"
            f"รหัสคุรภัณฑ์: {id_c}\n"
            f"ชื่อคุรภัณฑ์: {n_c}\n"
            f"รายละเอียด: {deta}\n"
            f"ห้อง: {room}\n"
            f"พิกัด: {locate}"
        )

    def loadData(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute('SELECT * FROM computer')
            rows = cur.fetchall()
        except Exception as e:
            QMessageBox.critical(self, "โหลดข้อมูลล้มเหลว", f"เกิดข้อผิดพลาด\n{e}")
            return
        finally:
            conn.close()

        self.tableWidget.setRowCount(len(rows))
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setHorizontalHeaderLabels(['รหัส', 'รหัสคุรภัณฑ์', 'ชื่อคุรภัณฑ์', 'รายละเอียด', 'ห้อง', 'พิกัด'])

        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                self.tableWidget.setItem(r, c, QTableWidgetItem(str(val)))

        self.tableWidget.resizeColumnsToContents()

    def delete_record(self):
        code = self.lineEdit.text().strip()
        if not code:
            QMessageBox.warning(self, "ไม่พบรหัส", "กรุณาเลือกรายการจากตารางก่อน")
            return

        confirm = QMessageBox.question(self, "ยืนยันการลบ", f"ต้องการลบข้อมูล '{code}' ใช่หรือไม่?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if confirm != QMessageBox.Yes:
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute('DELETE FROM computer WHERE "รหัส" = ?', (code,))
            conn.commit()
            QMessageBox.information(self, "สำเร็จ", "ลบข้อมูลเรียบร้อย")
        except Exception as e:
            QMessageBox.critical(self, "ลบข้อมูลล้มเหลว", f"เกิดข้อผิดพลาด\n{e}")
        finally:
            conn.close()
            self.loadData()

    def update_record(self):
        id = self.lineEdit.text().strip()
        id_c = self.lineEdit_2.text().strip()
        n_c = self.lineEdit_3.text().strip()
        deta = self.lineEdit_4.text().strip()
        room = self.lineEdit_5.text().strip()
        locate = self.lineEdit_6.text().strip()

        if not id:
            QMessageBox.warning(self, "ไม่พบรหัส", "กรุณาเลือกรายการจากตารางก่อน")
            return

        if not all([id_c, n_c, deta, room, locate]):
            QMessageBox.warning(self, "ข้อมูลไม่ครบ", "กรุณากรอกข้อมูลใหม่ให้ครบทุกช่อง")
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                UPDATE computer
                SET "รหัสคุรภัณฑ์"=?, "ชื่อคุรภัณฑ์"=?, "รายละเอียด"=?, "ห้อง"=?, "พิกัด"=?
                WHERE "รหัส"=?
            """, (id_c, n_c, deta, room, locate, id))
            conn.commit()
            QMessageBox.information(self, "สำเร็จ", "แก้ไขข้อมูลเรียบร้อย")
        except Exception as e:
            QMessageBox.critical(self, "แก้ไขข้อมูลล้มเหลว", f"เกิดข้อผิดพลาด\n{e}")
        finally:
            conn.close()
            self.loadData()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = comcs()
    window.show()
    sys.exit(app.exec_())

