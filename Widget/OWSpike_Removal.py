from Orange.widgets.widget import OWWidget, Msg, Input, Output

from Orange.widgets import gui, settings
import Orange.data
from AnyQt.QtWidgets import QWidget, QFormLayout
from AnyQt.QtCore import Qt
import numpy as np
import numpy.ma as ma
from orangecontrib.spectroscopy.widgets.gui import lineEditIntOrNone

class SpikeRemovalEditor(BaseEditorOrange):
    name = "Spike Removal"
    description = "Finds Spikes in Ramen spectra based on Z-Score and allows for removal by averaging nearby data"
    priority = 100
    class Inputs:
        data = Input("Data", Orange.data.Table, default=True)
    class Outputs:
        Processed = Output("Data", Orange.data.Table, default=True)
    want_main_area = False
    settingsHandler = settings.DomainContextHandler()
    threshold = settings.Setting(7)
    Hi = settings.Setting(100)
    dis = settings.Setting(5)
    commitOnChange = settings.Setting(True)
    class Warning(OWWidget.Warning):
        nodata = Msg("No useful data on input!")
    def __init__(self):
        super().__init__()
        super().__init__()
        self.data = None
        self.set_data(self.data)

        self.optionsBox = gui.widgetBox(self.controlArea, "Options")
        gui.spin(
            self.optionsBox,
            self,
            "threshold",
            minv=1,
            maxv=20,
            step=1,
            label="Threshold value for Z-Score, Used to determine what is a spike:",
            callback=[self.threshold_Changed, self.checkCommit],
        )
        gui.spin(
            self.optionsBox,
            self,
            "Hi",
            minv=1,
            maxv=1000,
            step=1,
            label="Minium for peak difference to classify a spectra as having spikes:",
            callback=[self.Hi_Changed, self.checkCommit],
        )
        gui.spin(
            self.optionsBox,
            self,
            "dis",
            minv=1,
            maxv=20,
            step=1,
            label="Number of nearby normal peaks to average:",
            callback=[self.dis_Changed, self.checkCommit],
        )
        gui.checkBox(
            self.optionsBox, self, "commitOnChange", "Commit data on selection change"
        )
        gui.button(self.optionsBox, self, "Commit", callback=self.commit)
        self.optionsBox.setDisabled(False)

    @Inputs.data
    def set_data(self, dataset):
        self.Warning.nodata.clear()
        self.closeContext()
        self.data = dataset
        if dataset is None:
            self.Warning.nodata()
        else:
            self.openContext(dataset.domain)
    def threshold_Changed(self):
        self.commit()
    def Hi_Changed(self):
        self.commit()
    def dis_Changed(self):
        self.commit()
    def commit(self):
        def modified_z_score(intensity):
            median1 = np.median(intensity)
            mad_int = np.median([np.abs(intensity - median1)])
            modified_z_scores = 0.6745 * (intensity - median1) / mad_int
            return modified_z_scores
        #Z_Scores is the method used on a spectra to find spikes
        def fixer(y, m):
            threshold = self.threshold
            difference = (abs(np.array(modified_z_score(y))) > threshold)
            #peaks greater than the threshold are classified as spikes
            y_out = y.copy()
            spikes = difference.reshape(len(difference))  # shape needed
            for i in np.arange(len(spikes)):
                if spikes[i] != 0:
                    w = np.arange(i - m, i + m)
                    w2 = w[spikes[w] == 0]
                    y_out[i] = np.mean(y[w2])
            return y_out
            #Spikes are replaced by an averaged of the nearby points around them
        def finder(U):
            out = []
            Set = np.array(U)
            for row in Set:
                Distance = np.diff(row, n=0)
                if np.any(Distance > self.Hi):
                    out.append(fixer(row,m=self.dis))
                 #Looks for spectra which contain a specific height differenc between two points as seen in cosimic ray spikes.
                else:
                    out.append(row)
            return out
            #
        domain = self.data.domain
        Processed_data = Orange.data.Table(domain, finder(self.data))
        self.Outputs.Processed.send(Processed_data)

    def checkCommit(self):
            if self.commitOnChange:
                self.commit()




