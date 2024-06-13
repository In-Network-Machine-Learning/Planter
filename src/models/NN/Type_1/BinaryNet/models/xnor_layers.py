from torch import zeros
from torch.autograd import Function
from torch.nn import Parameter, Module, Conv2d, Linear, BatchNorm1d, BatchNorm2d, Dropout, ReLU


__all__ = ['XNORConv2d', 'XNORLinear', 'BNConvReLU','BNLinearReLU']


class BinActive(Function):
    @staticmethod
    def forward(ctx, input):
        ctx.save_for_backward(input)
        input = input.sign()
        return input 

    @staticmethod
    def backward(ctx, grad_output):
        input, = ctx.saved_tensors
        grad_input = grad_output.clone()
        grad_input[input.ge(1)] = 0
        grad_input[input.le(-1)] = 0
        return grad_input


class XNORConv2d(Module):
    def __init__(self, in_channels, out_channels, kernel_size=1, stride=1, padding=0, groups=1, bias=True, dropout_ratio=0):
        super(XNORConv2d, self).__init__()
    
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = padding
        self.groups = groups
    
        self.conv = Conv2d(in_channels = in_channels, out_channels = out_channels, kernel_size = kernel_size, stride = stride, padding = padding, groups = groups)
        self.conv.weight.data.normal_(0, 0.05)
        self.conv.bias.data.zero_()

        self.fp_weights = Parameter(zeros(self.conv.weight.size()))
        self.fp_weights.data.copy_(self.conv.weight.data)
    
    def forward(self, x):
        
        self.fp_weights.data = self.fp_weights.data - self.fp_weights.data.mean(1, keepdim = True)
        self.fp_weights.data.clamp_(-1, 1)
        self.mean_val = self.fp_weights.abs().view(self.out_channels, -1).mean(1, keepdim=True)

        self.conv.weight.data.copy_(self.fp_weights.data.sign() * self.mean_val.view(-1, 1, 1, 1))
        x = self.conv(x)

        return x

    def update_gradient(self):
        proxy = self.fp_weights.abs().sign()
        proxy[self.fp_weights.data.abs()>1] = 0
        binary_grad = self.conv.weight.grad * self.mean_val.view(-1, 1, 1, 1) * proxy

        mean_grad = self.conv.weight.data.sign() * self.conv.weight.grad
        mean_grad = mean_grad.view(self.out_channels, -1).mean(1).view(-1, 1, 1, 1)
        mean_grad = mean_grad * self.conv.weight.data.sign()

        self.fp_weights.grad = binary_grad + mean_grad
        self.fp_weights.grad = self.fp_weights.grad * self.fp_weights.data[0].nelement() * (1-1/self.fp_weights.data.size(1))

class BNConvReLU(Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride=1, padding=0, groups=1, bias=True, dropout_ratio=0):
        super(BNConvReLU, self).__init__()
        self.dropout = dropout_ratio
        self.a_active = BinActive.apply
        
        self.bn = BatchNorm2d(in_channels, eps=1e-4, momentum=0.1, affine=True)
        if self.dropout !=0:
            self.drop = Dropout(self.dropout, inplace=True)
        self.econv = XNORConv2d(in_channels, out_channels, kernel_size=kernel_size, stride=stride, padding=padding, groups=groups, bias=bias)
        self.relu = ReLU(inplace=True)

    def forward(self, x):
        
        x = self.bn(x)
        x = self.a_active(x)
        if self.dropout !=0:
            x = self.drop(x)

        x = self.econv(x)
        x = self.relu(x)
        return x


class XNORLinear(Module):
    def __init__(self, in_features, out_features, bias=True):
        super(XNORLinear, self).__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.bias = bias

        self.linear = Linear(in_features = in_features, out_features = out_features, bias = bias)
        self.fp_weights = Parameter(zeros(self.linear.weight.size()))
        self.fp_weights.data.copy_(self.linear.weight.data)

    def forward(self, x):
        self.fp_weights.data = self.fp_weights.data - self.fp_weights.data.mean(1, keepdim = True)
        self.fp_weights.data.clamp_(-1, 1)

        self.mean_val = self.fp_weights.abs().view(self.out_features, -1).mean(1, keepdim=True)

        self.linear.weight.data.copy_(self.fp_weights.data.sign() * self.mean_val.view(-1, 1))
        x = self.linear(x)
        return x

    def update_gradient(self):
        proxy = self.fp_weights.abs().sign()
        proxy[self.fp_weights.data.abs()>1] = 0
        binary_grad = self.linear.weight.grad * self.mean_val.view(-1, 1) * proxy

        mean_grad = self.linear.weight.data.sign() * self.linear.weight.grad
        mean_grad = mean_grad.view(self.out_features, -1).mean(1).view(-1, 1)
        mean_grad = mean_grad * self.linear.weight.data.sign()

        self.fp_weights.grad = binary_grad + mean_grad
        self.fp_weights.grad = self.fp_weights.grad * self.fp_weights.data[0].nelement() * (1-1/self.fp_weights.data.size(1))
        return

class BNLinearReLU(Module):
    def __init__(self, in_channels, out_channels, bias=True, dropout_ratio=0):
        super(BNLinearReLU, self).__init__()
        self.dropout = dropout_ratio
        self.a_active = BinActive.apply
        
        self.bn = BatchNorm1d(in_channels, eps=1e-4, momentum=0.1, affine=True)
        if self.dropout !=0:
            self.drop = Dropout(self.dropout, inplace=True)
        self.fc = XNORLinear(in_channels, out_channels, bias=bias)
        self.relu = ReLU(inplace=True)

    def forward(self, x):
        
        x = self.bn(x)
        x = self.a_active(x)
        if self.dropout !=0:
            x = self.drop(x)

        x = self.fc(x)
        x = self.relu(x)
        return x
