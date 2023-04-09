import os
import argparse
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from sagemaker_training import environment

env = environment.Environment()
# get the folder where the model should be saved
model_dir = env.model_dir

# Define the Stable Diffusion model
class StableDiffusionModel(nn.Module):
    def __init__(self, n_channels, n_blocks):
        super(StableDiffusionModel, self).__init__()
        self.n_channels = n_channels
        self.n_blocks = n_blocks
        self.blocks = nn.Sequential(*[nn.Conv2d(3, self.n_channels, 32, padding=1) for _ in range(self.n_blocks)])

    def forward(self, x):
        return x + self.blocks(x)

def train(model, device, train_loader, optimizer, criterion, epoch):
    model.train()
    for batch_idx, (data, _) in enumerate(train_loader):
        data = data.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, data)
        loss.backward()
        optimizer.step()

        if batch_idx % 10 == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                epoch, batch_idx * len(data), len(train_loader.dataset),
                100. * batch_idx / len(train_loader), loss.item()))

def main():
    parser = argparse.ArgumentParser()
    # full argument list refer to: https://github.com/aws/sagemaker-training-toolkit/blob/master/src/sagemaker_training/params.py
    parser.add_argument('--epochs', type=int, default=10, help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=64, help='Batch size for training')
    parser.add_argument('--lr', type=float, default=0.001, help='Learning rate')
    parser.add_argument('--n-channels', type=int, default=64, help='Number of channels in the model')
    parser.add_argument('--n-blocks', type=int, default=4, help='Number of convolutional blocks in the model')
    parser.add_argument('--training_dataset_s3_path', type=str, help='S3 path to the training dataset')
    args = parser.parse_args()

    # Set up device and data loaders
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    transform = transforms.Compose([transforms.Resize(32),
                                    transforms.RandomHorizontalFlip(),
                                    transforms.RandomCrop(32, padding=4),
                                    transforms.ToTensor(),
                                    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
    train_dataset = datasets.CIFAR10(root='./data', train=True, download=True, transform=transform)
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)

    # Initialize the model, optimizer, and loss function
    model = StableDiffusionModel(n_channels=args.n_channels, n_blocks=args.n_blocks).to(device)
    optimizer = optim.Adam(model.parameters(), lr=args.lr)
    criterion = nn.MSELoss()

    # Train the model using the training data
    for epoch in range(1, args.epochs + 1):
        train(model, device, train_loader, optimizer, criterion, epoch)

    # Save the trained model
    os.makedirs('/opt/ml/model', exist_ok=True)
    torch.save(model.state_dict(), os.path.join(model_dir, 'model.pth'))

if __name__ == '__main__':
    main()