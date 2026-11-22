"""Scope the A06 wording and four-card layout consistency update after v60."""

MANIFEST = 'provenance/platform-presentation.v61.json'
MANIFEST_SHA256 = '62cf0ea40368f73280ef2baded1f21cb2fe1050867362abaeaa77ad11214e09c'
PREDECESSOR = 'b297f2589fdd71a71736269f624ad3536fe96528'
PRESENTATION_ID = 'PLATFORM-MAJOR-ACHIEVEMENT-CARD-CONSISTENCY-20261122-v61'
HTML_PATHS = (
    'achievements/index.html',
    'index.html',
    'topics/chen-reagent/index.html',
)
DOCUMENT_PATHS = ('README.md',)
CHANGED_FILES = (
    {'site/' + name for name in HTML_PATHS}
    | set(DOCUMENT_PATHS)
    | {'scripts/story_sources_publication.py'}
)
V60_ADDITIONS = {
    'provenance/platform-presentation.v60.json':
        ('e932b4cc9aa011e1a5e493c27d5f0409ec94d6d3b49aa71932cc15833ca5d153', 5259),
    'scripts/ci_compatibility_publication.py':
        ('f574c5945c32b18f7f30192273d852911ab0811e7f88b827fbbc7094c033643a', 811),
}
