import torch.nn as nn
from .xnor_layers import * 

__all__ = ['mlp']

class MLP(nn.Module):
    def __init__(self, input_size, num_hidden_nodes, num_layers, out_classes ):
        super(MLP, self).__init__()
        self.num_layers = num_layers
        self.classifier = nn.Sequential()
        for l in range(num_layers):
            if l==0:
                self.classifier.add_module('layer'+str(l)+'_flatten', nn.Flatten())
                self.classifier.add_module('layer'+str(l), nn.Linear(input_size, num_hidden_nodes[l]))
                self.classifier.add_module('layer'+str(l)+'_normal', nn.BatchNorm1d(num_hidden_nodes[l], eps=1e-4, momentum=0.1, affine=False))
                self.classifier.add_module('layer'+str(l)+'_activate', nn.ReLU(inplace=True))
            elif l+1 == num_layers:
                self.classifier.add_module('layer'+str(l), nn.Linear(num_hidden_nodes[l-1], out_classes))
            else:
                self.classifier.add_module('layer'+str(l), nn.Linear(num_hidden_nodes[l-1], num_hidden_nodes[l]))
                self.classifier.add_module('layer' + str(l) + '_normal', nn.BatchNorm1d(num_hidden_nodes[l], eps=1e-4, momentum=0.1, affine=False))
                self.classifier.add_module('layer' + str(l) + '_activate', nn.ReLU(inplace=True))

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
        x = self.classifier(x)
        return x

def mlp(input_size, num_hidden_nodes, num_layers, out_classes):
    return MLP(input_size, num_hidden_nodes, num_layers, out_classes)
