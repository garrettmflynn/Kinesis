# [Kinesis](https://github.com/Mousai-Neurotechnologies/Kinesis)
Streamlined Movement Decoding on OpenBCI Headsets

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

[![Kinesis YouTube Video](media/KinesisCollage.png)](https://youtu.be/JmtpmnEbmtA) 
 
**Kinesis** is a movement decoding pipeline for OpenBCI headsets that integrates automatic motion tracking with real-time signals processing. Configured for (1) synthetic data streams and (2) the OpenBCI Cyton Daisy board.

*Special thanks to [OpenBCI](https://openbci.com/), [Brainflow](https://brainflow.readthedocs.io/en/stable/index.html), and [Sentdex](https://github.com/Sentdex/BCI) for the supporting code.*

## Usage
### Set Up a Conda Environment
Download [Miniconda](https://docs.conda.io/en/latest/miniconda.html) and run: 
```
conda env create -f mousai.yml
```

### Run Kinesis.py
To start the app, run: 
```
python Kinesis.py
```

### Termios Keylogging (Windows)
Termios is not compatible with Windows. Since this part of the code only toggles between a black background and live video, please comment this out and continue working with Kinesis.




