from PySide6.QtWidgets import QApplication, QColorDialog

app = QApplication()

color = QColorDialog()
color.setOption(QColorDialog.DontUseNativeDialog, True)
color.setOption(QColorDialog.NoButtons, True)
color.ColorDialogOption.NoButtons
color.ColorDialogOption.DontUseNativeDialog
color.show()

app.exec()