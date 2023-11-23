# Hawk, A highly efficient non-intrusive load monitoring system you always wanted

## Introduction
For the review process, we provide access to the complete Hawk model, select portions of the code, and a subset of the dataset, along with various result logs that we have compiled in the past.

The "Codes" folder contains code and execution scripts, including a separate folder for performance validation code.

In the "Datasets" folder, there are two dataset files; upon publication of our paper, we will make public the download methods for all datasets.

The "GroundTruth" folder holds annotation data for 18 datasets, indicating intervals when appliances were turned on, serving as a reference for output results.

The "Models" folder contains pre-trained models.

"PreResult" houses the inference results obtained from applying these codes and models on the complete dataset.

"Result" is designated for storing current prediction outcomes.

Reviewers might critique our code style, but the integrity of our data results is indisputable. We believe that our code is robust and has significant potential for improvement.

We welcome any questions or feedback.


### Prerequisites
To run the Python scripts, you need to pre-install `xgboost` and `numpy`.

For executing the performance test code, you will need to compile and install the XGBoost C API by following the official documentation available at: [XGBoost C API Tutorial](https://github.com/dmlc/xgboost/blob/master/doc/tutorials/c_api_tutorial.rst#install-xgboost-on-conda-environment). Additionally, installation of FFTW (Fastest Fourier Transform in the West) is required, which can be found on its official website: [FFTW](https://www.fftw.org/).

## Usage
For rapid utilization and verification, please execute or refer to the run-pred.sh script in the Codes directory.