"""Scope the deeper A07/A08 accounts and their four-to-eight-line reader links."""

MANIFEST = 'provenance/platform-presentation.v57.json'
MANIFEST_SHA256 = '02b4091576a82c85e6db1b5a7094873dfeae5a814285368a6ba35b69ca74f537'
PREDECESSOR = '5c6bc3ebbb77e520137d45554903f8fd7f3edcd5'
PRESENTATION_ID = 'PLATFORM-FOUR-EIGHT-DEEPENING-20261121-v57'
HTML_PATHS = (
    'index.html',
    'achievements/index.html',
    'topics/index.html',
    'topics/fluoroporphyrins/index.html',
    'topics/single-electron-transfer/index.html',
)
DOCUMENT_PATHS = (
    'README.md',
    'docs/ACADEMIC_ACHIEVEMENTS_zh-CN.md',
    'docs/PLATFORM_PURPOSE_zh-CN.md',
    'docs/A07_ACADEMIC_ACHIEVEMENTS_zh-CN.md',
    'docs/A08_ACADEMIC_ACHIEVEMENTS_zh-CN.md',
    'content/a07-biography-narrative.v1.json',
    'content/a08-biography-narrative.v1.json',
)
CHANGED_FILES = (
    {'site/' + name for name in HTML_PATHS}
    | set(DOCUMENT_PATHS)
    | {'scripts/story_sources_publication.py'}
)
V56_ADDITIONS = {
    'provenance/platform-presentation.v56.json':
        ('18c1948ba8661badc7da892195dff31e915fdc66ec3ddbf47df1c448e1b2bfc6', 51723),
    'scripts/four_primary_achievements_publication.py':
        ('071a0ac3b907bd4657143aa79efed74ba5268bab3e90666328ee7c5e9ab6a0ab', 1010),
}
