from Orange.widgets.widget import OWWidget, Msg, Input, Output
from Orange.widgets import gui, settings
import Orange.data
from AnyQt.QtWidgets import QWidget, QFormLayout
from AnyQt.QtCore import Qt
import numpy as np
import numpy.ma as ma
from orangecontrib.spectroscopy.widgets.gui import lineEditIntOrNone

class SpikeRemovalEditor(BaseEditorOrange):
    class Inputs:
        data = Input("Data", Orange.data.Table, default=True)
    class Outputs:
        Processed = Output("Data", Orange.data.Table, default=True)
    settingsHandler = settings.DomainContextHandler()
    threshold = settings.Setting(7)
    Hi = settings.Setting(100)
    dis = settings.Setting(5)
    commitOnChange = settings.Setting(True)
    class Warning(OWWidget.Warning):
        nodata = Msg("No useful data on input!")
    def __init__(self, parent = None, **kwargs):
        super().__init__(parent, **kwargs)
        layout = QVBoxLayout()
        self.dis=5
        self.threshold = 7
        self.Hi = 100
        self.Optionform = QFormLayout()
        minf, maxf = -sys.float_info.max, sys.float_info.max
        self.heig = SetXDoubleSpinBox(
            minimum=minf, maximum=maxf, singleStep=1,
            value=self.Hi, enabled=True)
        self.dista = SetXDoubleSpinBox(
            minimum=minf, maximum=maxf, singleStep=1,
            value=self.dis, enabled=True)
        self.threshol = SetXDoubleSpinBox(
            minimum=minf, maximum=maxf, singleStep=1,
            value=self.threshold, enabled=True)
        self.areaform.addRow("Threshold", self.threshol)
        self.areaform.addRow("Value to select for spiked spectra", self.heig)
        self.areaform.addRow("Distance between averaged normal peaks", self.dista)
        self.preview_data = None

        self.user_changed = False

    @Inputs.data
    def __call__ (self, data):
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
        def finder(Spectral):
            out = []
            Series = np.array(Spectral)
            for row in Series:
                Distance = np.diff(row, n=0)
                if np.any(Distance > self.Hi):
                    out.append(fixer(row,m=self.dis))
                 #Looks for spectra which contain a specific height differenc between two points as seen in cosimic ray spikes.
                else:
                    out.append(row)
            return out
         
        domain = Orange.data.Domain(atts, data.domain.class_vars,
									data.domain.metas)
  
        return data.from_table(domain, finder(data))

    def set_preview_data(self, data):
            self.preview_data = data
