import torch

print(f'CUDA available: {torch.cuda.is_available()}')
print(f'CUDA version: {torch.version.cuda}')
print(f'PyTorch version: {torch.__version__}')
print(f'Device count: {torch.cuda.device_count()}')
if torch.cuda.is_available():
    print(f'Device name: {torch.cuda.get_device_name(0)}')
    print(f'Device capability: {torch.cuda.get_device_capability(0)}')
else:
    print('Device name: N/A')
    print('Device capability: N/A')
