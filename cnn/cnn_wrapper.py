import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import transforms
from torch.utils.tensorboard import SummaryWriter
from custom_image_loader import CustomImageFolder
from cnn import CNN
from cnn_trainer import CnnTrainer

class CnnWrapper():
    def __init__(self, test_data_dir, model_path, batch_size = 128, learning_rate= 0.0002, has_training = False):
        # Example usage
        self.transform = transforms.Compose([
            transforms.Grayscale(),
            transforms.Resize((112, 112)),
            transforms.ToTensor(),
        ])

        self.test_data_dir = test_data_dir
        self.model_path = model_path
        self.dataset = CustomImageFolder(test_data_dir, transform=self.transform)

        total_size = len(self.dataset)
        if has_training:
            train_size = int(0.7 * total_size)
            val_size = int(0.15 * total_size)
            test_size = total_size - train_size - val_size
        else:
            train_size = 0
            val_size = 0
            test_size = total_size
        
        train_data, val_data, test_data = torch.utils.data.random_split(
            self.dataset, [train_size, val_size, test_size], 
            generator=torch.Generator().manual_seed(42)
        )

        self.train_loader = DataLoader(train_data, batch_size=batch_size, shuffle=True)
        self.val_loader = DataLoader(val_data, batch_size=batch_size)
        self.test_loader = DataLoader(test_data, batch_size=batch_size)

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.num_classes = len(self.dataset.classes)
        self.model = CNN(self.num_classes).to(self.device)
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate, weight_decay=2e-5)
        self.scheduler = torch.optim.lr_scheduler.StepLR(self.optimizer, step_size=30, gamma=0.1)
        self.writer = SummaryWriter(log_dir='./nn_boards')

        self.trainer = CnnTrainer(self.model, self.device, self.train_loader, self.val_loader, self.test_loader, 
                                  self.optimizer, self.criterion, self.scheduler, self.writer, self.model_path)

    def train(self, epochs = 50, stop_val = 2e-4, model_path = 'model.pth', load_model = False):
        return self.trainer.run(epochs, stop_val, model_path, load_model)

    def test(self):
        return self.trainer.test()

    def perform_prediction(self, model_path, test_data):
        return self.trainer.predict(model_path, test_data)