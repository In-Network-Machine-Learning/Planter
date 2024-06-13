from torch.utils.data import DataLoader
from os.path import join
from torchvision.datasets import MNIST
from torchvision.transforms import Compose, Resize, Normalize, ToTensor


def load_train_data(batch_size=128, sampler=None):
    cuda = True
    loader_kwargs = {'num_workers': 0, 'pin_memory': True} if cuda else {}
    
    train_loader = DataLoader(
        MNIST(join('datasets', 'mnist'), train=True, download=True,
            transform=Compose([
                   Resize((28, 28)),
                   ToTensor(),
                   Normalize((0.1307,),(0.308,)),
                  ])),
        batch_size=batch_size, shuffle=True, **loader_kwargs)

    return train_loader

def load_test_data(batch_size=1000, sampler=None):
    
    cuda = True
    loader_kwargs = {'num_workers': 0, 'pin_memory': True} if cuda else {}
    
    test_loader = DataLoader(
        MNIST(join('datasets', 'mnist'), train=False, download=True,
            transform=Compose([
                   Resize((28, 28)),
                   ToTensor(),
                   Normalize((0.1307,),(0.308,)),
                    ])),
        batch_size= batch_size, shuffle=False,sampler=sampler, **loader_kwargs)

    return test_loader


