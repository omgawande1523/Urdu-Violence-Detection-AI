import torch
import torch.nn as nn
from transformers import AutoModel, AutoConfig

class MultiHeadAttention(nn.Module):
    def __init__(self, embed_dim: int, num_heads: int):
        super().__init__()
        self.attention = nn.MultiheadAttention(embed_dim=embed_dim, num_heads=num_heads, batch_first=True)
        
    def forward(self, x, mask=None):
        # x shape: [batch_size, seq_len, embed_dim]
        # PyTorch attention takes key_padding_mask as a boolean tensor where True represents padding
        attn_output, attn_weights = self.attention(x, x, x, key_padding_mask=mask)
        return attn_output, attn_weights

class HierarchicalViolenceClassifier(nn.Module):
    def __init__(self, model_name: str = "xlm-roberta-base", 
                 lstm_hidden_dim: int = 128, 
                 num_heads: int = 4, 
                 dropout_prob: float = 0.3):
        super().__init__()
        
        # 1. Base XLM-RoBERTa Model
        self.config = AutoConfig.from_pretrained(model_name)
        self.transformer = AutoModel.from_pretrained(model_name, config=self.config)
        
        # Freeze transformer embeddings / bottom layers if needed for speed, or fine-tune
        # Here we fine-tune the whole model but freeze embeddings to save memory
        for param in self.transformer.embeddings.parameters():
            param.requires_grad = False
            
        hidden_size = self.config.hidden_size
        
        # 2. Bidirectional LSTM
        self.bilstm = nn.LSTM(
            input_size=hidden_size,
            hidden_size=lstm_hidden_dim,
            num_layers=1,
            batch_first=True,
            bidirectional=True
        )
        
        # BiLSTM output dimension is lstm_hidden_dim * 2
        lstm_out_dim = lstm_hidden_dim * 2
        
        # 3. Multi-Head Attention Layer
        self.attention = MultiHeadAttention(embed_dim=lstm_out_dim, num_heads=num_heads)
        
        # 4. Pooling & Dropout
        self.dropout = nn.Dropout(dropout_prob)
        
        # 5. Classification Heads
        # Level 1: Violence (0) or Non-Violence (1) -> 2 logits
        self.level1_head = nn.Sequential(
            nn.Linear(lstm_out_dim, lstm_hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout_prob),
            nn.Linear(lstm_hidden_dim, 2)
        )
        
        # Level 2: Six Categories -> 6 logits
        # Categories: Gender (0), Economic (1), Ethnic (2), Political (3), Religious (4), General (5)
        self.level2_head = nn.Sequential(
            nn.Linear(lstm_out_dim, lstm_hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout_prob),
            nn.Linear(lstm_hidden_dim, 6)
        )

    def forward(self, input_ids, attention_mask=None):
        # Get XLM-RoBERTa outputs
        transformer_outputs = self.transformer(input_ids=input_ids, attention_mask=attention_mask)
        sequence_output = transformer_outputs.last_hidden_state # [batch_size, seq_len, hidden_size]
        
        # BiLSTM
        lstm_output, _ = self.bilstm(sequence_output) # [batch_size, seq_len, lstm_hidden_dim * 2]
        
        # Attention Mask adjustments (if attention_mask is provided)
        # key_padding_mask should be True for padding tokens
        key_padding_mask = None
        if attention_mask is not None:
            key_padding_mask = (attention_mask == 0)
            
        # Multi-Head Attention
        attn_output, attn_weights = self.attention(lstm_output, mask=key_padding_mask)
        
        # Global Average Pooling over sequence length
        if attention_mask is not None:
            # Mask out padding tokens before average pooling
            masked_attn = attn_output * attention_mask.unsqueeze(-1)
            pooled_output = masked_attn.sum(dim=1) / attention_mask.sum(dim=1, keepdim=True).clamp(min=1)
        else:
            pooled_output = attn_output.mean(dim=1)
            
        pooled_output = self.dropout(pooled_output)
        
        # Compute Logits
        level1_logits = self.level1_head(pooled_output)
        level2_logits = self.level2_head(pooled_output)
        
        return {
            "level1_logits": level1_logits,
            "level2_logits": level2_logits,
            "attention_weights": attn_weights
        }
