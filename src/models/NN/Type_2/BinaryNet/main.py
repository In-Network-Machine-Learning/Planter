import torch
from classifiers.xnor_classifier import *
from classifiers.dorefa_classifier import *
from classifiers.bnn_classifier import *
from config import FLAGS
import importlib
from models import *

cuda = torch.cuda.is_available() and not(FLAGS.no_cuda)
device = torch.device('cuda' if cuda else 'cpu')
torch.manual_seed(0)
if cuda:
    torch.backends.cudnn.deterministic=True
    torch.cuda.manual_seed(0)

dataset = importlib.import_module("dataloader.{}".format(FLAGS.dataset))
train_loader = dataset.load_train_data(FLAGS.batch_size)
test_loader = dataset.load_test_data(FLAGS.test_batch_size)

model = eval(FLAGS.model)()
model.to(device)


if FLAGS.bin_type == 'xnor':
    classification = XnorClassifier(model, train_loader, test_loader, device)

elif FLAGS.bin_type == 'bnn':
    classification = BnnClassifier(model, train_loader, test_loader, device)

elif FLAGS.bin_type == 'dorefa':
    classification = DorefaClassifier(model, train_loader, test_loader, device)

criterion = torch.nn.CrossEntropyLoss()
criterion.to(device)

if hasattr(model, 'init_w'):
    model.init_w()


if FLAGS.optimizer == 'adam':
    optimizer = torch.optim.Adam(model.parameters(), lr=FLAGS.lr, weight_decay=1e-5)
elif FLAGS.optimizer == 'sgd':
    optimizer = torch.optim.SGD(model.parameters(), lr=FLAGS.lr, momentum=0.9,
        weight_decay=5.e-4)

scheduler = torch.optim.lr_scheduler.MultiStepLR(optimizer, FLAGS.steps,
        gamma=FLAGS.gamma)

classification.train(criterion, optimizer, FLAGS.epochs, scheduler, FLAGS.checkpoint)
