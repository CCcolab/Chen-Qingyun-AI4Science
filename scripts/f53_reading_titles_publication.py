"""Record the A04 reader-facing section titles and links."""

MANIFEST = 'provenance/platform-presentation.v71.json'
MANIFEST_SHA256 = '49455e679fac0d2df0d7f1a259c0ce49a0babc57f1a21fe8b9327a61b611713d'
PREDECESSOR = '20f3e1cdb8c4514cadd76cd4b6c5354cebd91584'
PRESENTATION_ID = 'PLATFORM-A04-READING-TITLES-20261127-v71'
HTML_PATHS = (
    'achievements/index.html',
    'topics/f53/index.html',
    'topics/index.html',
)
CHANGED_FILES = {
    'scripts/story_sources_publication.py',
    'site/achievements/index.html',
    'site/topics/f53/index.html',
    'site/topics/index.html',
}
V70_ADDITIONS = {
    'provenance/platform-presentation.v70.json': (
        'c1ebaef2a37c3552f52548453f0f400fe091414d6906a872e38a2a4a5e1c2871', 13392,
    ),
    'scripts/f53_scientific_boundaries_publication.py': (
        '006923eb35f6e0b891dddf5887fd6929528e311ec0022492f6183717ce6ff9a5', 805,
    ),
}
