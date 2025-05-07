import sys
import sqlite3
import random
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit,
    QTabWidget, QListWidget, QTextEdit, QMessageBox, QTimeEdit
)
from PyQt6.QtCore import Qt, QDate, QTime
from PyQt6.QtWidgets import QDateEdit


class ZatishokApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Затишок")
        self.setGeometry(100, 100, 600, 700)
        self.setStyleSheet("background-color: #FDF8F5; color: black;")
        
        self.initDB()
        self.initUI()

    def initDB(self):
        self.conn = sqlite3.connect("zatishok.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS joys (
                id INTEGER PRIMARY KEY,
                text TEXT,
                date DATE
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY,
                text TEXT,
                time TEXT
            )
        """)
        self.conn.commit()

    def initUI(self):
        mainLayout = QVBoxLayout()
        
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                background: #FFDDC1;
                color: black;
                padding: 10px;
                border-radius: 8px;
                font-size: 14px;
            }
            QTabBar::tab:selected {
                background: white;
                border: 2px solid #F4CAC3;
                font-weight: bold;
            }
        """)

        self.tab_main = QWidget()
        self.tab_reminders = QWidget()
        self.tab_archive = QWidget()
        self.tab_statistics = QWidget()
        self.tab_field = QWidget()

        self.tabs.addTab(self.tab_main, "🌿 Головна")
        self.tabs.addTab(self.tab_reminders, "🔔 Нагадування")
        self.tabs.addTab(self.tab_archive, "📜 Архів радостей")
        self.tabs.addTab(self.tab_statistics, "📊 Статистика")
        self.tabs.addTab(self.tab_field, "🌼 Поле")

        self.initMainTab()
        self.initRemindersTab()
        self.initArchiveTab()
        self.initStatisticsTab()
        self.initFieldTab()

        mainLayout.addWidget(self.tabs)
        self.setLayout(mainLayout)

    def initMainTab(self):
        layout = QVBoxLayout()
        
        self.joy_text = QTextEdit()
        self.joy_text.setPlaceholderText("Напиши тут свою мікрорадість...")
        self.joy_text.setStyleSheet("background-color: white; color: black;")
        
        self.save_button = QPushButton("💾 Зберегти радість")
        self.save_button.setStyleSheet("background-color: #F4CAC3; color: black;")
        self.save_button.clicked.connect(self.saveJoy)

        self.random_joy_button = QPushButton("😊 Мені сумно")
        self.random_joy_button.setStyleSheet("background-color: #F4CAC3; color: black;")
        self.random_joy_button.clicked.connect(self.showRandomJoy)
        
        layout.addWidget(self.joy_text)
        layout.addWidget(self.save_button)
        layout.addWidget(self.random_joy_button)
        self.tab_main.setLayout(layout)

    def initRemindersTab(self):
        layout = QVBoxLayout()
        
        self.reminder_text = QLineEdit()
        self.reminder_text.setPlaceholderText("Напиши нагадування...")
        self.reminder_text.setStyleSheet("background-color: white; color: black;")
        
        self.reminder_time = QTimeEdit()
        self.reminder_time.setStyleSheet("background-color: white; color: black;")
        self.reminder_time.setTime(QTime.currentTime())
        
        self.reminder_button = QPushButton("🔔 Додати нагадування")
        self.reminder_button.setStyleSheet("background-color: #FFDAB9; color: black;")
        self.reminder_button.clicked.connect(self.addReminder)
        
        self.reminder_list = QListWidget()
        self.reminder_list.setStyleSheet("background-color: white; color: black;")
        
        layout.addWidget(self.reminder_text)
        layout.addWidget(self.reminder_time)
        layout.addWidget(self.reminder_button)
        layout.addWidget(self.reminder_list)
        self.tab_reminders.setLayout(layout)

    def initArchiveTab(self):
        layout = QVBoxLayout()
        self.archive_list = QListWidget()
        self.archive_list.setStyleSheet("background-color: white; color: black;")
        layout.addWidget(self.archive_list)
        self.tab_archive.setLayout(layout)
        self.loadArchive()

    def initStatisticsTab(self):
        # Додаємо віджети для вибору початкової та кінцевої дати
        self.start_date_input = QDateEdit(self)
        self.end_date_input = QDateEdit(self)

        self.start_date_input.setDate(QDate.currentDate())
        self.end_date_input.setDate(QDate.currentDate())

        self.start_date_input.setStyleSheet("background-color: white; color: black;")
        self.end_date_input.setStyleSheet("background-color: white; color: black;")

        # Вибір періоду
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Виберіть період:"))
        layout.addWidget(self.start_date_input)
        layout.addWidget(self.end_date_input)

        # Кнопка для оновлення статистики
        self.update_stats_button = QPushButton("Оновити статистику")
        self.update_stats_button.clicked.connect(self.updateStatistics)

        layout.addWidget(self.update_stats_button)

        # Виведення статистики
        self.days_list = QListWidget()
        layout.addWidget(self.days_list)

        self.tab_statistics.setLayout(layout)

    def updateStatistics(self):
        start_date = self.start_date_input.date().toString("yyyy-MM-dd")
        end_date = self.end_date_input.date().toString("yyyy-MM-dd")

        # Отримуємо дати радощів за вказаний період
        self.cursor.execute("""
            SELECT DISTINCT date FROM joys
            WHERE date BETWEEN ? AND ?
        """, (start_date, end_date))

        dates_with_joys = self.cursor.fetchall()

        # Оновлюємо список з днями
        self.days_list.clear()
        for date in dates_with_joys:
            self.days_list.addItem(date[0])

    def initFieldTab(self):
        layout = QVBoxLayout()
        self.field_canvas = QLabel()
        self.field_canvas.setStyleSheet("background-color: #E6EEE6;")
        layout.addWidget(self.field_canvas)
        self.tab_field.setLayout(layout)

    def saveJoy(self):
        text = self.joy_text.toPlainText().strip()
        if text:
            date = QDate.currentDate().toString("yyyy-MM-dd")
            self.cursor.execute("INSERT INTO joys (text, date) VALUES (?, ?)", (text, date))
            self.conn.commit()
            self.joy_text.clear()
            self.loadArchive()
            self.addFlower()
        else:
            QMessageBox.warning(self, "Помилка", "Будь ласка, введіть текст радості!")

    def showRandomJoy(self):
    # SQL-запит для вибору випадкової радості
        self.cursor.execute("SELECT text FROM joys ORDER BY RANDOM() LIMIT 1")
        row = self.cursor.fetchone()
    
    # Якщо радість знайдено, показуємо повідомлення
        if row:
            QMessageBox.information(self, "Щасливий спогад", row[0])
        else:
        # Якщо архів радощів порожній
            QMessageBox.information(self, "Щасливий спогад", "У вас поки немає радощів!")

    def loadArchive(self):
        self.archive_list.clear()
        self.cursor.execute("SELECT text FROM joys ORDER BY id DESC")
        joys = self.cursor.fetchall()
        for joy in joys:
            self.archive_list.addItem(joy[0])

    def addFlower(self):
        flower_text = "🌻"
        flower_label = QLabel(flower_text, self.field_canvas)
        flower_label.setStyleSheet("font-size: 24px;")
        canvas_width = self.field_canvas.width()
        canvas_height = self.field_canvas.height()
        x = random.randint(0, canvas_width - 50)
        y = random.randint(0, canvas_height - 50)
        flower_label.move(x, y)
        flower_label.show()

    def addReminder(self):
        text = self.reminder_text.text().strip()
        time = self.reminder_time.time().toString("HH:mm")
        if text:
            self.cursor.execute("INSERT INTO reminders (text, time) VALUES (?, ?)", (text, time))
            self.conn.commit()
            self.reminder_list.addItem(f"{time} - {text}")
            self.reminder_text.clear()
        else:
            QMessageBox.warning(self, "Помилка", "Будь ласка, введіть текст нагадування!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ZatishokApp()
    window.show()
    sys.exit(app.exec())