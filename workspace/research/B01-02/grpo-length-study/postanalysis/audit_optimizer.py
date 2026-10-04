"""CPU audit of actual initialization/endpoint adapter and optimizer states."""
import json
import math
from pathlib import Path
import torch
from safetensors.torch import load_file

torch.set_num_threads(1)
R = Path(__file__).resolve().parents[1]
assert (R / 'analysis/computation-complete.json').exists()
TASKS = ['7b-L3', '7b-L4', '7b-L5', '14b-L5', '14b-L6', '14b-L7']
records = []
for task in TASKS:
    for seed in [301, 302, 303]:
        for condition in ['STEP', 'NAME']:
            run = R / task / f'runs/v1-{condition}-s{seed}'
            initial = load_file(str(run / 'checkpoint-000/adapter_model.safetensors'))
            final = load_file(str(run / 'checkpoint-100/adapter_model.safetensors'))
            assert initial.keys() == final.keys()
            b_keys = [k for k in initial if 'lora_B' in k]
            assert b_keys and all(torch.count_nonzero(initial[k]).item() == 0 for k in b_keys)
            assert all(torch.isfinite(v).all().item() for v in initial.values())
            assert all(torch.isfinite(v).all().item() for v in final.values())
            assert all(v.dtype == torch.float32 for v in initial.values())
            assert all(v.dtype == torch.float32 for v in final.values())
            distance_squared = sum(float((final[k] - initial[k]).double().square().sum())
                                   for k in initial)
            optimizer0 = torch.load(run / 'checkpoint-000/optimizer.pt',
                                    map_location='cpu', weights_only=False)
            optimizer100 = torch.load(run / 'checkpoint-100/optimizer.pt',
                                      map_location='cpu', weights_only=False)
            assert optimizer0['update'] == 0 and not optimizer0['optimizer']['state']
            assert optimizer100['update'] == 100
            states = optimizer100['optimizer']['state']
            assert len(states) == len(initial)
            assert all(float(s['step']) == 100 for s in states.values())
            assert all(torch.isfinite(v).all().item() for s in states.values()
                       for v in s.values() if torch.is_tensor(v))
            records.append(dict(task=task, seed=seed, condition=condition,
                                initial_lora_B_all_zero=True, initial_optimizer_empty=True,
                                endpoint_all_optimizer_steps=100, adapter_tensors=len(initial),
                                adapter_and_optimizer_finite=True, adapter_dtype='float32',
                                endpoint_adapter_l2_change=math.sqrt(distance_squared)))
            del initial, final, optimizer0, optimizer100, states
assert len(records) == 36
(R / 'analysis/optimizer-audit.json').write_text(json.dumps(
    dict(passed=True, records=records,
         note='Zero endpoint change is permitted for zero-signal runs; it is recorded, not treated as an implementation failure.'),
    indent=2) + '\n')
print('Actual initialization and optimizer endpoint audit passed for36 runs.')
