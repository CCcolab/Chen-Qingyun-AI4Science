"""Read-only independent saved-checkpoint check; no PySCF or SCF call."""
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RAW = ROOT/'scratch/m0-cf3-center-terminal-scf-20261113-v1'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    output = HERE/'independent-checkpoint-review.v1.json'
    if output.exists():
        raise FileExistsError('New independent review required; no overwrite')
    final_path = RAW/'result.json'; worker_path = RAW/'point/result.json'
    final = json.loads(final_path.read_bytes()); worker = json.loads(worker_path.read_bytes())
    paths = [final_path, worker_path, RAW/'process-result.json', RAW/'shared-budget.json']
    pins = {str(path.relative_to(ROOT)): {'sha256': sha(path), 'size_bytes': path.stat().st_size} for path in paths}
    checks = {'zero_gradient_attempts': all(final['budget_snapshot'][k]==0 for k in ['gradient_reservations','gradient_started','completed_gradients']),
        'exactly_one_SCF_reservation': final['budget_snapshot']['total_scf_attempts']==1,
        'worker_gradient_never_started': worker['gradient_started'] is False and worker['nuclear_gradient_calls']==0,
        'native_worker_returncode_present': isinstance(final['process']['returncode'],int)}
    h5_result = None
    if worker.get('electronic_complete') is True:
        import h5py
        import numpy as np
        checkpoint = RAW/'point/scf.chk'
        pins[str(checkpoint.relative_to(ROOT))] = {'sha256': sha(checkpoint), 'size_bytes': checkpoint.stat().st_size}
        with h5py.File(checkpoint,'r') as file:
            occ = np.asarray(file['scf/mo_occ'][()]); coeff = np.asarray(file['scf/mo_coeff'][()])
            energy = float(file['scf/e_tot'][()]); dumped = file['mol'][()]
            if isinstance(dumped,bytes): dumped = dumped.decode('utf-8')
            mol = json.loads(dumped)
        atom = mol.get('_atom')
        geometry_difference = None
        if atom is not None:
            coords = np.asarray([row[1] for row in atom])
            expected = np.asarray(worker['coordinates_bohr'])
            geometry_difference = float(np.max(np.abs(coords-expected)))
            checks['saved_molecule_geometry_Bohr_matches'] = coords.shape==(26,3) and geometry_difference<=1e-12
            checks['saved_molecule_symbols_match'] = [row[0] for row in atom]==worker['species_manifest']['symbols']
        else:
            checks['saved_molecule_geometry_Bohr_matches'] = None
        checks.update({'saved_checkpoint_SHA_matches_worker': sha(checkpoint)==worker['checkpoint_sha256'],
            'saved_restricted_occupation_0_2': bool(np.all(np.isfinite(occ)) and np.all(np.isclose(occ,0,atol=1e-12,rtol=0)|np.isclose(occ,2,atol=1e-12,rtol=0))),
            'saved_electron_count_154': abs(float(occ.sum())-154)<=1e-6,
            'saved_AO_count_matches': coeff.ndim==2 and coeff.shape[0]==worker['basis_functions'] and coeff.shape[1]==len(occ),
            'saved_energy_finite_and_matches': math.isfinite(energy) and abs(energy-worker['energy_Eh'])<=1e-12,
            'saved_occupation_matches_worker': occ.tolist()==worker['final_occupations']})
        h5_result = {'energy_Eh':energy,'electrons':float(occ.sum()),'AO_count':int(coeff.shape[0]),
            'geometry_max_difference_bohr':geometry_difference,'h5py_version':h5py.__version__,'numpy_version':np.__version__}
    for name, pin in pins.items():
        if sha(ROOT/name)!=pin['sha256'] or (ROOT/name).stat().st_size!=pin['size_bytes']:
            raise RuntimeError('Saved source changed during independent review')
    report = {'schema_version':'1.0','scientific_review_status':'review_required','release_eligible':False,
        'scope':'Saved HDF5 checkpoint read and ledger arithmetic, separate from worker; no PySCF import or new quantum evaluation',
        'new_quantum_calls':0,'checks':checks,'all_available_checks_passed':not any(value is False for value in checks.values()),
        'checkpoint':h5_result,'source_fingerprints':pins,'sources_unchanged':True}
    with output.open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(report,stream,ensure_ascii=False,indent=2,allow_nan=False);stream.write('\n')
    print(json.dumps({'checkpoint_review_passed':report['all_available_checks_passed'],'checks':len(checks),'new_quantum_calls':0}))
    return 0 if report['all_available_checks_passed'] else 1


if __name__=='__main__':
    raise SystemExit(main())
