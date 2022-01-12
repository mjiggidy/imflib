from PySide6 import QtCore, QtWidgets, QtGui
from imflib import imf, cpl
from posttools import timecode
import sys, pathlib

from imflib.cpl import AudioResource, ImageResource

class DiffList(QtWidgets.QTreeWidget):
	"""List control showing the timecode list"""

	def __init__(self):
		super().__init__()
		self.headers = ["Record In", "Record Out", "Source In", "Source Out", "Duration", "Rate", "Essence Name", "Essence ID", "Essence Type"]
		self.setHeaderLabels(self.headers)
		self.setSortingEnabled(True)
		self.setIndentation(False)
		self.setAlternatingRowColors(True)
	
	@QtCore.Slot()
	def slot_imfChanged(self, imf:imf.Imf):
		self.clear()
		resources = list()
		
		# Here we go now
		for segment in imf.cpl.segments:
			for sequence in segment.sequences:
				tc_start = imf.cpl.tc_start
				for resource in sequence.resources:
					if isinstance(resource, cpl.Resource):
						tc_out = tc_start + resource.duration
						asset = imf.pkl.getAsset(resource.file_id)
						file_name = asset.file_name if asset else "External"
						essence_type = "Video" if isinstance(resource, cpl.ImageResource) else "Audio"
						self.addTopLevelItem(QtWidgets.QTreeWidgetItem([
							str(tc_start),
							str(tc_out),
							str(resource.in_point),
							str(resource.out_point),
							str(resource.duration),
							str(resource.edit_rate_formatted),
							file_name,
							resource.file_id,
							essence_type
						]))
						tc_start = tc_out
		
		for x in range(self.columnCount()):
			self.resizeColumnToContents(x)
		
		#self.sortByColumn(self.headers.index("Essence Type"), QtCore.Qt.SortOrder.DescendingOrder)
		self.sortByColumn(self.headers.index("Record In"), QtCore.Qt.SortOrder.AscendingOrder)



class MainArea(QtWidgets.QWidget):
	"""The main area of the application"""

	def __init__(self, difflist):
		super().__init__()
		self.setLayout(QtWidgets.QVBoxLayout())
		
		self.lbl_imfname = QtWidgets.QLabel()
		self.lst_difflist = difflist

		self.setupWidgets()

	def setupWidgets(self):
		self.layout().addWidget(self.lbl_imfname)
		self.layout().addWidget(self.lst_difflist)
	
	@QtCore.Slot()
	def slot_imfChanged(self, imf:imf.Imf):
		self.lbl_imfname.setText(imf.cpl.title)

class MainWindow(QtWidgets.QMainWindow):

	def __init__(self):
		super().__init__()
		self.tb_main  = QtWidgets.QToolBar()
		self.setupWindow()
	
	def setupWindow(self):
		self.tb_main.setMovable(False)
		self.addToolBar(self.tb_main)
		self.setUnifiedTitleAndToolBarOnMac(True)
	
	@QtCore.Slot()
	def slot_imfChanged(self, imf:imf.Imf):
		pass

		

