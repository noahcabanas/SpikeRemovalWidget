Spike Removal

**Inputs**

- Data: input dataset

**Outputs**

- Averages: averaged dataset

The **Spike Removal** widget enables you to remove anaomylous spiked data form ramen spectra. It achieves this in a two part method. First, since spiked data is generally significantly larger than the normal spectra, it finds spectra in the dataset which are exhibit these vast difference. Second, using a z scores method it sets a limit for these spike spectra in order to find the areas within the spectra which are spikes and replacing them with an average of nearby data. 
