from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader

from tools.minimap_model import shared
from tools.minimap_model.dataset import MinimapDataset
from tools.minimap_model.model import MinimapModel

model = MinimapModel().to("cuda")
optimizer = torch.optim.Adam(model.parameters(), lr=0.0001)
loss_function = nn.CrossEntropyLoss().to("cuda")

train_dataset = MinimapDataset(shared.DATASET_PATH, transform=shared.TRAIN_TRANSFORM)
train_dataloader = DataLoader(train_dataset, shared.BATCH_SIZE, shuffle=True)

val_dataset = MinimapDataset(shared.DATASET_PATH, False, transform=shared.VAL_TRANSFORM)
val_dataloader = DataLoader(val_dataset, shared.BATCH_SIZE)
best_val_loss = float("inf")

for epoch in range(shared.EPOCH_COUNT):
    model.train()
    total_train_loss = 0.0

    for images, labels in train_dataloader:
        images = images.to("cuda").float()
        labels = labels.to("cuda")

        optimizer.zero_grad()
        predictions = model(images)
        loss = loss_function(predictions, labels)

        loss.backward()
        optimizer.step()

        total_train_loss += loss.item()

    avg_train_loss = total_train_loss / len(train_dataloader)

    model.eval()
    total_val_loss = 0.0
    correct = 0
    total = 0

    with torch.inference_mode():
        for val_images, val_labels in val_dataloader:
            val_images = val_images.to("cuda").float()
            val_labels = val_labels.to("cuda")

            val_preds = model(val_images)
            val_loss = loss_function(val_preds, val_labels)
            total_val_loss += val_loss.item()

            predicted_classes = torch.argmax(val_preds, dim=1)
            correct += (predicted_classes == val_labels).sum().item()
            total += val_labels.size(0)

    avg_val_loss = total_val_loss / len(val_dataloader)
    accuracy = (correct / total) * 100

    if avg_val_loss < best_val_loss:
        best_val_loss = avg_val_loss
        torch.save(model.state_dict(), Path("tools\\minimap_model\\best.pth"))

    print(
        f"Epoch: {epoch:03d} | Train Loss: {avg_train_loss:.4f} | Val Loss: {avg_val_loss:.4f} | Val Acc: {accuracy:.2f}%"
    )

model.eval()
print("\n--- Final Predictions Sample ---")
with torch.inference_mode():
    for val_images, val_labels in val_dataloader:
        val_images = val_images.to("cuda").float()
        outputs = model(val_images)
        predicted_classes = torch.argmax(outputs, dim=1)

        for pred, actual in zip(predicted_classes[:10], val_labels[:10]):
            print(f"Predicted: {pred.item()} | Actual: {actual.item()}")
        break