class DiffFinder(QtWidgets.QApplication):
	"""An application to display local media in an IMF"""

	sig_imf_chosen = QtCore.Signal(imf.Imf)

	def __init__(self):
		super().__init__()

		self.active_imf = None
		
		self.wnd_main = MainWindow()
		self.mnu_main = QtWidgets.QMenuBar()

		self.lst_diff = DiffList()

		self.act_open = QtGui.QAction()
		self.act_exp_edl = QtGui.QAction()
		self.act_exp_txt = QtGui.QAction()

		self.setupMenuBar()
		self.setupActions()
		self.setupMainWindow()
		self.firstRun()
		self.wnd_main.show()

	def setupMenuBar(self):
		self.mnu_file = self.mnu_main.addMenu("File")

	def setupActions(self):
		self.act_open.setText("&Open...")
		self.act_open.setToolTip("Open an IMF package")
		#self.act_open.setIcon(QtGui.QIcon("../res/icn_open.png"))
		self.act_open.triggered.connect(lambda: self.openImf())
		
		self.act_exp_edl.setText("Export &EDL...")
		self.act_exp_edl.setToolTip("Export the visible items as an EDL")
		self.act_exp_edl.triggered.connect(lambda: self.outputAsEdl())
		#self.act_exp_edl.setIcon(QtGui.QIcon("../res/icn_exp_edl.png"))
		
		self.act_exp_txt.setText("Export &Text File...")
		#self.act_exp_txt.setIcon(QtGui.QIcon("../res/icn_exp_txt.png"))
		self.act_exp_txt.setToolTip("Export the visible items as a change list")

		self.mnu_file.addAction(self.act_open)
		self.mnu_file.addSeparator()
		self.mnu_file.addAction(self.act_exp_edl)
		self.mnu_file.addAction(self.act_exp_txt)

	def setupMainWindow(self):
		self.wnd_main.setWindowTitle("IMF Differ Extreme!")
		self.wnd_main.setCentralWidget(MainArea(self.lst_diff))
		self.wnd_main.setMenuBar(self.mnu_main)
		self.wnd_main.resize(1024, 800)


		spacer = QtWidgets.QWidget()
		spacer.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

		logo = QtWidgets.QLabel("<img src='../res/logo_soft.png' height='25' />")
		
		logo.setScaledContents(True)
		

		
		self.wnd_main.tb_main.addAction(self.act_open)
		self.wnd_main.tb_main.addSeparator()
		self.wnd_main.tb_main.addAction(self.act_exp_edl)
		self.wnd_main.tb_main.addAction(self.act_exp_txt)
		self.wnd_main.tb_main.addWidget(spacer)
		#self.wnd_main.tb_main.addWidget(logo)

		self.sig_imf_chosen.connect(self.wnd_main.slot_imfChanged)
		self.sig_imf_chosen.connect(self.wnd_main.centralWidget().slot_imfChanged)
		self.sig_imf_chosen.connect(self.lst_diff.slot_imfChanged)
	
	def openImf(self):
		selected = QtWidgets.QFileDialog.getExistingDirectory(self.wnd_main, "Choose an IMF folder...", "../examples/")
		if not selected:
			return

		try:
			self.active_imf = imf.Imf.fromPath(selected)
		except Exception as e:
			QtWidgets.QMessageBox.critical(self.wnd_main, "Cannot Open IMF", f"The following error occurred when attempting to open this IMF:\n\n{e}")
			return
		
		self.sig_imf_chosen.emit(self.active_imf)
	
	def outputAsEdl(self):
		selected, _ = QtWidgets.QFileDialog.getSaveFileName(self.wnd_main, "Save EDL as...", "../examples/", filter="EDL (*.edl);;All Files (*)")
		if not selected:
			return
		
		path_output = pathlib.Path(selected)
		
		with path_output.open("w") as edl_output:
			print(f"TITLE: {self.active_imf.cpl.title}", file=edl_output)
			print(f"FCM: {'DROP FRAME' if self.active_imf.cpl.tc_start.mode == timecode.Timecode.Mode.DF else 'NON-DROP FRAME'}\n", file=edl_output)

			idx_event = 1

			for segment in self.active_imf.cpl.segments:
				for sequence in segment.sequences:
					tc_start = self.active_imf.cpl.tc_start
					for clip in sequence.resources:
						print("  ".join([
							str(idx_event).zfill(4),
							pathlib.Path(self.active_imf.pkl.getAsset(clip.file_id).file_name if self.active_imf.pkl.getAsset(clip.file_id) else "External").stem.ljust(128),
							"V" if isinstance(clip, cpl.ImageResource) else "A",
							"C",
							f"{clip.in_point} {clip.out_point} {tc_start} {tc_start + clip.duration}"
						]), file=edl_output)
						
						tc_start += clip.duration
						idx_event += 1

			QtWidgets.QMessageBox.information(self.wnd_main,"EDL Complete",f"The EDL has been output to:\n\n{path_output}")

	
	def firstRun(self):
		self.openImf()
		


app = DiffFinder()
app.exec()