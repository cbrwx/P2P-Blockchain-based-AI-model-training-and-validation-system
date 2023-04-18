import torch
import torch.nn as nn
from torch.optim import Optimizer
from torch.utils.data import Dataset
import numpy as np
import pandas as pd
from torch.utils.data import Dataset

class CsvDataset(Dataset):
    def __init__(self, file_path, transform=None):
        self.data = pd.read_csv(file_path)
        self.transform = transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        text = self.data.iloc[idx]['text']
        label = self.data.iloc[idx]['label']
        
        if self.transform:
            text = self.transform(text)

        return text, label

class DynamicTransformer(nn.Module):
    def __init__(self, config):
        super(DynamicTransformer, self).__init__()
        self.layers = nn.ModuleList()
        self.attention_heads = config['initial_attention_heads']
        self.embedding = nn.Embedding(config['vocab_size'], config['embedding_dim'])

        for _ in range(config['initial_layers']):
            layer = nn.TransformerEncoderLayer(
                d_model=config['embedding_dim'],
                nhead=self.attention_heads,
                dim_feedforward=config['feedforward_dim']
            )
            self.layers.append(layer)

    def forward(self, inputs):
        x = self.embedding(inputs)
        for layer in self.layers:
            x = layer(x)
        return x

    def adjust_architecture(self, task_complexity):
        if task_complexity == 'add_layer':
            new_layer = nn.TransformerEncoderLayer(
                d_model=self.embedding.embedding_dim,
                nhead=self.attention_heads,
                dim_feedforward=self.layers[0].fc1.in_features
            )
            self.layers.append(new_layer)

        elif task_complexity == 'add_attention_head':
            self.attention_heads += 1
            for idx, layer in enumerate(self.layers):
                new_layer = nn.TransformerEncoderLayer(
                    d_model=self.embedding.embedding_dim,
                    nhead=self.attention_heads,
                    dim_feedforward=self.layers[idx].fc1.in_features
                )
                self.layers[idx] = new_layer
