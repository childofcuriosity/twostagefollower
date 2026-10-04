# 与旧训练器的差异

原训练源码文件未改动；每次新作业保存driver_snapshot.py。包装器只扩展condition参数允许值、把输出根指向新增目录，并替换目标文本构造函数。LoRA、优化器、学习率、损失归一化、batch顺序、梯度裁剪及原开发集评测逻辑沿旧代码。新标签目标实现见src/common.py的target。

旧程序写出的config.json中的source_sha256指driver_snapshot.py；complete.json另记录原训练器hash。旧基座、revision、trainable参数、环境与实际样本/token计数另行审计。

包装器在原正式测试后，用仍在内存中的同一模型运行旧独立集的batch4、greedy、512-token设置，额外保存原始token及实际prompt；不再次训练，不改变原正式测试，不把参考计算写入生成上下文。

## qwen1.5b对应训练器

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

## qwen32b对应训练器

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

