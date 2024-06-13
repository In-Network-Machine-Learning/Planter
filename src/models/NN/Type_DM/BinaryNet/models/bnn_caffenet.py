import torch.nn as nn
from .bnn_layers import *


__all__ = ['bnn_caffenet']


    
class BNNCaffenet(nn.Module):

    def __init__(self, num_classes=10):
        super(BNNCaffenet, self).__init__()
 
        self.features = nn.Sequential(
                
                BNNConv2d(3, 32, kernel_size=5, stride=1, padding=2, bias=False),
                nn.BatchNorm2d(32),
                nn.Hardtanh(inplace=True),
                nn.MaxPool2d(kernel_size=3, stride=2, padding=0, ceil_mode=True),
                
                BNNConv2d(32, 32, kernel_size=5, stride=1, padding=2, bias=False),
                nn.BatchNorm2d(32),
                nn.Hardtanh(inplace=True),
                nn.MaxPool2d(kernel_size=3, stride=2, padding=0, ceil_mode=True),
                
                BNNConv2d(32, 32, kernel_size=5, stride=1, padding=2, bias=False),
                nn.BatchNorm2d(32),
                nn.Hardtanh(inplace=True),
                nn.MaxPool2d(kernel_size=3, stride=2, padding=0, ceil_mode=True),
                
                nn.Flatten(),
                nn.BatchNorm1d(512),
                nn.Hardtanh(inplace=True),
                BNNLinear(512, num_classes),
                nn.BatchNorm1d(num_classes, affine=False),
                nn.LogSoftmax(dim=1),
        )

    def forward(self, x):
        return self.features(x)


    def init_w(self):
        # weight initialization
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out')
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.ones_(m.weight)
                nn.init.zeros_(m.bias)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.zeros_(m.bias)
        return


def bnn_caffenet(num_classes=10):
    return BNNCaffenet(num_classes)

