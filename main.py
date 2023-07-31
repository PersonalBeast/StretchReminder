import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, 
                             QLabel, QGridLayout, QInputDialog, QMessageBox,
                             QSystemTrayIcon, QAction, QMenu)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import  QIcon, QCursor
from plyer import notification
from datetime import datetime, timedelta
import winsound
import traceback
import logging

# Set up logging to a file for uncaught exceptions
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

def log_uncaught_exceptions(ex_cls, ex, tb):
    # This function handles uncaught exceptions and logs them to a file
    text = '{}: {}:\n'.format(ex_cls.__name__, ex)
    text += ''.join(traceback.format_tb(tb))
    logging.error(text)

# Set the function to handle uncaught exceptions
sys.excepthook = log_uncaught_exceptions


# Define the style of the task button (close and minimize)
TASK_BUTTON_STYLE = """
QPushButton {
    background-color: transparent; 
}
QPushButton:hover {
    background-color: red;
    border-radius: 5px;
}
"""

# Define the style of the time button (15, 30, 60 minutes and Custom)
TIME_BUTTON_STYLE = """
QPushButton {
    background-color: green; 
    border: 1px solid green;
    border-radius: 15px;
    min-width: 80px;
    max-width: 80px;
    min-height: 30px;
    max-height: 30px;
}
QPushButton:hover {
    background-color: darkgreen;
    border: 1px solid darkgreen;
}
"""

# Define the style of the stop button
STOP_BUTTON_STYLE = """
QPushButton {
    background-color: red; 
    border: 1px solid red;
    border-radius: 15px;
    max-height: 30px;
    min-height: 30px;
    max-width: 190px;
    min-width: 190px;
}
QPushButton:hover {
    background-color: darkred;
    border: 1px solid darkred;
}
"""

class MyMessageBox(QMessageBox):
    # This class extends QMessageBox to customize its behavior
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def closeEvent(self, event):
        # Overriding the close event to ignore it and hide the message box instead
        event.ignore()
        self.hide()

