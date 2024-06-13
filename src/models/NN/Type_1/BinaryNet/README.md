# Binary Neural Networks on PyTorch 

![Binarization](https://github.com/lucamocerino/Binary-Neural-Networks-PyTorch-1.0/blob/master/bin.png)


This repository implements three popular papers that introduced the concept of Binary Neural Networks: 
- **XNOR-Net: ImageNet Classification Using Binary Convolutional Neural Networks**: https://arxiv.org/abs/1603.05279.
- **Binarized Neural Networks** :https://papers.nips.cc/paper/6573-binarized-neural-networks
- **DoReFa-Net: Training Low Bitwidth Convolutional Neural Networks with Low Bitwidth Gradients** :https://arxiv.org/abs/1606.06160



The project is organized as follows:

  - **models** folder contains CNN models (simple mlp, Network-in-Network, LeNet5, etc.)
  - **classifiers/{type}_classifier.py** contains the test and train procedures; where type = {bnn, xnor, dorefa}
  - **models/{type}_layers.py** contains the binarylayers implementation (binary activation, binary conv and fully-connected layers, gradient update);  where type = {bnn, xnor, dorefa}
  - **yml** folder contains configuration files with hyperparameters
  - **main.py** represents the entry file

### Installation

All packages are in *requirement.txt*
Install the dependencies:

```sh
pip install -r requirements.txt
```
### Basic usage
```sh
$ python main.py app:{yml_file}
```
### Example 
Network-in-Network on CIFAR10 dataset. All hyper parameters are in .yml file. 
```sh
$ python main.py app:yml/nin_cifar10.yml
```
## Related Applications
If you find this code useful in your research, please consider citing one of the works in this section.

  - Fast and Accurate Inference on Microcontrollers With Boosted Cooperative Convolutional Neural Networks (BC-Net) https://ieeexplore.ieee.org/abstract/document/9275360
  - CoopNet: Cooperative Convolutional Neural Network for Low-Power MCUs https://ieeexplore.ieee.org/abstract/document/8964993
  - TentacleNet: A Pseudo-Ensemble Template for Accurate Binary Convolutional Neural Networks https://ieeexplore.ieee.org/abstract/document/9073982/

License
----

MIT




