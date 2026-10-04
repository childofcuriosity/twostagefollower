from common import *
import importlib.util
spec=importlib.util.spec_from_file_location('legacy_audit',S/'src/audit.py');legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)
HEADER=re.compile(r'^([A-Za-z][A-Za-z0-9]*):$')
OP=re.compile(r'^(rev|rot|inc|neg|swap|ends) ([0-9]) ([0-9]) ([0-9]) ([0-9])$')
def grade(row,condition):
 # Legacy main endpoint ignores label identity; only extend header syntax to proposed labels.
 normalized=dict(row);normalized['raw']='\n'.join('step:' if HEADER.fullmatch(x) else x for x in row['raw'].split('\n'))
 result=legacy.check(normalized)
 if condition in ['flat','macro']:
  old=legacy.check(row)
  assert old['strict_trace']==result['strict_trace'] and old['accuracy']==result['accuracy'] and old['correct_prefix_early_answer']==result['correct_prefix_early_answer']
 segments=[];current=None;state=tuple(row['x']);unsegmented=False
 for line in row['raw'].splitlines():
  h=HEADER.fullmatch(line);op=OP.fullmatch(line)
  if h:
   current={'label':h[1],'ops':[],'numeric':True};segments.append(current)
  elif op:
   actual=tuple(map(int,op.groups()[1:]));correct=actual==dsl.step(state,op[1]);state=actual
   if current is None:unsegmented=True
   else:current['ops'].append(op[1]);current['numeric'] &= correct
  elif line.startswith('Answer:'):current=None
 labels=[s['label'] for s in segments];chain=row['chain'];lib=WORLD['library']
 expected_labels=([f'step{i}' for i in range(1,len(chain)+1)] if condition=='position' else [ALIASES[t] for t in chain] if condition=='alias' else [WORLD['names'][t] for t in chain] if condition=='macro' else ['step']*len(chain))
 segment_good=[];internal_short=0
 for i,s in enumerate(segments):
  wanted=lib[chain[i]] if i<len(chain) else None
  segment_good.append(wanted is not None and s['ops']==wanted and s['numeric'])
  internal_short+=bool(wanted is not None and 0<len(s['ops'])<len(wanted) and s['ops']==wanted[:len(s['ops'])] and s['numeric'])
 result.update(label_sequence_correct=labels==expected_labels,all_emitted_segments_correct=bool(segments) and all(segment_good) and not unsegmented,
  internal_short_any=bool(internal_short),emitted_segments=len(segments),expected_labels=expected_labels,emitted_labels=labels,
  label_aware_complete=bool(result['strict_trace'] and labels==expected_labels),segment_ops=[s['ops'] for s in segments])
 return result
