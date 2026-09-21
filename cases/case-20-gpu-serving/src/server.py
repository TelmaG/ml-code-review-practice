import torch
from fastapi import FastAPI
from preprocess import preprocess
from model import Model

app = FastAPI()
model = Model().cuda()

@app.post('/predict')
def predict(payload: dict):
    images = preprocess(payload['images'])
    tensor = torch.tensor(images).cuda()
    with torch.no_grad():
        output = model(tensor)
    torch.cuda.synchronize()
    return {'scores': output.cpu().tolist()}
