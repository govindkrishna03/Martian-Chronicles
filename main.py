import requests
import os
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton, QListWidget, QListWidgetItem, QFrame, QFileDialog
from PyQt5.QtGui import QPixmap, QIcon, QPainter, QBrush, QPalette
from PyQt5.QtCore import Qt, QSize
import sys

class MarsRoverApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Martian Chronicles')
        self.setGeometry(100, 100, 800, 600)

    
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setBrush(QPalette.Window, QBrush(QPixmap("background.jpeg")))
        self.setPalette(palette)

        self.container = QFrame(self)
        self.container.setFrameShape(QFrame.StyledPanel)
        self.container.setFrameShadow(QFrame.Raised)

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)

        self.photo_list = QListWidget(self.container)
        self.photo_list.itemClicked.connect(self.display_photo)

        self.load_button = QPushButton('Load Photos', self.container)
        self.load_button.clicked.connect(self.load_photos)
        

        self.download_button = QPushButton('Download Image', self.container)
        self.download_button.clicked.connect(self.download_image)
        self.download_button.setEnabled(False)

        layout = QVBoxLayout(self.container)
        layout.addWidget(self.photo_list)
        layout.addWidget(self.load_button)
        layout.addWidget(self.download_button)


        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.image_label)
        main_layout.addWidget(self.container)

    def load_photos(self):
    
        api_key = 'HUxVxTUxiILP8gSlhiUMmgpnIzN3YdvGP4I03Kap'

        
        url = f'https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?earth_date=2015-6-3&api_key={api_key}'
        response = requests.get(url)
        data = response.json()
        photos = data['photos']

        for photo in photos:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, photo['img_src'])
            pixmap = QPixmap()
            pixmap.loadFromData(requests.get(photo['img_src']).content)
            item.setIcon(QIcon(pixmap))
            item.setText(f"Caption: {photo['camera']['full_name']}\nCamera Type: {photo['camera']['name']}\nLocation: {photo['rover']['name']}")
            self.photo_list.addItem(item)

        self.load_button.hide()
        self.download_button.setEnabled(True)

    def display_photo(self, item):
        pixmap = item.icon().pixmap(QSize(640, 480))
        self.image_label.setPixmap(pixmap)
        self.selected_photo_url = item.data(Qt.UserRole)

    def download_image(self):
        if not hasattr(self, 'selected_photo_url'):
            return
        
        filename, _ = QFileDialog.getSaveFileName(self, 'Save Image', '', 'JPEG files (*.jpg);;All files (*.*)')
        if not filename:
            return

        response = requests.get(self.selected_photo_url)
        with open(filename, 'wb') as f:
            f.write(response.content)
            f.close()

        print(f'Successfully downloaded image to {filename}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MarsRoverApp()
    window.show()
    sys.exit(app.exec_())