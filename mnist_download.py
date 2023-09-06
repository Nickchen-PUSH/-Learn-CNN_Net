from torchvision import datasets, transforms

train_dataset = datasets.MNIST('./data',train=True,transform=transforms.ToTensor(),download=True)
test_dataset = datasets.MNIST('./data',train=False,transform=transforms.ToTensor(),download=True)