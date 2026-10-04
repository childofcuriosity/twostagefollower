"""Control observed nondeterminism in local queue experiments; no oracle access."""
from agent import tool as original_tool
from sandbox import execute
PRELUDE='''import datetime as _clock_datetime, time as _clock_time, random as _clock_random, os as _clock_os
_clock_epoch=1790294400.0
_clock_original_datetime=_clock_datetime.datetime
_clock_original_date=_clock_datetime.date
class _FixedDateTime(_clock_original_datetime):
    @classmethod
    def now(cls,tz=None):
        return cls.fromtimestamp(_clock_epoch,tz)
    @classmethod
    def utcnow(cls):
        return cls.utcfromtimestamp(_clock_epoch)
    @classmethod
    def today(cls):
        return cls.now()
class _FixedDate(_clock_original_date):
    @classmethod
    def today(cls):
        return cls(2026,9,25)
_clock_datetime.datetime=_FixedDateTime
_clock_datetime.date=_FixedDate
_clock_old_localtime=_clock_time.localtime
_clock_old_gmtime=_clock_time.gmtime
_clock_old_ctime=_clock_time.ctime
_clock_old_strftime=_clock_time.strftime
_clock_time.time=lambda:_clock_epoch
_clock_time.time_ns=lambda:int(_clock_epoch*1000000000)
_clock_time.localtime=lambda seconds=None:_clock_old_localtime(_clock_epoch if seconds is None else seconds)
_clock_time.gmtime=lambda seconds=None:_clock_old_gmtime(_clock_epoch if seconds is None else seconds)
_clock_time.ctime=lambda seconds=None:_clock_old_ctime(_clock_epoch if seconds is None else seconds)
_clock_time.strftime=lambda fmt,t=None:_clock_old_strftime(fmt,_clock_old_localtime(_clock_epoch) if t is None else t)
_clock_random.seed(20260925)
_clock_rng=_clock_random.Random(20260925)
_clock_os.urandom=lambda n:_clock_rng.randbytes(n)
_clock_random._urandom=_clock_os.urandom
'''
def tool(work,root,name,args):
 if name=='run_python':return execute(root,PRELUDE+'\n'+args['code'])
 return original_tool(work,root,name,args)
def canonical_error(ex,work):return {'error':type(ex).__name__+': '+str(ex).replace(str(work),'/workspace')[:1000]}
