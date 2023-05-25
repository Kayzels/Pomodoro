import sys
from pathlib import Path
import ctypes
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QApplication
from mainWindow import Ui_MainWindow

# constants
APP_NAME = "Pomo!"
APP_ID = "pomodoro.v1"
WORK_MIN = 30
SHORT_BREAK_MIN = 5
LONG_BREAK_MIN = 30
LONG_BREAK_INTERVAL = 4

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.startButton.clicked.connect(self.startTimer)
        self.resetButton.clicked.connect(self.resetTimer)

        self.workTimer = QTimer()
        self.workTimer.setInterval(1000) # 1 second
        self.workTimer.timeout.connect(self.updateWork)
        self.breakTimer = QTimer()
        self.breakTimer.setInterval(1000) # 1 second
        self.breakTimer.timeout.connect(self.updateBreak)

        self._setDefaults()

    def startTimer(self):
        self.startWork()
        self.startButton.setEnabled(False)

    def resetTimer(self):
        self._setDefaults()

    def startWork(self):
        self.modeLabel.setText("Work")
        self.modeLabel.setStyleSheet("color: red")
        self.timeLCD.display(f"{WORK_MIN:02d}:00")
        self.workSessions += 1
        self.timeRemainingSec = WORK_MIN * 60
        self.workTimer.start()

    def updateWork(self):
        self.updateTimeDisplay()
        if self.timeRemainingSec == 0:
            self.checkmarks += "✅"
            self.countLabel.setText(self.checkmarks)
            self.workTimer.stop()
            self.startBreak()

    def startBreak(self):
        if (self.workSessions % LONG_BREAK_INTERVAL == 0):
            self.modeLabel.setText("Long Break")
            duration = LONG_BREAK_MIN
            self.modeLabel.setStyleSheet("color: #80c342")
        else:
            self.modeLabel.setText("Short Break")
            duration = SHORT_BREAK_MIN
            self.modeLabel.setStyleSheet("color: #53baff")
        self.timeLCD.display(f"{duration:02d}:00")
        self.timeRemainingSec = duration * 60
        self.breakTimer.start()

    def updateBreak(self):
        self.updateTimeDisplay()
        if self.timeRemainingSec == 0:
            self.breakTimer.stop()
            self.startWork()

    def updateTimeDisplay(self):
        self.timeRemainingSec -= 1
        mins, secs = secToMinSec(self.timeRemainingSec)
        mins = f"{mins:02d}"
        secs = f"{secs:02d}"
        remainingText = mins + ":" + secs
        self.timeLCD.display(remainingText)

    def _setDefaults(self):
        self.workSessions = 0
        self.checkmarks = ""
        self.countLabel.setText(self.checkmarks)
        self.startButton.setEnabled(True)
        self.modeLabel.setText("Let's get working")
        self.modeLabel.setStyleSheet("color: #f0f0f0")
        self.workTimer.stop()
        self.breakTimer.stop()
        self.timeLCD.display("30:00")

def secToMinSec(seconds: int) -> tuple[int, int]:
    mins = seconds // 60
    seconds = seconds - (mins * 60)
    return (mins, seconds)

def run():
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setWindowIcon(QIcon("tomato.png"))
    app.setStyleSheet(Path('styles.qss').read_text())
    window = MainWindow()
    window.show()
    app.exec()

if __name__ == "__main__":
    sys.exit(run())