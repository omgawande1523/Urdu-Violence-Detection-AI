import os
import torch
import numpy as np
from torch.utils.data import DataLoader, Dataset
from torch.cuda.amp import autocast, GradScaler
from transformers import get_linear_schedule_with_warmup
import mlflow
from typing import Dict, Any, List, Optional
from ai_service.app.evaluation.metrics import calculate_metrics

class ViolenceDataset(Dataset):
    def __init__(self, encodings: Dict[str, torch.Tensor], level1_labels: List[int], level2_labels: List[int]):
        self.encodings = encodings
        self.level1_labels = level1_labels
        self.level2_labels = level2_labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['level1_label'] = torch.tensor(self.level1_labels[idx], dtype=torch.long)
        item['level2_label'] = torch.tensor(self.level2_labels[idx], dtype=torch.long)
        return item

    def __len__(self):
        return len(self.level1_labels)

class HierarchicalTrainer:
    def __init__(
        self,
        model: torch.nn.Module,
        train_dataset: ViolenceDataset,
        val_dataset: ViolenceDataset,
        device: str = "cpu",
        epochs: int = 5,
        batch_size: int = 16,
        lr: float = 2e-5,
        weight_decay: float = 0.01,
        warmup_steps: int = 100,
        early_stopping_patience: int = 3,
        checkpoint_dir: str = "./checkpoints",
        use_mlflow: bool = True
    ):
        self.model = model
        self.train_dataset = train_dataset
        self.val_dataset = val_dataset
        self.device = device
        self.epochs = epochs
        self.batch_size = batch_size
        self.lr = lr
        self.weight_decay = weight_decay
        self.warmup_steps = warmup_steps
        self.early_stopping_patience = early_stopping_patience
        self.checkpoint_dir = checkpoint_dir
        self.use_mlflow = use_mlflow
        
        os.makedirs(checkpoint_dir, exist_ok=True)
        self.model.to(self.device)

    def train(self) -> Dict[str, Any]:
        train_loader = DataLoader(self.train_dataset, batch_size=self.batch_size, shuffle=True)
        val_loader = DataLoader(self.val_dataset, batch_size=self.batch_size)
        
        # Optimizer with weight decay exclude for bias/LayerNorm
        no_decay = ["bias", "LayerNorm.weight"]
        optimizer_grouped_parameters = [
            {
                "params": [p for n, p in self.model.named_parameters() if not any(nd in n for nd in no_decay)],
                "weight_decay": self.weight_decay,
            },
            {
                "params": [p for n, p in self.model.named_parameters() if any(nd in n for nd in no_decay)],
                "weight_decay": 0.0,
            },
        ]
        optimizer = torch.optim.AdamW(optimizer_grouped_parameters, lr=self.lr)
        
        # Scheduler
        total_steps = len(train_loader) * self.epochs
        scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=self.warmup_steps, num_training_steps=total_steps)
        
        # Mixed Precision Scaler
        scaler = GradScaler()
        
        # Hierarchical losses
        criterion_level1 = torch.nn.CrossEntropyLoss()
        
        # Level 2 is only optimized when sample is Violence (class 0 in level 1, or mapped appropriately).
        # We can implement a masked cross entropy loss: only calculate loss for level 2 targets if level 1 is Violence.
        # Let's say level 1 label for Violence is 0. If label is 0, we count level 2 loss.
        # Let's define the criteria:
        criterion_level2 = torch.nn.CrossEntropyLoss(ignore_index=-1) # -1 can represent non-violence elements
        
        best_val_f1 = -1.0
        patience_counter = 0
        
        if self.use_mlflow:
            # Check if active run exists, if not start it
            if not mlflow.active_run():
                mlflow.start_run()
            mlflow.log_params({
                "lr": self.lr,
                "batch_size": self.batch_size,
                "epochs": self.epochs,
                "weight_decay": self.weight_decay,
                "warmup_steps": self.warmup_steps
            })

        for epoch in range(self.epochs):
            self.model.train()
            train_loss = 0.0
            
            for step, batch in enumerate(train_loader):
                optimizer.zero_grad()
                
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                l1_labels = batch['level1_label'].to(self.device)
                l2_labels = batch['level2_label'].to(self.device)
                
                # Forward pass with mixed precision autocast
                with autocast(enabled=(self.device == "cuda")):
                    outputs = self.model(input_ids, attention_mask=attention_mask)
                    
                    loss_l1 = criterion_level1(outputs["level1_logits"], l1_labels)
                    
                    # Create mask where level 1 label is Violence (label = 0).
                    # Level 2 labels for non-violence samples should be ignored (-1)
                    # Let's ensure l2_labels is ignored where l1_labels is 1 (Non-Violence).
                    # Level 1 classes: 0 -> Violence, 1 -> Non-Violence
                    l2_labels_masked = l2_labels.clone()
                    l2_labels_masked[l1_labels == 1] = -1
                    
                    loss_l2 = criterion_level2(outputs["level2_logits"], l2_labels_masked)
                    
                    # Total Loss combining heads
                    # Weight Level 2 loss: only calculate if we have violence samples in batch
                    total_loss = loss_l1
                    if (l1_labels == 0).sum() > 0:
                        total_loss += 0.5 * loss_l2 # Weigh Level 2 loss slightly lower or equal
                        
                # Backprop
                scaler.scale(total_loss).backward()
                
                # Gradient Clipping
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                
                scaler.step(optimizer)
                scaler.update()
                scheduler.step()
                
                train_loss += total_loss.item()
                
            train_loss /= len(train_loader)
            
            # Validation Step
            val_results = self.evaluate(val_loader, criterion_level1, criterion_level2)
            
            # Logging Epoch Metrics
            print(f"Epoch {epoch+1}/{self.epochs} - Train Loss: {train_loss:.4f} | Val Loss: {val_results['loss']:.4f} | Val F1: {val_results['f1']:.4f}")
            
            if self.use_mlflow:
                mlflow.log_metrics({
                    "train_loss": train_loss,
                    "val_loss": val_results["loss"],
                    "val_accuracy": val_results["accuracy"],
                    "val_f1": val_results["f1"]
                }, step=epoch)
                
            # Checkpoint & Early Stopping
            if val_results["f1"] > best_val_f1:
                best_val_f1 = val_results["f1"]
                patience_counter = 0
                # Save best checkpoint
                torch.save(self.model.state_dict(), os.path.join(self.checkpoint_dir, "best_model.pt"))
                print(f"--> Saved new best model checkpoint with Val F1: {best_val_f1:.4f}")
            else:
                patience_counter += 1
                if patience_counter >= self.early_stopping_patience:
                    print("Early stopping triggered!")
                    break
                    
        return {"best_val_f1": best_val_f1}

    def evaluate(self, loader: DataLoader, criterion_l1, criterion_l2) -> Dict[str, Any]:
        self.model.eval()
        val_loss = 0.0
        all_l1_preds = []
        all_l1_labels = []
        
        with torch.no_grad():
            for batch in loader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                l1_labels = batch['level1_label'].to(self.device)
                l2_labels = batch['level2_label'].to(self.device)
                
                outputs = self.model(input_ids, attention_mask=attention_mask)
                
                loss_l1 = criterion_l1(outputs["level1_logits"], l1_labels)
                l2_labels_masked = l2_labels.clone()
                l2_labels_masked[l1_labels == 1] = -1
                
                loss_l2 = criterion_l2(outputs["level2_logits"], l2_labels_masked)
                
                total_loss = loss_l1
                if (l1_labels == 0).sum() > 0:
                    total_loss += 0.5 * loss_l2
                    
                val_loss += total_loss.item()
                
                l1_preds = torch.argmax(outputs["level1_logits"], dim=-1).cpu().numpy()
                all_l1_preds.extend(l1_preds)
                all_l1_labels.extend(l1_labels.cpu().numpy())
                
        metrics = calculate_metrics(np.array(all_l1_labels), np.array(all_l1_preds), num_classes=2)
        metrics["loss"] = val_loss / len(loader)
        return metrics
