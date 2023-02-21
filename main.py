from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow ,QLineEdit,QMessageBox
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QListWidget, QListWidgetItem, QFileDialog
import sys,requests
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QBuffer, QByteArray, QIODevice

from PyQt5.QtCore import Qt, QSize
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage


class MarsRover(QMainWindow):
    def __init__(self):
        super(MarsRover,self).__init__()
        loadUi('main.ui',self)

        self.image_label=self.findChild(QLabel,"label_4")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.photo_list =self.findChild(QListWidget,"listWidget")
        self.loadbutton=self.findChild(QPushButton,"pushButton")
        self.downloadbutton=self.findChild(QPushButton,"pushButton_2")
        self.sendbutton=self.findChild(QPushButton,"pushButton_3")
        self.subject=self.findChild(QLineEdit,"lineEdit_2")
        self.attachbutton=self.findChild(QPushButton,"pushButton_4")
        self.recipients = self.findChild(QLineEdit,"lineEdit")
        

        self.photo_list.itemClicked.connect(self.display_photo)
        self.loadbutton.clicked.connect(self.load_photos)
        self.downloadbutton.clicked.connect(self.download_image)
        self.attachbutton.clicked.connect(self.attach_image)
        self.sendbutton.clicked.connect(self.send_email)
        self.downloadbutton.setEnabled(False)


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

        self.loadbutton.hide()
        self.downloadbutton.setEnabled(True)


    def display_photo(self, item):
        pixmap = item.icon().pixmap(QSize(640, 480))
        self.image_label.setPixmap(pixmap)
        self.selected_photo_url = item.data(Qt.UserRole)

    def download_image(self):
        if not hasattr(self, 'selected_photo_url'):
            return

        response = requests.get(self.selected_photo_url)
        self.selected_photo_data = response.content

        filename, _ = QFileDialog.getSaveFileName(self, 'Save Image', '', '')
        if not filename:
            return

        with open(filename, 'wb') as f:
            f.write(self.selected_photo_data)

        print(f'Successfully downloaded image to {filename}')

    def attach_image(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Open File', '', '')

        if filename:
            pixmap = QPixmap(filename)
            self.selected_image = pixmap.toImage()
            self.attachbutton.setText('Attached')

    def send_email(self):
        recipients = self.recipients.text().split(',')
        subject = 'MarsRover'
        

        if not recipients:
            QMessageBox.warning(self, 'Error', 'Please enter at least one recipient.')
            return

        if not subject:
            QMessageBox.warning(self, 'Error', 'Please enter a subject.')
            return

        if not self.selected_image:
            QMessageBox.warning(self, 'Error', 'Please attach an image.')
            return

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login('gk5974518@gmail.com', 'zfzjrlzmxkerqsvs')

            msg = MIMEMultipart()
            msg['From'] = 'gk5974518@gmail.com'
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject


            image_bytes = QByteArray()
            buffer = QBuffer(image_bytes)
            buffer.open(QIODevice.WriteOnly)
            self.selected_image.save(buffer, "JPEG")
            img = MIMEImage(image_bytes)
            img.add_header('Content-Disposition', 'attachment', filename='')
            msg.attach(img)

            server.sendmail('gk5974518@gmail.com', recipients, msg.as_string())
            server.quit()

            QMessageBox.information(self, 'Success', 'Email sent successfully.')
            self.close()

        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Error sending email: {e}')

            server.quit()

            self.close()
    
    

    



if __name__ == '__main__':
    app =QApplication(sys.argv)
    window = MarsRover()
    window.show()
    app.exec_()