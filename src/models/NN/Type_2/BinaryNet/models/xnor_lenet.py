import torch.nn as nn
from .xnor_layers import * 

__all__ = ['lenet5']

class LeNet5(nn.Module):
    def __init__(self, out_classes = 10):
        super(LeNet5, self).__init__()
        self.features = nn.Sequential(
                nn.Conv2d(1, 20, kernel_size=5, stride=1),
                nn.BatchNorm2d(20, eps=1e-4, momentum=0.1, affine=False),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(kernel_size=2, stride=2),
                XNORConv2d(20, 50, kernel_size=5, stride=1, padding=0),
                nn.MaxPool2d(kernel_size=2, stride=2),
                nn.Flatten(),
        )
        self.classifier = nn.Sequential(
                BNLinearReLU(800, 500),
                nn.BatchNorm1d(500, eps=1e-4, momentum=0.1, affine=False),
                nn.Linear(500, out_classes),
        )

    def init_w(self):
        for m in self.modules():
            if isinstance(m, nn.BatchNorm2d) or isinstance(m, nn.BatchNorm1d):
                if hasattr(m.weight, 'data'):
                    m.weight.data.zero_().add_(1.0)
        return

    def norm_bn(self):
        for m in self.modules():
            if isinstance(m, nn.BatchNorm2d) or isinstance(m, nn.BatchNorm1d):
                if hasattr(m.weight, 'data'):
                    m.weight.data.clamp_(min = 0.01)
        return

    def forward(self, x):
        self.norm_bn()
        x = self.features(x)
        x = self.classifier(x)
        return x

def lenet5(out_classes=10):
    return LeNet5(out_classes)
