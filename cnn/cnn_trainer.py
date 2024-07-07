import torch
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from tqdm import tqdm
import torch.nn.functional as F
class CnnTrainer:
    def __init__(self, model, device, train_loader, val_loader, test_loader, optimizer, criterion, scheduler, writer, model_path):
        self.model = model
        self.device = device
        
        self.set_train_data(train_loader)
        self.set_val_data(val_loader)
        self.set_test_data(test_loader)

        self.optimizer = optimizer
        self.criterion = criterion
        self.scheduler = scheduler
        self.writer = writer
        self.model_path = model_path
        
    def set_train_data(self, train_loader):
        self.train_loader = train_loader
    
    def set_val_data(self, val_loader):
        self.val_loader = val_loader
    
    def set_test_data(self, test_loader):
        self.test_loader = test_loader

    def save_model(self, filepath):
        torch.save(self.model.state_dict(), filepath)

    def load_model(self, filepath):
        self.model.load_state_dict(torch.load(filepath))
        return self.model
    
    def write_metrics(self,dataset_type,loss, acc, precision, recall, f1, epoch):
        self.writer.add_scalar(f'Loss/{dataset_type}', loss, epoch)
        self.writer.add_scalar(f'Accuracy/{dataset_type}', acc, epoch)
        self.writer.add_scalar(f'Precision/{dataset_type}', precision, epoch)
        self.writer.add_scalar(f'Recall/{dataset_type}', recall, epoch)
        self.writer.add_scalar(f'F1_Score/{dataset_type}', f1, epoch)
    
    def calculate_metrics(self, dataset_type, epoch, loss, all_targets, all_predictions):
        acc = accuracy_score(all_targets, all_predictions)
        precision = precision_score(all_targets, all_predictions, average='weighted')
        recall = recall_score(all_targets, all_predictions, average='weighted')
        f1 = f1_score(all_targets, all_predictions, average='weighted')        
        self.write_metrics(dataset_type, loss, acc, precision, recall, f1, epoch)

        return acc

    def train(self, epoch):
        self.model.train()

        train_loss = 0
        all_targets = []
        all_predictions = []

        for batch_idx, (data, target) in enumerate(tqdm(self.train_loader, desc="Training")):
            data, target = data.to(self.device), target.to(self.device)

            self.optimizer.zero_grad()
            output = self.model(data)
            loss = self.criterion(output, target)
            loss.backward()
            self.optimizer.step()

            train_loss += loss.item()
            _, predicted = output.max(1)
            
            all_targets.extend(target.cpu().numpy())
            all_predictions.extend(predicted.cpu().numpy())

        train_loss /= len(self.train_loader.dataset)
        train_acc = self.calculate_metrics('train', epoch, train_loss, all_targets, all_predictions)

        return train_loss * 100, train_acc * 100

    def validate(self, epoch):
        self.model.eval()
        val_loss = 0
        all_targets = []
        all_predictions = []

        with torch.no_grad():
            for data, target in tqdm(self.val_loader, desc="Validation"):
                data, target = data.to(self.device), target.to(self.device)
                
                output = self.model(data)
                loss = self.criterion(output, target)

                val_loss += loss.item()
                _, predicted = output.max(1)

                all_targets.extend(target.cpu().numpy())
                all_predictions.extend(predicted.cpu().numpy())

        val_loss /= len(self.val_loader.dataset)
        val_acc = self.calculate_metrics('validation', epoch, val_loss, all_targets, all_predictions)

        return val_loss * 100, val_acc * 100

    def test(self):
        self.model.eval()

        all_targets = []
        all_predictions = []

        with torch.no_grad():
            for data, target in self.test_loader:
                data, target = data.to(self.device), target.to(self.device)

                output = self.model(data)
                pred = output.argmax(dim=1, keepdim=True)

                all_targets.extend(target.cpu().numpy())
                all_predictions.extend(pred.cpu().numpy())

        
        accuracy = accuracy_score(all_targets, all_predictions)
        precision = precision_score(all_targets, all_predictions, average='weighted')
        recall = recall_score(all_targets, all_predictions, average='weighted')
        f1 = f1_score(all_targets, all_predictions, average='weighted')

        print(f'Test Accuracy: {accuracy:.4f}')
        print(f'Test Precision: {precision:.4f}')
        print(f'Test Recall: {recall:.4f}')
        print(f'Test F1 Score: {f1:.4f}')

        return accuracy * 100, precision, recall, f1

    def run(self, epochs = 50, stop_val = 2e-4,model_path = 'model.pth', load_model = False):
        if load_model:
            print('Loading Model')
            self.load_model(model_path)
            print('Loaded Model')

        best_val_loss = float('inf')

        if epochs > 0:
            for epoch in range(1, epochs + 1):
                train_loss, train_acc = self.train(epoch)
                val_loss, val_acc = self.validate(epoch)
                print(f'Epoch: {epoch}, Train Loss: {train_loss:.6f}, Train Acc: {train_acc:.2f}%, Val Loss: {val_loss:.6f}, Val Acc: {val_acc:.2f}%')
                self.scheduler.step()

                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    self.save_model(model_path)

                if train_loss < stop_val:
                    break

    def predict(self, model_path, test_data):
        # print('Loading Best Model')
        self.load_model(model_path)
        
        # print('Starting Testing')
        self.set_test_data(test_data)
         
        self.model.eval()
        top5_predictions = []

        with torch.no_grad():
            for data in self.test_loader:
                data = data.to(self.device)
                output = self.model(data)

                # Get top 5 predictions with probabilities
                probabilities = F.softmax(output, dim=1)
                top5_probs, top5_indices = probabilities.topk(5, dim=1, largest=True, sorted=True)

                for i in range(data.size(0)):
                    top5_predictions.append({
                        'predictions': [
                            {'label': top5_indices[i, j].item(), 'probability': top5_probs[i, j].item()}
                            for j in range(5)
                        ]
                    })
                    
        return top5_predictions[0]

    # def set_test_data(self, test_data):
    #     test_size = len(test_data)
    #     self.test_loader = DataLoader(test_data, batch_size=128, shuffle=False)
