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

        # Connect button signals to their respective functions
        self.startButton.clicked.connect(self.startTimer)
        self.resetButton.clicked.connect(self.resetTimer)
        self.increaseButton.clicked.connect(self.increaseTime)
        self.decreaseButton.clicked.connect(self.decreaseTime)

        # Set up timers for work and break intervals
        # Set up variables
        self.workTimer = QTimer()
        self.workTimer.setInterval(1000)  # 1 second
        self.workTimer.timeout.connect(self.updateWork)
        self.breakTimer = QTimer()
        self.breakTimer.setInterval(1000)  # 1 second
        self.breakTimer.timeout.connect(self.updateBreak)
        self.countdownStopped = True
        self.timeSet = WORK_MIN * 60
        self.countdownSec = self.timeSet
        self._setDefaults()

    def startTimer(self):
        # Start the work timer
        self.startWork()
        # Countdown started, set countdownStopped to False
        # Disable the start button and hide increase/decrease buttons
        self.startButton.setEnabled(False)
        self.countdownStopped = False
        self.decreaseButton.hide()
        self.increaseButton.hide()

    def resetTimer(self):
        # Reset the timer to its default values
        self._setDefaults()
        mins, secs = divmod(self.timeSet, 60)
        self.timeLCD.display(f"{mins:02d}:{secs:02d}")
        # Show the increase/decrease buttons
        self.decreaseButton.show()
        self.increaseButton.show()

    def startWork(self):
        # Set up the UI for work mode
        self.modeLabel.setText("Work")
        self.modeLabel.setStyleSheet("color: red")
        # Use the selected time as the starting time
        self.timeRemainingSec = self.countdownSec
        mins, secs = divmod(self.timeRemainingSec, 60)
        remainingText = f"{mins:02d}:{secs:02d}"
        self.timeLCD.display(remainingText)
        self.workSessions += 1
        self.workTimer.start()

    def updateWork(self):
        # Update the work timer display and switch to break mode when it reaches 0
        self.updateTimeDisplay()
        if self.timeRemainingSec == 0:
            self.checkmarks += "✅"
            self.countLabel.setText(self.checkmarks)
            self.workTimer.stop()
            self.startBreak()

    def startBreak(self):
        # Determine the type of break (long or short) based on work session count
        break_type = self.workSessions % LONG_BREAK_INTERVAL
        break_info = {
            0: ("Long Break", LONG_BREAK_MIN, "#80c342"),
            1: ("Short Break", SHORT_BREAK_MIN, "#53baff")
        }
        label, duration, color = break_info.get(break_type, ("Unknown", 0, "#000000"))
        # Set up the UI for break mode
        self.modeLabel.setText(label)
        self.modeLabel.setStyleSheet(f"color: {color}")
        self.timeLCD.display(f"{duration:02d}:00")
        self.timeRemainingSec = duration * 60
        self.countdownSec = duration * 60
        self.breakTimer.start()

    def updateBreak(self):
        # Update the break timer display and switch back to work mode when it reaches 0
        self.updateTimeDisplay()
        if self.timeRemainingSec == 0:
            self.breakTimer.stop()
            self.startWork()

    def updateTimeDisplay(self):
        # Update the time display and decrement the remaining time
        if not self.countdownStopped:
            self.timeRemainingSec -= 1
        mins, secs = divmod(self.timeRemainingSec, 60)
        mins = f"{mins:02d}"
        secs = f"{secs:02d}"
        remainingText = mins + ":" + secs
        self.timeLCD.display(remainingText)

    def decreaseTime(self):
        # Decrease the timer duration by 1 minute (minimum 1 min)
        if self.countdownStopped:
            self.timeSet -= 60
            if self.timeSet < 60:
                self.timeSet = 60
            mins, secs = divmod(self.timeSet, 60)
            self.countdownSec = self.timeSet
            self.timeLCD.display(f"{mins:02d}:{secs:02d}")

    def increaseTime(self):
        # Increase the timer duration by 1 minute (max 120 min)
        if self.countdownStopped:
            self.timeSet += 60
            if self.timeSet > 120 * 60:
                self.timeSet = 120 * 60
            mins, secs = divmod(self.timeSet, 60)
            self.countdownSec = self.timeSet
            self.timeLCD.display(f"{mins:02d}:{secs:02d}")

    def _setDefaults(self):
        # Reset all variables and UI elements to their default values
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
        # Set countdownStopped to True on reset
        # Reset countdownSec to initial work duration
        self.countdownStopped = True
        self.countdownSec = WORK_MIN * 60

def run():
    # Set the application's user model ID and create the main application instance
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setWindowIcon(QIcon("tomato.png"))
    app.setStyleSheet(Path('styles.qss').read_text())
    # Create and show the main window
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run()
