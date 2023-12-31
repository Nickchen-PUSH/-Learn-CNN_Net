import time

import torch
from PIL import Image
from torch.autograd import Variable
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms

root = 'data/MNIST/raw/'

#----------Prepare the dataset-------------
def default_loader(path):
    return Image.open(path).convert('RGB')
class MyDataset(Dataset):
    def __init__(self,txt,transform=None,target_transform=None,loader=default_loader):
        fh = open(txt,'r')
        imgs = []
        for line in fh:
            line = line.strip('\n')
            line = line.rstrip()
            words = line.split()
            imgs.append((words[0],int(words[1])))
        self.imgs = imgs
        self.transform = transform
        self.target_transform = target_transform
        self.loader = loader

    def __getitem__(self,index):
        fn,lable = self.imgs[index]
        img = self.loader(fn)
        if self.transform is not None:
            img = self.transform(img)
        return img,lable

    def __len__(self):
        return len(self.imgs)

train_data = MyDataset(txt=root+'train.txt',transform=transforms.ToTensor())
test_data = MyDataset(txt=root+'test.txt',transform=transforms.ToTensor())
train_loader = DataLoader(dataset=train_data,batch_size=64,shuffle=True)
test_loader = DataLoader(dataset=test_data,batch_size=64,shuffle=True)



#----------Create the Net and train-------------

class Net(torch.nn.Module):
    def __init__(self):
        super(Net,self).__init__()
        self.conv1 = torch.nn.Sequential(
            torch.nn.Conv2d(3,32,3,1,1),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(2)
        )
        self.conv2 = torch.nn.Sequential(
            torch.nn.Conv2d(32,64,3,1,1),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(2)
        )
        self.conv3 = torch.nn.Sequential(
            torch.nn.Conv2d(64,64,3,1,1),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(2)
        )
        self.dense = torch.nn.Sequential(
            torch.nn.Linear(64*3*3,128),
            torch.nn.ReLU(),
            torch.nn.Linear(128,10)
        )

    def forward(self,x):
        conv1_out = self.conv1(x)
        conv2_out = self.conv2(conv1_out)
        conv3_out = self.conv3(conv2_out)
        res = conv3_out.view(conv3_out.size(0),-1)
        out = self.dense(res)
        return out

model = Net()
print(model)

optimizer = torch.optim.Adam(model.parameters())
loss_func = torch.nn.CrossEntropyLoss()

for epoch in range(10):
    print(f'epoch{epoch+1}')
    train_loss = 0
    train_acc = 0
    count = 0
    for batch_x,batch_y in train_loader:
        batch_x,batch_y = Variable(batch_x),Variable(batch_y)
        out = model(batch_x)
        loss = loss_func(out,batch_y)
        train_loss += loss.item()
        pred = torch.max(out,1)[1]
        train_correct = (pred == batch_y).sum()
        train_acc += train_correct.item()
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        count+=1
        #print(f"Training batch no.{count}")
    print('Train Loss:{:.6f},Acc:{:.6f}'.format(train_loss/(len(train_data)),train_acc/(len(train_data))))
    count=0
    #------------evaluation---------------
    model.eval()
    eval_loss = 0
    eval_acc = 0
    for batch_x,batch_y in test_loader:
        #batch_x,batch_y = Variable(batch_x,volatile=True),Variable(batch_y,volatile=True)
        out = model(batch_x)
        loss = loss_func(out,batch_y)
        eval_loss += loss.item()
        pred = torch.max(out,1)[1]
        num_correct = (pred == batch_y).sum()
        eval_acc += num_correct.item()
    print('Test Loss:{:.6f},Acc:{:.6f}'.format(eval_loss/(len(test_data)),eval_acc/(len(test_data))))
    print(model.parameters())

current_time = time.strftime("%Y%H%b_%H:%M:%S")
torch.save(model.state_dict(),f"./{current_time}.pt")
