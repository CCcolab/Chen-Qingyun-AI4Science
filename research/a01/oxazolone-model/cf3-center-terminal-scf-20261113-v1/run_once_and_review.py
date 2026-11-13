"""Capture native controller exit, then read saved HDF5; never retry SCF."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RAW = ROOT/'scratch/m0-cf3-center-terminal-scf-20261113-v1'


def main():
    if RAW.exists():
        raise FileExistsError('Existing trial is final; no retry or renamed output')
    manifest = json.loads((HERE/'launch-manifest.v1.json').read_bytes())
    for row in manifest['files']:
        path = HERE/row['path']
        if hashlib.sha256(path.read_bytes()).hexdigest()!=row['sha256']:
            raise RuntimeError('Sealed launch source changed')
    began = time.time()
    controller = subprocess.run([sys.executable,'-u',str(HERE/'controller.py')],cwd=ROOT)
    recorded = {'native_controller_returncode':controller.returncode,'started_epoch':began,
        'controller_finished_epoch':time.time(),'quantum_retry_performed':False,'nuclear_gradient_calls':0}
    if (RAW/'result.json').exists():
        review = subprocess.run([sys.executable,'-u',str(HERE/'audit_checkpoint.py')],cwd=ROOT)
        recorded['independent_saved_checkpoint_review_returncode']=review.returncode
    else:
        recorded['independent_saved_checkpoint_review_returncode']=None
        recorded['review_not_started_reason']='Controller did not create a terminal scientific result'
    recorded['engineering_wrapper_finished_epoch']=time.time()
    with (HERE/'native-exit-observation.v1.json').open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(recorded,stream,ensure_ascii=False,indent=2);stream.write('\n')
    return controller.returncode


if __name__=='__main__':
    raise SystemExit(main())
