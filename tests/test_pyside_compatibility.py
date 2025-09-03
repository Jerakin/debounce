from PySide6 import QtCore, QtWidgets

import pytest

from debounce import debounce

class TestApp(QtWidgets.QWidget):
    TestSignal = QtCore.Signal()

    def __init__(self):
        super(TestApp, self).__init__()
        self.button = QtWidgets.QPushButton("Test")
        self.events = 0
        self.setLayout(QtWidgets.QVBoxLayout())
        self.button.clicked.connect(self.btn_clicked)

    @debounce(0.1)
    def btn_clicked(self):
        self.TestSignal.emit()
        self.events += 1

    @debounce(0.5, leading=True)
    def mousePressEvent(self, event, /):
        self.events += 1


@pytest.fixture
def app(qtbot):
    test_hello_app = TestApp()
    qtbot.addWidget(test_hello_app)
    return test_hello_app


def test_debounce_event(qtbot, app):
    for i in range(100):
        qtbot.mousePress(app, QtCore.Qt.LeftButton)
    assert app.events == 1


def test_debounced_signal(qtbot, app):
    with qtbot.waitSignal(app.TestSignal, timeout=10000) as blocker:
        for i in range(100):
            app.button.click()
    assert app.events == 1
