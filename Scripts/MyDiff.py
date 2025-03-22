# File: MyDiff.py
# Path: SysUtils/MyDiff.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-20
# Last Modified: 2025-03-20  10:30AM
# Description: File diff generation tool with GUI interface

import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QFileDialog, QLabel
from PySide6.QtGui import QColor, QFont, QFontDatabase
from PySide6.QtCore import Qt

import difflib

class DiffWindow(QWidget):
    """
    GUI window for comparing and displaying differences between two files.
    
    This class provides a graphical interface for selecting two files,
    generating a diff between them, and visualizing the differences.
    """
    
    def __init__(self):
        """Initialize the diff window with UI components."""
        super().__init__()
        self.setWindowTitle("File Diff Generator")

        self.File1Path = ""
        self.File2Path = ""

        # Widgets
        self.File1Button = QPushButton("Select Original File")
        self.File1Label = QLabel("Original File: Not selected")
        self.File2Button = QPushButton("Select New File")
        self.File2Label = QLabel("New File: Not selected")
        self.GenerateButton = QPushButton("Generate Diff")
        self.GenerateButton.setEnabled(False)  # Disable initially

        self.OriginalText = QTextEdit()
        self.OriginalText.setReadOnly(True)
        self.NewText = QTextEdit()
        self.NewText.setReadOnly(True)
        self.DiffText = QTextEdit()
        self.DiffText.setReadOnly(True)

        self.OriginalHideButton = QPushButton("Hide Original")
        self.NewHideButton = QPushButton("Hide New")
        self.DiffHideButton = QPushButton("Hide Diff")

        self.OriginalVisible = True
        self.NewVisible = True
        self.DiffVisible = True

        # Layout
        FileLayout = QHBoxLayout()
        FileLayout.addWidget(self.File1Button)
        FileLayout.addWidget(self.File1Label)
        FileLayout.addWidget(self.File2Button)
        FileLayout.addWidget(self.File2Label)

        HideLayout = QHBoxLayout()
        HideLayout.addWidget(self.OriginalHideButton)
        HideLayout.addWidget(self.NewHideButton)
        HideLayout.addWidget(self.DiffHideButton)

        self.TextLabelLayout = QHBoxLayout()
        self.TextLabelLayout.addWidget(QLabel("Original File"))
        self.TextLabelLayout.addWidget(QLabel("New File"))
        self.TextLabelLayout.addWidget(QLabel("Diff"))

        self.DisplayLayout = QHBoxLayout()
        self.DisplayLayout.addWidget(self.OriginalText)
        self.DisplayLayout.addWidget(self.NewText)
        self.DisplayLayout.addWidget(self.DiffText)

        MainLayout = QVBoxLayout()
        MainLayout.addLayout(FileLayout)
        MainLayout.addWidget(self.GenerateButton)
        MainLayout.addLayout(HideLayout)
        MainLayout.addLayout(self.TextLabelLayout)
        MainLayout.addLayout(self.DisplayLayout)

        self.setLayout(MainLayout)

        # Connections
        self.File1Button.clicked.connect(self.SelectFile1)
        self.File2Button.clicked.connect(self.SelectFile2)
        self.GenerateButton.clicked.connect(self.GenerateDiff)

        self.OriginalHideButton.clicked.connect(self.ToggleOriginal)
        self.NewHideButton.clicked.connect(self.ToggleNew)
        self.DiffHideButton.clicked.connect(self.ToggleDiff)

    def SelectFile1(self):
        """Open a file dialog to select the first (original) file."""
        File1Path, _ = QFileDialog.getOpenFileName(self, "Select Original File")
        if File1Path:
            self.File1Path = File1Path
            self.File1Label.setText("Original File: " + self.File1Path)
            self.CheckEnableGenerate()

    def SelectFile2(self):
        """Open a file dialog to select the second (new) file."""
        File2Path, _ = QFileDialog.getOpenFileName(self, "Select New File")
        if File2Path:
            self.File2Path = File2Path
            self.File2Label.setText("New File: " + self.File2Path)
            self.CheckEnableGenerate()

    def CheckEnableGenerate(self):
        """Enable the Generate button if both files have been selected."""
        if self.File1Path and self.File2Path:
            self.GenerateButton.setEnabled(True)
        else:
            self.GenerateButton.setEnabled(False)

    def GenerateDiff(self):
        """Generate and display the diff between the two selected files."""
        try:
            with open(self.File1Path, 'r') as F1:
                File1Lines = F1.readlines()
            with open(self.File2Path, 'r') as F2:
                File2Lines = F2.readlines()

            # Display original and new files with specified colors
            self.OriginalText.setHtml(f"<pre><span style='color: green;'>{''.join(File1Lines)}</span></pre>")
            self.NewText.setHtml(f"<pre><span style='color: red;'>{''.join(File2Lines)}</span></pre>")

            Diff = difflib.Differ().compare(File1Lines, File2Lines)
            DiffText = ""
            for Line in Diff:
                if Line.startswith('  '):
                    DiffText += f"<span style='color: white;'>  {Line[2:]}</span>"  # Common lines
                elif Line.startswith('- '):
                    DiffText += f"<span style='color: red;'>1: {Line[2:]}</span>"  # File 1 lines
                elif Line.startswith('+ '):
                    DiffText += f"<span style='color: green;'>2: {Line[2:]}</span>"  # File 2 lines
                elif Line.startswith('? '):
                    DiffText += f"<span style='color: yellow;'>? {Line[2:]}</span>"  # Questionable lines
                else:
                    DiffText += f"<span style='color: darkgray;'>{Line}</span>"  # Other lines (e.g. ---, +++)

            if not DiffText:
                self.DiffText.setText("No differences found.")
            else:
                self.DiffText.setHtml(f"<pre>{DiffText}</pre>")

        except FileNotFoundError:
            self.OriginalText.setText("Error: One or both files not found.")
            self.NewText.setText("Error: One or both files not found.")
            self.DiffText.setText("Error: One or both files not found.")
        except Exception as e:
            self.DiffText.setText(f"Error: {str(e)}")

    def ToggleOriginal(self):
        """Toggle visibility of the original file pane."""
        self.OriginalVisible = not self.OriginalVisible
        self.OriginalText.setVisible(self.OriginalVisible)
        self.UpdateLayout()

    def ToggleNew(self):
        """Toggle visibility of the new file pane."""
        self.NewVisible = not self.NewVisible
        self.NewText.setVisible(self.NewVisible)
        self.UpdateLayout()

    def ToggleDiff(self):
        """Toggle visibility of the diff pane."""
        self.DiffVisible = not self.DiffVisible
        self.DiffText.setVisible(self.DiffVisible)
        self.UpdateLayout()

    def UpdateLayout(self):
        """Update the layout to reflect current visibility settings."""
        # Remove all widgets from the layout
        for i in reversed(range(self.DisplayLayout.count())):
            Widget = self.DisplayLayout.itemAt(i).widget()
            if Widget is not None:
                Widget.setParent(None)

        # Add the visible widgets back to the layout
        if self.OriginalVisible:
            self.DisplayLayout.addWidget(self.OriginalText)
        if self.NewVisible:
            self.DisplayLayout.addWidget(self.NewText)
        if self.DiffVisible:
            self.DisplayLayout.addWidget(self.DiffText)

def Main():
    """Main entry point for the application."""
    App = QApplication(sys.argv)
    Window = DiffWindow()
    Window.show()
    sys.exit(App.exec())

if __name__ == '__main__':
    Main()
