# Differences from the original trainers

Original trainer source files are unchanged; each new job saves driver_snapshot.py. The wrapper only extends allowed condition values, redirects the output root to the new directory, and replaces target-text construction functions. LoRA, optimizer, learning rate, loss normalization, batch order, gradient clipping, and original development evaluation follow the existing code. New label targets are implemented in target in src/common.py.

In config.json written by the old program, source_sha256 points to driver_snapshot.py; complete.json separately records the original trainer hash. Original base models, revisions, trainable parameters, environments, and actual example/token counts are audited separately.

After the original formal test, the wrapper uses the same model still in memory to evaluate the earlier independent set with batch4, greedy decoding, and a 512-token cap, additionally saving raw tokens and actual prompts. It does not retrain, alter the original formal test, or place reference computations in generation context.

## Trainer for qwen1.5b

```diff
--- original
+++ new-isolated-driver
@@ -33,7 +33,7 @@
   rs=[r for r in results if r['split']==key];groups[key]={'n':len(rs),'accuracy':sum(r['correct'] for r in rs)/len(rs),'program_accuracy':sum(r['primitive_sequence_correct'] for r in rs)/len(rs),'valid_execution':sum(r['execution_steps_correct'] for r in rs)/len(rs)}
  return {'groups':groups,'elapsed_seconds':time.time()-start,'generated_tokens':sum(r['generated_tokens'] for r in results)}
 def main():
- ap=argparse.ArgumentParser();ap.add_argument('--condition',choices=['flat','macro','natural','shuffled','frozen'],required=True);ap.add_argument('--seed',type=int,default=11);ap.add_argument('--world',default='original');ap.add_argument('--steps',type=int,default=512);ap.add_argument('--microbatch',type=int,default=16);ap.add_argument('--accum',type=int,default=2);ap.add_argument('--calibrate',action='store_true');ap.add_argument('--eval-only',action='store_true');ap.add_argument('--with-library',action='store_true');ap.add_argument('--tag',default='');args=ap.parse_args()
+ ap=argparse.ArgumentParser();ap.add_argument('--condition',choices=['flat','macro','natural','shuffled','frozen','position','alias'],required=True);ap.add_argument('--seed',type=int,default=11);ap.add_argument('--world',default='original');ap.add_argument('--steps',type=int,default=512);ap.add_argument('--microbatch',type=int,default=16);ap.add_argument('--accum',type=int,default=2);ap.add_argument('--calibrate',action='store_true');ap.add_argument('--eval-only',action='store_true');ap.add_argument('--with-library',action='store_true');ap.add_argument('--tag',default='');args=ap.parse_args()
  runid=f'{args.condition}-{args.world}-s{args.seed}'+('-calibration' if args.calibrate else '')+args.tag
  out=ROOT/'runs'/runid;out.mkdir(exist_ok=True);set_seed(args.seed);torch.set_num_threads(4)
  tok=AutoTokenizer.from_pretrained(ROOT/'model',local_files_only=True);tok.pad_token=tok.eos_token
```

## Trainer for qwen32b

```diff
--- original
+++ new-isolated-driver
@@ -35,9 +35,9 @@
   rs=[r for r in results if r['split']==key];groups[key]={'n':len(rs),'accuracy':sum(r['correct'] for r in rs)/len(rs),'program_accuracy':sum(r['primitive_sequence_correct'] for r in rs)/len(rs),'valid_execution':sum(r['execution_steps_correct'] for r in rs)/len(rs)}
  return {'groups':groups,'elapsed_seconds':time.time()-start,'generated_tokens':sum(r['generated_tokens'] for r in results)}
 def main():
- ap=argparse.ArgumentParser();ap.add_argument('--model',choices=['qwen32b','qwen7b'],required=True);ap.add_argument('--lr',type=float,default=3e-4);ap.add_argument('--probe-only',action='store_true');ap.add_argument('--condition',choices=['flat','macro','natural','shuffled','frozen'],required=True);ap.add_argument('--seed',type=int,default=11);ap.add_argument('--world',default='original');ap.add_argument('--steps',type=int,default=512);ap.add_argument('--microbatch',type=int,default=4);ap.add_argument('--accum',type=int,default=8);ap.add_argument('--calibrate',action='store_true');ap.add_argument('--eval-only',action='store_true');ap.add_argument('--with-library',action='store_true');ap.add_argument('--tag',default='');args=ap.parse_args()
+ ap=argparse.ArgumentParser();ap.add_argument('--model',choices=['qwen32b','qwen7b'],required=True);ap.add_argument('--lr',type=float,default=3e-4);ap.add_argument('--probe-only',action='store_true');ap.add_argument('--condition',choices=['flat','macro','natural','shuffled','frozen','position','alias'],required=True);ap.add_argument('--seed',type=int,default=11);ap.add_argument('--world',default='original');ap.add_argument('--steps',type=int,default=512);ap.add_argument('--microbatch',type=int,default=4);ap.add_argument('--accum',type=int,default=8);ap.add_argument('--calibrate',action='store_true');ap.add_argument('--eval-only',action='store_true');ap.add_argument('--with-library',action='store_true');ap.add_argument('--tag',default='');args=ap.parse_args()
  global ROOT
- ROOT=ROOT/args.model
+ # ROOT supplied by isolated wrapper
  runid=f'{args.condition}-{args.world}-s{args.seed}'+('-calibration' if args.calibrate else '')+args.tag
  out=ROOT/'runs'/runid;out.mkdir(exist_ok=False);set_seed(args.seed);torch.set_num_threads(4)
  tok=AutoTokenizer.from_pretrained(ROOT/'model',local_files_only=True);tok.pad_token=tok.eos_token
```

