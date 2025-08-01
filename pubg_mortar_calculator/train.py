import os
import json
import torch
import cv2
import torch.nn as nn
from torchvision import transforms
from torch.utils.data import Dataset, DataLoader, random_split
from PIL import Image
import numpy as np
from .grid_detector import GridDetector
from .height_detector import HeightDetector
from .custom_widgets import CustomImage
import torch.nn.functional as F

class MapDataset(Dataset):
    def __init__(self, folder_path, image_size=(512, 512)):
        self.folder_path = folder_path
        self.image_size = image_size
        self.data = []
        self.transform = transforms.Compose([
            transforms.Grayscale(),
            transforms.Resize(image_size),
            transforms.ToTensor()
        ])
        
        for file in os.listdir(folder_path):
            if file.endswith('.json'):
                json_path = os.path.join(folder_path, file)
                try:
                    with open(json_path, 'r') as f:
                        info = json.load(f)
                    if "real_distance" not in info:
                        continue
                    image_path = os.path.join(folder_path, info['name'] + '.png')
                    if os.path.exists(image_path):
                        self.data.append((image_path, info))
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Skipping {file}: {str(e)}")

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        image_path, info = self.data[idx]
        try:
            image = cv2.imread(image_path)
            player_pos, mark_pos = info['player_position'], info['mark_position']
            HeightDetector.cut_to_points(image, player_pos, mark_pos, 0.01)

            image = Image.fromarray(image).convert('RGB')
            width, height = image.size
            norm_gray_image = self.transform(image)
            
            grid_gap = info['grid_gap']
            distance_km = GridDetector.get_distance(player_pos, mark_pos, grid_gap) / 1000
            norm_player_pos = (player_pos[0]/width, player_pos[1]/height)
            norm_mark_pos = (mark_pos[0]/width, mark_pos[1]/height)
            corrected_distance_km = info['real_distance'] / 1000

            return (
                norm_gray_image,
                torch.tensor(distance_km, dtype=torch.float32),         
                torch.tensor(corrected_distance_km, dtype=torch.float32),  
                torch.tensor(norm_player_pos, dtype=torch.float32),        
                torch.tensor(norm_mark_pos, dtype=torch.float32),          
            )
        except Exception as e:
            print(f"Error processing {image_path}: {str(e)}")
            # Return a placeholder or skip
            return self[(idx + 1) % len(self)]

class CorrectedDistanceModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.cnn = nn.Sequential(
            nn.Conv2d(1, 16, 3, padding=1), 
            nn.ReLU(), 
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1), 
            nn.ReLU(), 
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), 
            nn.ReLU(), 
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1), 
            nn.ReLU(), 
            nn.MaxPool2d(2),
            nn.Conv2d(128, 256, 3, padding=1), 
            nn.ReLU(), 
            nn.MaxPool2d(2),  # Output: [256, 16, 16]
            nn.AdaptiveAvgPool2d((1, 1))  # Output: [256, 1, 1]
        )
        self.fc = nn.Sequential(
            nn.Linear(256 + 1 + 2 + 2, 128),  # 256 features + distance + 2 positions
            nn.ReLU(),
            nn.Linear(128, 1)
        )

    def forward(self, image, distance, player_pos, mark_pos):
        x = self.cnn(image)
        x = x.view(x.size(0), -1)  # Flatten to [batch, 256]
        
        # Ensure all inputs have consistent batch dimension
        distance = distance.view(-1, 1)
        player_pos = player_pos.view(-1, 2)
        mark_pos = mark_pos.view(-1, 2)
        
        x = torch.cat((x, distance, player_pos, mark_pos), dim=1)
        return self.fc(x)

def train_model(data_dir, epochs=10, batch_size=8, save_path='models/corrector_xnn.pt'):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    full_dataset = MapDataset(data_dir)
    train_size = int(0.8 * len(full_dataset))
    val_size = len(full_dataset) - train_size
    train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=4)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=4)

    model = CorrectedDistanceModel().to(device)
    loss_fn = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-5)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=3, factor=0.5)

    best_val_loss = float('inf')
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    for epoch in range(epochs):
        model.train()
        train_loss = 0.0
        for image, distance, target, player_pos, mark_pos in train_loader:
            image = image.to(device)
            distance = distance.to(device)
            target = target.to(device).unsqueeze(1)  # Add output dimension
            player_pos = player_pos.to(device)
            mark_pos = mark_pos.to(device)
            
            optimizer.zero_grad()
            output = model(image, distance, player_pos, mark_pos)
            loss = loss_fn(output, target)
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * image.size(0)

        # Validation
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for image, distance, target, player_pos, mark_pos in val_loader:
                image = image.to(device)
                distance = distance.to(device)
                target = target.to(device).unsqueeze(1)
                player_pos = player_pos.to(device)
                mark_pos = mark_pos.to(device)
                
                output = model(image, distance, player_pos, mark_pos)
                loss = loss_fn(output, target)
                val_loss += loss.item() * image.size(0)

        train_loss /= len(train_loader.dataset)
        val_loss /= len(val_loader.dataset)
        scheduler.step(val_loss)
        
        print(f"Epoch {epoch+1}/{epochs} | Train Loss: {train_loss:.6f} | Val Loss: {val_loss:.6f} | LR: {optimizer.param_groups[0]['lr']:.2e}")

        # Save best model
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), save_path)
            print(f"Saved new best model with val loss: {val_loss:.6f}")

    print(f"Training complete. Best validation loss: {best_val_loss:.6f}")
    return model

def export_onnx(model, export_path="models/corrector_model.onnx"):
    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    model.eval().cpu()

    dummy_img = torch.randn(1, 1, 512, 512)
    dummy_dist = torch.randn(1, 1)
    dummy_player_pos = torch.randn(1, 2)
    dummy_mark_pos = torch.randn(1, 2)

    torch.onnx.export(
        model,
        (dummy_img, dummy_dist, dummy_player_pos, dummy_mark_pos),
        export_path,
        input_names=["image", "distance_km", "norm_player_pos", "norm_mark_pos"],
        output_names=["corrected_distance"],
        dynamic_axes={
            "image": {0: "batch_size"},
            "distance_km": {0: "batch_size"},
            "norm_player_pos": {0: "batch_size"},
            "norm_mark_pos": {0: "batch_size"},
            "corrected_distance": {0: "batch_size"}
        },
        opset_version=14,
        do_constant_folding=True
    )
    print(f"ONNX model saved to: {export_path}")

if __name__ == "__main__":
    folder = "tests/test_samples"
    model = train_model(folder, epochs=10)
    export_onnx(model) 