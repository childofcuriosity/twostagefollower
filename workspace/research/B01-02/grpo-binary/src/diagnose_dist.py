import json,os,torch,torch.distributed as dist
from datetime import timedelta
rank=int(os.environ['LOCAL_RANK']);torch.cuda.set_device(rank);dist.init_process_group('nccl',timeout=timedelta(seconds=60))
x=torch.ones((128,128),device='cuda',dtype=torch.bfloat16)*(dist.get_rank()+1)
dist.all_reduce(x)
assert float(x[0,0])==dist.get_world_size()*(dist.get_world_size()+1)/2
print(json.dumps(dict(rank=dist.get_rank(),world=dist.get_world_size(),gpu=torch.cuda.get_device_name(),torch=torch.__version__,bf16=bool(torch.cuda.is_bf16_supported()),allreduce='passed')),flush=True)
dist.destroy_process_group()
