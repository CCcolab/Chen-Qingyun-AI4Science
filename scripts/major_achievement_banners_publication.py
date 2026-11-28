"""Record the matching banners for the three remaining major achievements."""

MANIFEST = 'provenance/platform-presentation.v90.json'
MANIFEST_SHA256 = 'b7f2fc6b3d3bb59141c27f1ee583e6cfa03cb2601cb335ae9ad76ae9b6503e9a'
PREDECESSOR = '13d3af52c453f63175d40929a644e7f245fca31e'
PRESENTATION_ID = 'PLATFORM-MAJOR-ACHIEVEMENT-BANNERS-20261128-v90'
HTML_PATHS = (
    'topics/chen-reagent/index.html',
    'topics/fluoroporphyrins/index.html',
    'topics/single-electron-transfer/index.html',
)
CHANGED_FILES = {
    'scripts/story_sources_publication.py',
    'site/topics/chen-reagent/index.html',
    'site/topics/fluoroporphyrins/index.html',
    'site/topics/single-electron-transfer/index.html',
}
V89_ADDITIONS = {
    'provenance/platform-presentation.v89.json': (
        '380bb78e1fc75c2ff2f8adb26e696b579e656c83ac552e00edcff03e5da7a2b5', 16827,
    ),
    'scripts/a07_set_context_publication.py': (
        '681e8b52cd212a5ae0624d47fa2475b57e71262139d8733900e4a90678211bb3', 942,
    ),
}
