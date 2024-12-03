import os
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, \
    QLabel, QFileDialog, QMessageBox, QDialog
from PyQt6.QtWidgets import (
    QListWidget, QListWidgetItem, QTextEdit
)
from datasave import add_request, add_chat_path, delete_chat_path, load_chats_from_base
from gradio_client import Client
from groq_server import generategroq


# Запуск сервера
# sudo nano /etc/serv.py
# python3 /etc/serv.py
class ImageGeneratorApp(QDialog):  # Доп окно генерация
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Generator Interface")
        self.setGeometry(100, 100, 600, 600)

        # Основной контейнер
        main_layout = QVBoxLayout(self)

        # Поле ввода prompt
        prompt_layout = QHBoxLayout()
        self.prompt_input = QLineEdit()
        self.prompt_input.setPlaceholderText("Введите prompt для генерации изображения...")
        prompt_layout.addWidget(self.prompt_input)

        # Кнопка генерации изображения
        generate_button = QPushButton("Сгенерировать изображение")
        generate_button.clicked.connect(self.generate_image)
        prompt_layout.addWidget(generate_button)
        main_layout.addLayout(prompt_layout)

        # QLabel для отображения сгенерированного изображения
        self.image_display = QLabel("Здесь будет отображаться изображение")
        self.image_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_display.setStyleSheet("border: 1px solid black;")  # Рамка вокруг изображения
        main_layout.addWidget(self.image_display)

        # Кнопка для сохранения изображения
        save_button = QPushButton("Сохранить изображение")
        save_button.clicked.connect(self.save_image)
        main_layout.addWidget(save_button)

        # Переменная для хранения пути к сгенерированному изображению
        self.generated_image_path = None

    def generate_image(self):
        # Получаем prompt и вызываем функцию generateflux для генерации изображения
        prompt = self.prompt_input.text()
        if prompt.strip() == "":
            QMessageBox.warning(self, "Ошибка", "Введите prompt для генерации изображения.")
            return

        # Генерация изображения и отображение его в QLabel
        client = Client("lalashechka/FLUX_1")
        result = client.predict(
            prompt=prompt,
            task="FLUX.1 [schnell]",
            api_name="/flip_text"
        )
        # result = r'"C:\Users\radom\Downloads\asd.webp"'
        self.generated_image_path = result  # итоговый путь для изображения
        print(self.generated_image_path)
        if self.generated_image_path:
            pixmap = QPixmap(self.generated_image_path)
            self.image_display.setPixmap(pixmap.scaled(
                self.image_display.size(), Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))

    def save_image(self):
        # Сохранение изображения на компьютер
        if not self.generated_image_path:
            QMessageBox.warning(self, "Ошибка", "Сначала сгенерируйте изображение.")
            return

        save_path, _ = QFileDialog.getSaveFileName(self, "Сохранить изображение", "", "Images (*.webp *.png *.jpg)")
        if save_path:
            pixmap = QPixmap(self.generated_image_path)
            pixmap.save(save_path)
            QMessageBox.information(self, "Сохранение", "Изображение успешно сохранено!")


class ChatApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat Interface")
        self.setGeometry(100, 100, 800, 600)

        # Счетчик для названий чатов
        try:
            with open("counter_chat.txt", 'r') as file:
                self.chat_counter = int(file.read().strip())
        except Exception:
            self.chat_counter = 1
        print(self.chat_counter)

        # Основной контейнер
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # Боковая панель с чатами и кнопками
        sidebar_layout = QVBoxLayout()
        self.chat_list = QListWidget()
        self.chat_list.setFixedWidth(200)
        self.chat_list.itemClicked.connect(self.load_chat)
        sidebar_layout.addWidget(self.chat_list)

        # Кнопка добавления чата
        add_chat_button = QPushButton("Добавить чат")
        add_chat_button.clicked.connect(self.add_chat)
        sidebar_layout.addWidget(add_chat_button)

        # Кнопка удаления чата
        delete_chat_button = QPushButton("Удалить чат")
        delete_chat_button.clicked.connect(self.delete_chat)
        sidebar_layout.addWidget(delete_chat_button)

        main_layout.addLayout(sidebar_layout)

        # выбор режима
        self.mode_button = QPushButton("Генератор картинок", self)
        self.mode_button.clicked.connect(self.switch_mode)
        self.mode_button.setStyleSheet(
            "QPushButton {"
            "color: white;"  # Цвет текста
            "background-color: #484064;"  # Цвет фона кнопки (например, синий)
            "border-radius: 5px;"  # Скругленные края
            "padding: 5px;"  # Отступы
            "}"
            "QPushButton:hover {"
            "background-color: #332F42;"  # Цвет при наведении
            "}"
        )
        sidebar_layout.addWidget(self.mode_button)

        # Переменная для отслеживания текущего режима
        self.is_text_mode = True

        # Контейнер для области чата
        self.chat_area = QVBoxLayout()
        main_layout.addLayout(self.chat_area)

        # Титульная страница
        self.welcome_page = QWidget()
        welcome_layout = QVBoxLayout(self.welcome_page)
        welcome_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label = QLabel("Добро пожаловать в Chat Interface")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        welcome_layout.addWidget(welcome_label)

        start_chat_button = QPushButton("Начать новый чат")
        start_chat_button.clicked.connect(self.add_chat)
        welcome_layout.addWidget(start_chat_button)

        self.chat_area.addWidget(self.welcome_page)

        # QLabel для отображения выбранного чата
        self.selected_chat_label = QLabel("")
        self.selected_chat_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.selected_chat_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.chat_area.addWidget(self.selected_chat_label)

        # Поле для отображения сообщений (скрыто пока)
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setVisible(False)
        self.chat_area.addWidget(self.chat_display)

        # Поле для ввода запроса и кнопка отправки (скрыты пока)
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Введите запрос...")
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)

        self.send_button = QPushButton("Отправить")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        self.input_container = QWidget()
        self.input_container.setLayout(input_layout)
        self.input_container.setVisible(False)
        self.chat_area.addWidget(self.input_container)

        self.load_old_chats()

        # начальный чат в боковую панель
        # self.add_chat()

    def add_chat(self):
        # новый чат в список и автоматически переходит к нему
        chat_name = f"{self.chat_counter}..."
        add_chat_path(int(chat_name[:-3]), f"{chat_name}.txt")
        self.chat_counter += 1
        with open("counter_chat.txt", 'w') as file:
            file.write(str(self.chat_counter) + "\n")
        item = QListWidgetItem(chat_name)
        self.chat_list.addItem(item)
        self.chat_list.setCurrentItem(item)
        self.load_chat(item)

    def delete_chat(self):
        # Удаляет выбранный чат из списка
        selected_item = self.chat_list.currentItem()
        if selected_item:
            reply = QMessageBox.question(
                self, "Подтверждение удаления",
                f"Вы уверены, что хотите удалить {selected_item.text()}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                delete_chat_path(selected_item.text()[:2])

                file_name = f"{selected_item.text()}.txt"
                if os.path.isfile(file_name):
                    os.remove(file_name)
                    print(f"Файл '{file_name}' успешно удален.")
                else:
                    print(f"Файл '{file_name}' не существует.")

                row = self.chat_list.row(selected_item)
                self.chat_list.takeItem(row)
                self.show_welcome_page()
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите чат для удаления")

    def load_old_chats(self):
        # загрузка сообщений старых
        rows = load_chats_from_base()
        if rows:
            for row in rows:
                print(f"chat_id: {row[0]}, chat_path: {row[1]}")
                chat_name = f"{row[0]}..."
                item = QListWidgetItem(chat_name)
                self.chat_list.addItem(item)
        else:
            self.chat_counter = 1
        self.show_welcome_page()

    def load_chat(self, item):
        # загрузка сообщений
        self.chat_display.setVisible(True)
        self.input_container.setVisible(True)
        self.welcome_page.setVisible(False)

        # Обнова QLabel
        self.selected_chat_label.setText(f"Выбран: {item.text()}")

        self.chat_display.clear()

        file_name = f"{item.text()}.txt"
        if os.path.exists(file_name):
            with open(file_name, 'r') as file:
                text_all = file.read()
            self.chat_display.append(text_all)
            print(f"Чат успешно загружен из файла {file_name}.")
        else:
            print(f"Файл {file_name} не существует.")

    def show_welcome_page(self):
        # титульную страницу, если нет чата
        self.selected_chat_label.setText("")
        self.chat_display.setVisible(False)
        self.input_container.setVisible(False)
        self.welcome_page.setVisible(True)

    def send_message(self):
        # отправляет сообщение из поля ввода и добавляет его в чат
        user_message = self.input_field.text().strip()

        if user_message:
            self.chat_display.append(f"Вы: {user_message}" + "\n")
            self.input_field.clear()

            response_text = self.receive_response(user_message)
            self.chat_display.append(f"AI: {response_text}" + "\n")
            add_request(self.chat_list.currentItem().text()[:-2], user_message, response_text, "text")

        text_all = self.chat_display.toPlainText()
        file_name = f"{self.chat_list.currentItem().text()}.txt"
        print(file_name)
        with open(file_name, 'w') as file:
            file.write(text_all + "\n")
        print(f"Чат успешно сохранен в файл {file_name}.")

    def receive_response(self, user_message):
        # нейронка
        if self.is_text_mode:
            response_text = generategroq(user_message)
            return response_text

    def switch_mode(self):
        # Переключаем режим и обновляем текст кнопки
        self.image_generator_window = ImageGeneratorApp()
        self.image_generator_window.exec()  # Открытие окна как диалогового


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatApp()
    window.show()
    sys.exit(app.exec())
