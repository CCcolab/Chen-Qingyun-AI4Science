"""Scope the reader-source cleanup and A03 footer layout after v58."""

MANIFEST = 'provenance/platform-presentation.v59.json'
MANIFEST_SHA256 = 'b50513ba1f83c131fffaf6da0cbf32e0b63330f325c4a15033740d4602c9a75b'
PREDECESSOR = 'c20f4f0a237b7406e9f7633a5c28caba33b74af7'
PRESENTATION_ID = 'PLATFORM-READER-SOURCE-CLEANUP-20261122-v59'
HTML_PATHS = (
    'achievements/index.html',
    'index.html',
    'people/index.html',
    'people/stories/index.html',
    'pftb/index.html',
    'research/index.html',
    'topics/chen-reagent/index.html',
    'topics/early-fluoroketones/index.html',
    'topics/f53/index.html',
    'topics/fluorinated-small-rings/index.html',
    'topics/fluoromonomers/index.html',
    'topics/fluoroporphyrins/index.html',
    'topics/perfluorosulfonates/index.html',
    'topics/refrigerants/index.html',
    'topics/single-electron-transfer/index.html',
    'topics/sulfonyl-fluoride/index.html',
)
DOCUMENT_PATHS = ()
CHANGED_FILES = (
    {'site/' + name for name in HTML_PATHS}
    | {'scripts/check_navigation.py', 'scripts/story_sources_publication.py'}
)
V58_ADDITIONS = {
    'provenance/platform-presentation.v58.json':
        ('33dde6a5985c6aaa4b574df058a5a53f5a9f0ffe61a8986073cae0372d3f5ffc', 9250),
    'scripts/homepage_compaction_publication.py':
        ('35e50e19ff5f0ecadc451e43e1209a145742962c5f4d7420b9da17f062e5f680', 764),
}
