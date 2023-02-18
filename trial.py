import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import requests
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon, QPainter, QBrush, QPalette
from PyQt5.QtWidgets import (QApplication, QLabel, QVBoxLayout, QWidget, QPushButton, QListWidget,
                             QListWidgetItem, QFrame, QFileDialog, QHBoxLayout, QLineEdit,QMessageBox)


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
        self.email_label = QLabel('Recipient Email Address:', self.container)
        self.email_input = QLineEdit(self.container)

        self.send_button = QPushButton('Send Email', self.container)
        self.send_button.clicked.connect(self.send_email)
        self.send_button.setEnabled(False)

        self.photo_list = QListWidget(self.container)
        self.photo_list.itemClicked.connect(self.display_photo)

        self.load_button = QPushButton('Load Photos', self.container)
        self.load_button.clicked.connect(self.load_photos)

        self.download_button = QPushButton('Download Image', self.container)
        self.download_button.clicked.connect(self.download_image)
        self.download_button.setEnabled(False)

        self.recipient_edit = QLineEdit(self.container)
        self.recipient_edit.setPlaceholderText('Enter recipient email address')

        self.send_button = QPushButton('Send Email', self.container)
        self.send_button.clicked.connect(self.send_email)
        self.send_button.setEnabled(False)

        layout = QVBoxLayout(self.container)
        layout.addWidget(self.photo_list)
        layout.addWidget(self.load_button)
        layout.addWidget(self.download_button)
        layout.addWidget(self.recipient_edit)
        layout.addWidget(self.send_button)

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
        self.send_button.setEnabled(True)

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



    def send_email(self):
        sender = 'krishnago123@yahoo.com' 
        recipient = self.recipient_edit.text()
        if not recipient:
            QMessageBox.warning(self, 'Warning', 'Please enter a recipient email address.')
            return

        if not hasattr(self, 'selected_photo_url'):
            QMessageBox.warning(self, 'Warning', 'Please select a photo to download.')
            return

       
        response = requests.get(self.selected_photo_url)
        if response.status_code != 200:
            QMessageBox.warning(self, 'Warning', 'Failed to download image.')
            return

        image_data = response.content

        
        message = MIMEMultipart()
        message['From'] = 'krishnago123@yahoo.com'
        message['To'] = 'govindkrishna28@gmail.com'
        message['Subject'] = 'Mars Rover Photo'

        
        image = MIMEImage(image_data, name=os.path.basename(self.selected_photo_url))
        message.attach(image)

        
        body = 'Enjoy this photo from the Mars Rover!'
        message.attach(MIMEText(body))

        smtp_server = smtplib.SMTP('smtp.mail.yahoo.com', 587)
        smtp_server.starttls()
        smtp_server.login(sender, 'leomessi@10') 
        smtp_server.sendmail(sender, recipient, message.as_string())
        smtp_server.quit()

        QMessageBox.information(self, 'Success', f'Successfully sent email to {recipient}.')



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MarsRoverApp()
    window.show()
    sys.exit(app.exec_())