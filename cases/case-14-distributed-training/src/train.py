import os
import random
import numpy as np
import torch
import torch.distributed as dist


def train(dataset, epochs=10):
    rank = dist.get_rank()
    seed = int(os.getenv('SEED', '42')) + rank
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    loader = dataset.loader(shuffle=True)
    model = build_model().cuda()
    model = torch.nn.parallel.DistributedDataParallel(model)
    optimizer = torch.optim.Adam(model.parameters())
    for epoch in range(epochs):
        for batch in loader:
            optimizer.zero_grad()
            loss = model(batch.cuda()).mean()
            loss.backward(); optimizer.step()
        torch.save(model.state_dict(), f'/shared/checkpoint-{epoch}.pt')
    return model
