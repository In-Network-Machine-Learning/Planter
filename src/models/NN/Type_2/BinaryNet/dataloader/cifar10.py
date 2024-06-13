import os
import torch
from torchvision.datasets import CIFAR10
import torchvision.transforms as tvt


def load_train_data(batch_size=64, sampler=None):
    transform = tvt.Compose([
        tvt.RandomCrop(32, padding=4),
        tvt.RandomHorizontalFlip(),
        tvt.ToTensor(),
        tvt.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
        ])

    if sampler is None:
        shuffle = True
    else:
        shuffle = False

    dataset = CIFAR10(os.path.join('datasets', 'cifar10'), train=True,
            download=True, transform=transform)
    loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size,
            shuffle=shuffle, sampler=sampler, num_workers=4, pin_memory=True)

    return loader


def load_test_data(batch_size=1000, sampler=None):
    transform =  tvt.Compose([
        tvt.ToTensor(),
        tvt.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
        ])

    dataset = CIFAR10(os.path.join('datasets', 'cifar10'), train=False,
            download=True, transform=transform)
    loader = torch.utils.data.DataLoader( dataset, batch_size=batch_size,
            shuffle=False, sampler=sampler, num_workers=4, pin_memory=True)

    return loader
