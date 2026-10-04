import json,re,sys
from pathlib import Path
PARENT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(PARENT/'src'));import dsl
lib=json.loads((PARENT/'data/worlds.json').read_text())['original']['library']
def check(row):
 ops=list(dsl.expand(row['chain'],lib));truth=list(dsl.execute(row['x'],ops));assert truth==row['expected']
 raw=row['raw'];traces=re.findall(r'^(rev|rot|inc|neg|swap|ends) ([0-9]) ([0-9]) ([0-9]) ([0-9])$',raw,re.M)
 emitted=[t[0] for t in traces];state=tuple(row['x']);errors=0
 for t in traces:
  actual=tuple(map(int,t[1:]));errors+=actual!=dsl.step(state,t[0]);state=actual
 answers=re.findall(r'^Answer: ([0-9]) ([0-9]) ([0-9]) ([0-9])$',raw,re.M);pred=list(map(int,answers[-1])) if answers else None
 loose=dsl.answer(raw);assert (list(loose) if loose else None)==row['prediction'];assert (list(loose)==truth if loose else False)==row['correct']
 headers=re.findall(r'^([a-z]+):$',raw,re.M);strict_answer=pred==truth and len(answers)==1
 extra=[line for line in raw.splitlines() if line.strip() and not re.fullmatch(r'(?:[a-z]+:|(?:rev|rot|inc|neg|swap|ends) [0-9] [0-9] [0-9] [0-9]|Answer: [0-9] [0-9] [0-9] [0-9])',line)]
 correct_prefix=bool(emitted) and emitted==ops[:len(emitted)] and len(emitted)<len(ops) and not errors and len(answers)==1 and pred==list(state) and not extra
 two_ops=list(dsl.expand(row['chain'][:2],lib));two_stop=len(row['chain'])>2 and emitted==two_ops and correct_prefix
 limit=row.get('max_new_tokens',256);n=row['generated_tokens']
 # Existing records count non-EOS tokens; EOS equals PAD. Exact final token was not saved.
 stop_evidence='length_limit_reached' if n>=limit else ('eos_at_limit_or_earlier_ambiguous' if n==limit-1 else 'eos_before_length_limit_inferred')
 operation_mismatch=next((i for i,op in enumerate(emitted) if i>=len(ops) or op!=ops[i]),None)
 return dict(first_wrong_operation_index=operation_mismatch,wrong_operation=int(operation_mismatch is not None),numeric_step_error=int(errors>0),format_extra_lines=int(bool(extra)),missing_or_multiple_answer=int(len(answers)!=1),operation_prefix_only=int(bool(emitted) and emitted==ops[:len(emitted)] and len(emitted)<len(ops)),stop_evidence=stop_evidence,id=row['id'],split=row['split'],chain=row['chain'],required_calls=len(row['chain']),accuracy=int(strict_answer),strict_trace=int(strict_answer and emitted==ops and not errors and not extra),correct_prefix_early_answer=int(correct_prefix),exact_two_tools_early_answer=int(two_stop),two_output_segments=int(len(headers)==2),segments=len(headers),emitted_ops=len(emitted),required_ops=len(ops),arithmetic_errors=errors,unparsed_lines=len(extra),answer_present=int(len(answers)==1),budget_hit=int(row['generated_tokens']>=row.get('max_new_tokens',256)),loose_parser_false_positive=int(row['correct'] and not strict_answer))
