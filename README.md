# Hawk, A highly efficient non-intrusive load monitoring system you always wanted

## Quick Start
To quickly use and verify the system, please execute or refer to the `run-pred.sh` script located in the `Codes` directory.

## Installation Requirements
Before running the Python scripts, ensure that `xgboost` and `numpy` are installed on your system. For running the performance testing part of the code, you need to compile and install the XGBoost C API following the official documentation: [XGBoost C API Tutorial](https://github.com/dmlc/xgboost/blob/master/doc/tutorials/c_api_tutorial.rst#install-xgboost-on-conda-environment). Additionally, install `fftw` from its official website: [FFTW](https://www.fftw.org/).

## Project Structure
- `Codes`: Contains code and run scripts.
- `Datasets`: Two dataset files are located here. The full dataset will be made available for download upon publication of the paper.
- `GroundTruth`: Stores annotation data for 18 datasets corresponding to the intervals when appliances were turned on, for comparison with output results.
- `Models`: Pre-trained models are stored here.
- `PreResult`: Contains results inferred from the complete dataset using these codes and models.
- `Result`: For storing current prediction results.

## Note
Reviewers may complain the style of the code, but the results of the data are reliable.

We believe our code is robust and has significant room for improvement.

Any queries or suggestions are welcome. 