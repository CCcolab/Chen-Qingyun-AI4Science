"""Scope the public-label and historical-navigation CI fixes after v59."""

MANIFEST = 'provenance/platform-presentation.v60.json'
MANIFEST_SHA256 = 'e932b4cc9aa011e1a5e493c27d5f0409ec94d6d3b49aa71932cc15833ca5d153'
PREDECESSOR = '9b1831a57f1185d5fa81895997a7579111db5d41'
PRESENTATION_ID = 'PLATFORM-CI-COMPATIBILITY-20261122-v60'
HTML_PATHS = ('research/index.html',)
DOCUMENT_PATHS = ()
CHANGED_FILES = {
    'site/research/index.html',
    'scripts/check_navigation.py',
    'scripts/story_sources_publication.py',
}
V59_ADDITIONS = {
    'provenance/platform-presentation.v59.json':
        ('b50513ba1f83c131fffaf6da0cbf32e0b63330f325c4a15033740d4602c9a75b', 66905),
    'scripts/reader_source_cleanup_publication.py':
        ('6345a059b2b1027db0ed3f6ae96f73dd9454672f0b11912575304f87588d3a30', 1374),
}
