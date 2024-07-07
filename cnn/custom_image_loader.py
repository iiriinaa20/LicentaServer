from torchvision.datasets import ImageFolder
from PIL import Image
import os

class CustomImageFolder(ImageFolder):
    def __init__(self, images_root_directory, transform=None):
        super().__init__(images_root_directory, transform=transform)
        self.class_to_idx = {cls: i for i, cls in enumerate(sorted(os.listdir(images_root_directory)))}

    def __getitem__(self, index):
        path, target = self.samples[index]
        sample = self.loader(path)

        if self.transform is not None:
            sample = self.transform(sample)
        if self.target_transform is not None:
            target = self.target_transform(target)

        # Convert class name to index
        target = self.class_to_idx[os.path.basename(os.path.dirname(path))]
        return sample, target
    
    def display_first_image(self):
        if len(self.samples) > 0:
            path, _ = self.samples[0]
            image = Image.open(path)
            image.show()
        else:
            print("No images found in the dataset.")
    