class MainWindow(QMainWindow):
    # This class extends QMainWindow and sets up the main application window
    def __init__(self):
        super(MainWindow, self).__init__()
        # Set the window title and size
        self.setWindowTitle("Stretch Time!")
        self.setGeometry(750, 300, 300, 300)
        self.setFixedSize(250, 200)
        # Remove the window frame
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # Define the system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon('components/icon.ico'))

        # Define the context menu for the system tray icon
        show_action = QAction("Show", self)
        hide_action = QAction("Hide", self)
        quit_action = QAction("Exit", self)

        # Connect actions to functions
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(QApplication.instance().quit)

        # Add actions to a menu
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)

        # Connect the system tray icon to show the window when clicked
        self.tray_icon.activated.connect(self.icon_clicked)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
       
        # Create close and minimize buttons
        self.close_button = self.task_button('components/close.ico', self.close)
        self.minimize_button = self.task_button('components/minimize.ico', self.showMinimized)

        # Create time buttons
        self.time_button_15 = self.time_button('15 minutes', self.start_timer, 15)
        self.time_button_30 = self.time_button('30 minutes', self.start_timer, 30)
        self.time_button_60 = self.time_button('60 minutes', self.start_timer, 60)
        self.time_button_custom = self.time_button('Custom', self.custom_time)

        # Create stop button
        self.stop_button = self.stop_button('Stop', self.stop_timer)
        self.stop_button.setStyleSheet(STOP_BUTTON_STYLE)
        
        # Create a message box instance as a class member
        self.msg_box = MyMessageBox(self)
        self.msg_box.setWindowTitle("Reminder")
        self.msg_box.setText("Time to get up and stretch!")
        self.msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.StandardButton.Abort)
        stop_button = self.msg_box.button(QMessageBox.StandardButton.Abort)
        stop_button.setText("Stop")
        
        # Set the message box to always stay on top
        self.msg_box.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        self.msg_box.setWindowIcon(QIcon('components/icon.ico'))

        # Connect the button clicked signal to the appropriate slot
        self.msg_box.buttonClicked.connect(self.handle_msg_box)

        # Create title
        self.title = QLabel("Stretch Reminder")
        self.title.setStyleSheet("font: bold 20px;") 
        self.title.setAlignment(Qt.AlignCenter)  

        # Layout for buttons
        window_content = QWidget(self)
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addStretch()  
        self.buttons_layout.addWidget(self.minimize_button)
        self.buttons_layout.addWidget(self.close_button)
        self.buttons_layout.setContentsMargins(10, 10, 10, 10)

        self.title_layout = QHBoxLayout()
        self.title_layout.addWidget(self.title, alignment=Qt.AlignCenter)

        self.time_buttons_layout = QGridLayout() 
        self.time_buttons_layout.addWidget(self.time_button_15, 0, 0)
        self.time_buttons_layout.addWidget(self.time_button_30, 0, 1)
        self.time_buttons_layout.addWidget(self.time_button_60, 1, 0)
        self.time_buttons_layout.addWidget(self.time_button_custom, 1, 1)
        self.time_buttons_layout.setHorizontalSpacing(10)
        self.time_buttons_layout.setVerticalSpacing(10)

        self.stop_button_layout = QHBoxLayout()
        self.stop_button_layout.addWidget(self.stop_button)

        main_layout = QVBoxLayout(window_content)
        main_layout.addLayout(self.buttons_layout)
        main_layout.addLayout(self.title_layout)
        main_layout.addLayout(self.time_buttons_layout)
        main_layout.addLayout(self.stop_button_layout)
        main_layout.setContentsMargins(10, 0, 10, 10)

        window_content.setLayout(main_layout)
        self.setCentralWidget(window_content)

    def task_button(self, icon_path, callback):
        # This function creates a task button (close or minimize) with an icon and a callback function
        button = QPushButton()
        button.setIcon(QIcon(icon_path))
        button.setIconSize(QSize(20, 20))  
        button.setMaximumWidth(30)
        button.setStyleSheet(TASK_BUTTON_STYLE)
        button.setCursor(QCursor(Qt.PointingHandCursor))
        if callback == self.close:
            button.clicked.connect(QApplication.instance().quit)
        else:
            button.clicked.connect(callback)
        return button

    def time_button(self, text, callback, minutes=None):
        # This function creates a time button (15, 30, 60 minutes or Custom) with a text, a callback function and a number of minutes
        button = QPushButton(text)
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.setStyleSheet(TIME_BUTTON_STYLE)
        if text == 'Custom':
            button.clicked.connect(callback)
        else:
            button.clicked.connect(lambda: callback(minutes))
        return button

    def stop_button(self, text, callback):
        # This function creates a stop button with a text and a callback function
        button = QPushButton(text)
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(callback)
        return button
    
    def icon_clicked(self, reason):
        # This function handles the click event on the system tray icon to show the window
        if reason == QSystemTrayIcon.Trigger:
            self.show()

    def start_timer(self, minutes):
        # This function starts a timer for a specified number of minutes and shows a system notification
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
        self.timer = QTimer()
        self.timer.timeout.connect(self.timer_end)
        self.timer.start(minutes * 60 * 1000)

        # Calculate next notification time
        current_time = datetime.now()
        next_notification_time = current_time + timedelta(minutes=minutes)

        # Format the time as "x minutes" and "AM/PM"
        next_notification_time_str = next_notification_time.strftime("%I:%M %p")

        # Show system notification
        notification_title = "Stretch Reminder"
        notification_message = f"Timer is set for every {minutes} minutes. Your next notification will be at {next_notification_time_str}."
        notification.notify(title=notification_title, message=notification_message)
        self.hide() 
    
    def closeEvent(self, event):
        # Override the window's closeEvent method to hide the window instead of closing it
        event.ignore()
        self.hide()

    def timer_end(self):
        # This function handles the end of the timer by showing a reminder message box and playing a sound
        self.msg_box.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool)
        self.msg_box.show()
        self.msg_box.raise_()
        self.msg_box.activateWindow()
        winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)
      
    def handle_msg_box(self, button):
        # This function handles the click event on the reminder message box to stop the timer or set the next reminder
        if self.msg_box.standardButton(button) == QMessageBox.Ok:
            # Calculate next notification time
            current_time = datetime.now()
            minutes = self.timer.interval() // (60 * 1000)  
            next_notification_time = current_time + timedelta(minutes=minutes)

            # Format the time as "x minutes" and "AM/PM"
            next_notification_time_str = next_notification_time.strftime("%I:%M %p")

            # Show system notification for the next reminder time
            notification_title = "Stretch Reminder"
            notification_message = f"Your next reminder will be at {next_notification_time_str}."
            notification.notify(title=notification_title, message=notification_message)
        elif self.msg_box.standardButton(button) == QMessageBox.Abort:
            self.stop_timer()
        
    def stop_timer(self):
        # This function stops the timer and shows a message box that the timer has stopped
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
            self.msg_box.hide()  # Hide the reminder window
            QMessageBox.information(self, "Stopped", "Timer has stopped")
            self.show()  # Show the main window

    def custom_time(self):
        # This function shows a dialog to input a custom number of minutes and starts a timer for that amount
        num, ok = QInputDialog.getInt(self, 'Custom Time', 'Enter the number of minutes:')
        if ok:
            self.start_timer(num)
              
def main():
    # This is the main function that creates the application and the main window and starts the event loop
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False) 
    # Set the application icon
    app.setWindowIcon(QIcon('components/mainIcon.ico'))
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
