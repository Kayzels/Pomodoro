import sys
from pathlib import Path
import ctypes
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QApplication
from mainWindow import Ui_MainWindow
from constants import *

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.startButton.clicked.connect(self.startTimer)
        self.resetButton.clicked.connect(self.resetTimer)
        self.increaseButton.clicked.connect(self.increaseTime)
        self.decreaseButton.clicked.connect(self.decreaseTime)  # Connect decreaseButton
        self.workTimer = QTimer()
        self.workTimer.setInterval(1000)
        self.workTimer.timeout.connect(self.updateWork)
        self.breakTimer = QTimer()
        self.breakTimer.setInterval(1000)
        self.breakTimer.timeout.connect(self.updateBreak)
        self.countdownStopped = True
        self.timeSet = WORK_MIN * 60
        self.countdownSec = self.timeSet
        self._setDefaults()
        

    def startTimer(self):
        self.startWork()
        self.startButton.setEnabled(False)
        self.countdownStopped = False  # Countdown started, set countdownStopped to False

    def resetTimer(self):
        self._setDefaults()
        mins, secs = divmod(self.timeSet, 60)
        self.timeLCD.display(f"{mins:02d}:{secs:02d}")

    def startWork(self):
        self.modeLabel.setText("Work")
        self.modeLabel.setStyleSheet("color: red")
        self.timeRemainingSec = self.countdownSec  # Use the selected time as the starting time
        mins, secs = divmod(self.timeRemainingSec, 60)
        remainingText = f"{mins:02d}:{secs:02d}"
        self.timeLCD.display(remainingText)
        self.workSessions += 1
        self.workTimer.start()

    def updateWork(self):
        self.updateTimeDisplay()
        if self.timeRemainingSec == 0:
            self.checkmarks += "✅"
            self.countLabel.setText(self.checkmarks)
            self.workTimer.stop()
            self.startBreak()

    def startBreak(self):
        break_type = self.workSessions % LONG_BREAK_INTERVAL
        break_info = {
            0: ("Long Break", LONG_BREAK_MIN, "#80c342"),
            1: ("Short Break", SHORT_BREAK_MIN, "#53baff")
        }
        label, duration, color = break_info.get(break_type, ("Unknown", 0, "#000000"))
        self.modeLabel.setText(label)
        self.modeLabel.setStyleSheet(f"color: {color}")
        self.timeLCD.display(f"{duration:02d}:00")
        self.timeRemainingSec = duration * 60
        self.countdownSec = duration * 60
        self.breakTimer.start()

    def updateBreak(self):
        self.updateTimeDisplay()
        if self.timeRemainingSec == 0:
            self.breakTimer.stop()
            self.startWork()

    def updateTimeDisplay(self):
        if not self.countdownStopped:  # Only update time if countdown is not stopped
            self.timeRemainingSec -= 1
        mins, secs = divmod(self.timeRemainingSec, 60)
        mins = f"{mins:02d}"
        secs = f"{secs:02d}"
        remainingText = mins + ":" + secs
        self.timeLCD.display(remainingText)

    def decreaseTime(self):
        if self.countdownStopped:
            self.timeSet -= 60  # Decrease time by a minute
            if self.timeSet < 60:  # Check if timeSet is less than 1 minute
                self.timeSet = 60  # Set timeSet to 1 minute
            mins, secs = divmod(self.timeSet, 60)
            self.countdownSec = self.timeSet
            self.timeLCD.display(f"{mins:02d}:{secs:02d}")  # Update time display

    def increaseTime(self):
        if self.countdownStopped:
            self.timeSet += 60  # Increase time by a minute
            if self.timeSet > 120 * 60:  # Check if timeSet exceeds 120 minutes
                self.timeSet = 120 * 60  # Set timeSet to 120 minutes
            mins, secs = divmod(self.timeSet, 60)
            self.countdownSec = self.timeSet
            self.timeLCD.display(f"{mins:02d}:{secs:02d}")  # Update time display

    def _setDefaults(self):
        self.workSessions = 0
        self.checkmarks = ""
        self.countLabel.setText(self.checkmarks)
        self.startButton.setEnabled(True)
        self.modeLabel.setText("Let's get working")
        self.modeLabel.setStyleSheet("color: #f0f0f0")
        self.workTimer.stop()
        self.breakTimer.stop()
        mins = f"{WORK_MIN:02d}"
        secs = f"{0:02d}"
        remainingText = mins + ":" + secs
        self.timeLCD.display(remainingText)
        self.countdownStopped = True  # Set countdownStopped to True on reset
        self.countdownSec = WORK_MIN * 60  # Reset countdownSec to initial work duration

def run():
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setWindowIcon(QIcon("tomato.png"))
    app.setStyleSheet(Path('styles.qss').read_text())
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run()
