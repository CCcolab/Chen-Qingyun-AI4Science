"""Wait for exactly one native controller; record its real exit without retry."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
RAW=ROOT/'scratch/m0-cf3-tight-gradient-diagnosis-20261113-v1'

def main():
    if sys.platform!='linux' or RAW.exists():
        raise RuntimeError('Fresh output and existing WSL backend required; never retry this batch')
    manifest=json.loads((HERE/'launch-manifest.v1.json').read_bytes())
    for item in manifest['files']:
        p=HERE/item['path']
        if hashlib.sha256(p.read_bytes()).hexdigest()!=item['sha256'] or p.stat().st_size!=item['size_bytes']:
            raise RuntimeError('Frozen launch file differs: '+item['path'])
    start=time.time()
    process=subprocess.Popen([sys.executable,'-u',str(HERE/'controller.py')],cwd=ROOT,stdin=subprocess.DEVNULL)
    code=process.wait()
    record={'started_epoch':start,'finished_epoch':time.time(),'returncode':code,
        'native_wait_completed':True,'retry_performed':False,'controller_pid':process.pid,
        'controller_sha256':hashlib.sha256((HERE/'controller.py').read_bytes()).hexdigest(),
        'scientific_review_status':'review_required','release_eligible':False}
    target=RAW/'native-launch-result.json'
    if RAW.exists():
        with target.open('x',encoding='utf-8',newline='\n') as stream:
            json.dump(record,stream,indent=2,allow_nan=False);stream.write('\n');stream.flush();os.fsync(stream.fileno())
    print(json.dumps({'native_controller_returncode':code,'native_launch_record':str(target) if RAW.exists() else None}),flush=True)
    return code

if __name__=='__main__':
    sys.exit(main())
