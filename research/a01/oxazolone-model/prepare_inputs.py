"""Prepare named, mapped starting graphs from visually read primary figures."""
import argparse
import hashlib
import json
from pathlib import Path
from rdkit import Chem, rdBase
from rdkit.Chem import AllChem, Draw, rdMolDescriptors

root = Path(__file__).resolve().parents[3]
parser = argparse.ArgumentParser(description='Prepare source-derived paired graphs and starting geometries, without energy calculations')
parser.add_argument('--output', type=Path, required=True, help='New output directory; existing inputs are never overwritten')
args = parser.parse_args()
target = args.output.absolute()
if target.exists():
    parser.error('Use a new output directory')
target.mkdir(parents=True)
pairs = [
    ('A01-P134-IV-CF3', '[O:1]=[C:2]1[O:3][C:4]([c:5]2[cH:6][cH:7][cH:8][cH:9][cH:10]2)=[N:11][C:12]1=[C:13]([C:14]([F:16])([F:17])[F:18])[C:15]([F:19])([F:20])[F:21]', 'C12H5F6NO2'),
    ('A01-P134-IV-CH3', '[O:1]=[C:2]1[O:3][C:4]([c:5]2[cH:6][cH:7][cH:8][cH:9][cH:10]2)=[N:11][C:12]1=[C:13]([CH3:14])[CH3:15]', 'C12H11NO2'),
]
records, drawings = [], []
for identity, smiles, expected in pairs:
    molecule = Chem.MolFromSmiles(smiles)
    formula = rdMolDescriptors.CalcMolFormula(molecule)
    if formula != expected:
        raise ValueError((identity, formula, expected))
    drawing = Chem.Mol(molecule)
    for atom in drawing.GetAtoms():
        atom.SetAtomMapNum(0)
    drawings.append(drawing)
    explicit = Chem.AddHs(molecule)
    parameters = AllChem.ETKDGv3()
    parameters.randomSeed = 20261111
    parameters.pruneRmsThresh = 0.35
    conformers = list(AllChem.EmbedMultipleConfs(explicit, numConfs=8, params=parameters))
    if not conformers:
        raise ValueError('No starting geometry')
    sdf_path = target / f'{identity}.sdf'
    with Chem.SDWriter(str(sdf_path)) as writer:
        explicit.SetProp('_Name', identity)
        explicit.SetProp('scientific_status', 'AI graph transcription; unoptimized starting geometry; review_required')
        for conformer in conformers:
            writer.write(explicit, confId=conformer)
    records.append({'id': identity, 'source_id': 'CQ-R01', 'source_pages': [1367, 1369],
                    'source_pdf_sha256': 'ea6b42bd6e976fa82219cf4ed0a48357f46d6d7cdd9d9619144e3a80bc714175',
                    'mapped_smiles': smiles, 'derived_formula': formula,
                    'formal_charge': Chem.GetFormalCharge(molecule), 'working_multiplicity': 1,
                    'starting_conformers': len(conformers), 'sdf': sdf_path.name,
                    'sdf_sha256': hashlib.sha256(sdf_path.read_bytes()).hexdigest(),
                    'identity_status': 'AI_visual_transcription_pending_independent_chemical_review',
                    'geometry_status': 'embedded_not_electronic_structure_optimized',
                    'energy_or_frequency_calculation': 'not_performed'})
svg = Draw.MolsToGridImage(drawings, molsPerRow=2, subImgSize=(450, 330),
                          legends=['CF3: paper IV', 'CH3: comparator'], useSVG=True)
(target / 'matched-pair.svg').write_text(svg, encoding='utf-8')
record = {'schema_version': '1.0', 'task_id': 'A01-OX-M1', 'scientific_review_status': 'review_required',
          'preparation_method': 'RDKit ETKDGv3; 8 requested starting embeddings, RMS pruning0.35A; no force field or quantum energy',
          'rdkit_version': rdBase.rdkitVersion, 'seed': 20261111, 'structures': records,
          'boundary': 'Starting inputs only; neither structural uniqueness nor reaction mechanism verified'}
(target / 'structures.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'task_id': record['task_id'], 'structures': [(r['id'],r['derived_formula'],r['starting_conformers']) for r in records]}))
