import torch.nn as nn
import torch.nn.functional as F

class CNN(nn.Module):
    """
    Convolutional Neural Network (CNN) for image classification.
    """
    def __init__(self, num_classes):

        super(CNN, self).__init__()
        
        self.convolution_layer_1 = nn.Conv2d(1, 64, kernel_size=3, padding=1)
        self.convolution_layer_2 = nn.Conv2d(64, 64, kernel_size=3, padding=1)
        self.convolution_layer_3 = nn.Conv2d(64, 64, kernel_size=5, padding=2)
        self.convolution_layer_4 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.convolution_layer_5 = nn.Conv2d(128, 128, kernel_size=3, padding=1)
        self.convolution_layer_6 = nn.Conv2d(128, 128, kernel_size=5, padding=2)
        self.convolution_layer_7 = nn.Conv2d(128, 256, kernel_size=3, padding=1)
        
        self.batch_normalization_layer_1 = nn.BatchNorm2d(64)
        self.batch_normalization_layer_2 = nn.BatchNorm2d(64)
        self.batch_normalization_layer_3 = nn.BatchNorm2d(64)
        self.batch_normalization_layer_4 = nn.BatchNorm2d(128)
        self.batch_normalization_layer_5 = nn.BatchNorm2d(128)
        self.batch_normalization_layer_6 = nn.BatchNorm2d(128)
        self.batch_normalization_layer_7 = nn.BatchNorm2d(256)
        
        self.pool_layer_1 = nn.MaxPool2d(2, 2)
        self.pool_layer_2 = nn.MaxPool2d(2, 2)

        self.dropout_layer_1 = nn.Dropout(0.2)
        self.dropout_layer_2 = nn.Dropout(0.2)        
        self.dropout_layer_3 = nn.Dropout(0.2)
        
        # Define fully connected layers
        self.fully_connected_layer_1 = nn.Linear(256 * 14 * 14, 256)
        self.fully_connected_layer_2 = nn.Linear(256, 128)
        self.fully_connected_layer_3 = nn.Linear(128, num_classes)
        
        self.batch_normalization_fully_connected_layer_1 = nn.BatchNorm1d(256)
        self.batch_normalization_fully_connected_layer_2 = nn.BatchNorm1d(128)


    def forward(self, x):

        x = self.batch_normalization_layer_1(F.relu(self.convolution_layer_1(x)))
        x = self.batch_normalization_layer_2(F.relu(self.convolution_layer_2(x)))
        x = self.batch_normalization_layer_3(F.relu(self.convolution_layer_3(x)))
        x = self.pool_layer_1(x)
        x = self.dropout_layer_1(x)

        x = self.batch_normalization_layer_4(F.relu(self.convolution_layer_4(x)))
        x = self.batch_normalization_layer_5(F.relu(self.convolution_layer_5(x)))
        x = self.batch_normalization_layer_6(F.relu(self.convolution_layer_6(x)))
        x = self.pool_layer_1(x)
        x = self.dropout_layer_2(x)

        x = self.batch_normalization_layer_7(F.relu(self.convolution_layer_7(x)))
        x = self.pool_layer_2(x)
        x = self.dropout_layer_3(x)

        x = x.view(-1, 256 * 14 * 14)
        x = F.relu(self.batch_normalization_fully_connected_layer_1(self.fully_connected_layer_1(x)))
        x = F.relu(self.batch_normalization_fully_connected_layer_2(self.fully_connected_layer_2(x)))
        x = self.fully_connected_layer_3(x)
        return x
