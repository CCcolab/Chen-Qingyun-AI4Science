"""Bounded source-reviewed deduplication over the exact immutable v45 site."""
from __future__ import annotations

import atexit
import ast
from collections import Counter
from html.parser import HTMLParser
from copy import deepcopy
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import tempfile

MANIFEST = 'provenance/platform-presentation.v46.json'
PREVIOUS_MANIFEST = 'provenance/platform-presentation.v45.json'
PREVIOUS_COMMIT = '44cf595073bac2ed613ac6a8476507edcc1ca88c'
PRESENTATION_ID = 'PLATFORM-SITE-DEDUPLICATION-20261119-v46'
ROUTES = ('index.html', 'achievements/index.html', 'research/index.html')
INTEGRATIONS = ('scripts/a01_publication_contract.py', 'scripts/check_site.py')
CHANGED_FILES = (*('site/'+route for route in ROUTES), *INTEGRATIONS)
NEW_FILES = ('scripts/site_deduplication_publication.py', MANIFEST)

# SITE_DEDUPLICATION_FROZEN_CONSTANTS:BEGIN
FROZEN = True
PREDECESSOR_FILES = {'.gitattributes': ('411e439fc63c1b5276df34656b5c83c4ce69871d293e0efed2aa9cb3dccd22ba', 433),
 '.github/workflows/pages.yml': ('f56bc01ffd913e0ca987923f1b96be49370d4768ad83a1a283f2dc5560542d7b',
                                 1949),
 '.github/workflows/research-ci.yml': ('5353b0fae4b0ad0f3faa2b1275b54bb8a0619e95aec95575153a11de7988e047',
                                       2599),
 '.gitignore': ('27f1674a4121b0cabca9823fcdb935fc246fbe951d0d306868aeabcaaf7ecfe7', 68),
 'NOTICE.md': ('5374e5dbeb8049a39850073f6ac2a95be948a7b53f9e62db63a7226fe76a69f6', 821),
 'README.md': ('d7772373c93e0dbb3b175aa5885f90ec3213e66708de7fb4942b221755675bf7', 9331),
 'README_zh-CN.md': ('f8b1baca5be76d565fa786a4c4b88c82bdc574c26ab8fa943566b94b796c2f36', 3111),
 'SHA256SUMS': ('60275b777259e44d7277ffae4f15f71f5f628b1ef5e57286119d8e2b348a507a', 1746),
 'audit/javascript-report.json': ('8e147d7ae75f7e07be43e9db1f8404e772ec2ac295bdd2ed812f20dc63c0d411',
                                  191),
 'audit/site-manifest.json': ('be6b104b660aa81d2cefb3a1616e85936660a1ae1a45e69b851b40763c7cffa9',
                              2488),
 'audit/validation-report.json': ('7eded9a6475d61643ecdd83def59ac62270e055339ebea3d27d5946fe4a95609',
                                  486),
 'chen_research/__init__.py': ('22426c7b141accd04a156946d124760bbbeb753bc3370cc05182f05852f629bd',
                               92),
 'chen_research/__main__.py': ('86cbce145a47cf6d7acbbc127e3e5ce0df12da6efcf7dd5d88dc4fc5780002a6',
                               966),
 'chen_research/uv_replay.py': ('67169496a4c795eaef9ca7f68f3659def4050529fde0863fec5f2ffcce8b04de',
                                9996),
 'content/a01-historical-achievements.v1.json': ('f59916dd0ab0cc5d23684c102ffeaeb6936632f13975017d367ec7242408b8bd',
                                                 27827),
 'content/a01-historical-achievements.v2.json': ('c27a28b6922358d52e7bde69c9c6f56df06ac20efe58affc0706c5a0b4b20db8',
                                                 39364),
 'content/a01-primary-reading.v1.json': ('606f50cef7528a3ed176b9b0ce02c13ee14d6bea802bdd224f243e2dd8478f8d',
                                         7828),
 'content/a02-academic-achievements.v1.json': ('173ebb010d8e8797b1d40d626c0117f1b80aea77f04c3299a63d4d0cec2fc244',
                                               54356),
 'content/a02-biography-narrative.v1.json': ('37418b8249618689d06840b2c9f3b6d73d2acff10dcfc6f5452db605b4543589',
                                             8606),
 'content/a03-biography-narrative.v1.json': ('193b5dce331269d1cc41042ab3ec9d3053d1f8911aa54d768866b921e1f64e49',
                                             5642),
 'content/a04-biography-narrative.v1.json': ('1cac319094ec5d73b9faf57afa454bf1edab78026b25b305b93e3627c26655a8',
                                             11723),
 'content/a05-biography-narrative.v1.json': ('d5cb9d73f3804dd4bc6112477eebb9b259c5b1c80cdb0e4b618b3d2c594dc832',
                                             11849),
 'content/a06-biography-narrative.v1.json': ('002acd76b0953e00fa034b7f0d840dca957c8b692f113999454f56b4ef6bc96a',
                                             18948),
 'content/a07-biography-narrative.v1.json': ('22e6121f4f3d61e3676a8ec95b76dc22512df0ab550cfb7c403f809f245016db',
                                             13279),
 'content/a08-biography-narrative.v1.json': ('e33b1834271cfdc42a36d02589c046fa2b5f34a2033ba93beb63201fe91def82',
                                             28386),
 'content/a09-biography-narrative.v1.json': ('ef84978855c9edb156e528e72fd63df75932b4ed165dee94b43fb831794aec50',
                                             15824),
 'content/achievement-display.v1.json': ('0b0368e96a8cf3d8c8a06128acedb5e53041fdfd95d3e63ed31036721c95fe07',
                                         632354),
 'content/achievement-labels.v1.json': ('b63cec91955db4431480bb9bd9d886e794bc4a5f67ec5e36352c9cee91231cf8',
                                        564),
 'content/ai-research-section.v1.json': ('d7e454c826014ae31e0b1a346e66fc193a39ffc4516a4abecbfa895e7dac90e0',
                                         106110),
 'content/chen-reagent-achievement.v1.json': ('8d13ee4ecaa36a2208867c2510531c8b0d6eb1e06abb8da52c36dc0d7265bcb1',
                                              3884),
 'content/chen-reagent-cas-source.v1.json': ('2125b9eaba7853ab02c378ca7c1d78265bbef2895bb2fa512a2cb53981de05cf',
                                             1518),
 'content/heritage-20261114.v1.json': ('ba2aac21a10ed38ed6a4d796c904fa6fb539afd7f2fa370fc91b4274fb54d135',
                                       35989),
 'content/heritage-20261114.v2.json': ('981876c28a6c863874a8bee8840477fcc04e0f117608d06a4a076b2d0d645350',
                                       72392),
 'content/nine-line-deep-reading.v1.json': ('c503ce688c79c49848bce2a715a0fbf7ef6cbc3e037d89ff0b15c6221f326f99',
                                            92024),
 'content/nine-line-reading.v1.json': ('90c97ba6c17ba426ef8ef12ababdb7b5f2639a8df443400354f3299200ec1163',
                                       16823),
 'content/reader-journey.v1.json': ('eeac9e076795f9ef70ad094c8024f95243699372c56996918298a7cdb14e2672',
                                    212038),
 'content/reader-navigation.v1.json': ('191ab3d6a24e333df277dfdaf9a4c42cc95d860fd660070f49b7806ab5dff6d4',
                                       37365),
 'content/representative-studies.v1.json': ('5f213f9a2322b6673e72477d47387de4378d3600eb87c92f6d9a7fe3d40af1a5',
                                            66015),
 'data/pftb1966_table1.csv': ('92af88d5c1307d0a01b418354d2620a0d9eb8a8c68766adedd8be0feec2ff29a',
                              515),
 'data/sources.json': ('5d898ddda4013b0361d4a33cb3cca964374fabe1f63c1b528218ac867adda0cc', 1032),
 'docs/A01_FIRST_REPORT_zh-CN.md': ('6f8666b96ee0220c05266e63bf6239ec22205fd1977ce31bb8a6f488d2750071',
                                    8566),
 'docs/A01_HISTORICAL_ACHIEVEMENTS_zh-CN.md': ('30f0d767f751088facc2811c16996f8896c64197cfef7b1e18a0e6472d185e3f',
                                               11125),
 'docs/A01_PRIMARY_READING_zh-CN.md': ('2c6c2f196ebe587f75bb29ba47264d804eddb77b349cb64eda00af71bb2fa550',
                                       6764),
 'docs/A01_PROGRESS_PUBLICATION_zh-CN.md': ('5ad48ea0bccfe1cb520228617a70718eb9dad2c316d1b970a61fb5beb8632f9a',
                                            3412),
 'docs/A01_PROGRESS_V2_PUBLICATION_zh-CN.md': ('e34ed1358162e963f34f486a53fedf1355562dcdc1af82393fb6446ec36d0330',
                                               1929),
 'docs/A02_ACADEMIC_ACHIEVEMENTS_zh-CN.md': ('c58e296391b1141f33bf6b9e8f79635323fe1000554d4083600272164a60eb21',
                                             9064),
 'docs/A03_ACADEMIC_ACHIEVEMENTS_zh-CN.md': ('c0ff6a8f7728083c8f660a221dddafc0ee35260d0cac723d392795b1c216cbd2',
                                             4984),
 'docs/A04_ACADEMIC_ACHIEVEMENTS_zh-CN.md': ('83e49fc20fbf0991e242c4449494ba198726d95efd3bf5097790df8f2f6404a0',
                                             9938),
 'docs/A05_ACADEMIC_ACHIEVEMENTS_zh-CN.md': ('1d95bf451dddcdbb5027541bf9052204281feab0b5cd8f41024cd24501f8eb47',
                                             10857),
 'docs/A06_ACADEMIC_ACHIEVEMENTS_zh-CN.md': ('1eebc0dbec9fcbe553edbea5ac70c52a685d27661b7e423c16e21e81aa45f288',
                                             14564),
 'docs/A07_ACADEMIC_ACHIEVEMENTS_zh-CN.md': ('9d73bbb199e8c6d825550429ae35cb3ea8dffbcd4b17e3b73145603080cc487b',
                                             11338),
 'docs/A08_ACADEMIC_ACHIEVEMENTS_zh-CN.md': ('c64ea7e4cfde67d25cad6c8fc1538c8167ad69cbeea38fcb473e4b3a7e3a7e37',
                                             22967),
 'docs/A09_ACADEMIC_HERITAGE_zh-CN.md': ('00bd6eb7270a31ef0a9c857fe7f35b67a57abfb6aa41e22089b281380472508a',
                                         12603),
 'docs/ACADEMIC_ACHIEVEMENTS_zh-CN.md': ('cbeb047b09402e0c70bf10c5566522a56e18cc6763642662969a237194a582df',
                                         25979),
 'docs/ACHIEVEMENT_DISPLAY_zh-CN.md': ('354b6b99a56e42a25cc4d5a5ae0aaa31d9e0aa5d246fd9059f0d9bea0b4f4dfa',
                                       2692),
 'docs/AI_RESEARCH_zh-CN.md': ('b6ab17e0db1794a9f33c370349fc84a37e36f5c50e76492577e447fc4b32d2cb',
                               63386),
 'docs/CHEN_REAGENT_ACHIEVEMENT_zh-CN.md': ('aff472de27abf8d24eede857e77ae6aa0ce9d5a3a99cf774319250e08ee9128e',
                                            2350),
 'docs/GITHUB_HANDOFF_zh-CN.md': ('d3fb79397cc32e51472c4388693d4fc9d4bd5ef95da01652099c666d282d04cc',
                                  4586),
 'docs/GITHUB_PAGES_MIGRATION_zh-CN.md': ('3900e9667c7a73bdba034e9d3d3744d29ef610066940027211103124eaf490b4',
                                          4523),
 'docs/HERITAGE_ENRICHMENT_20261114_zh-CN.md': ('5451cca7e591a98cbe4dc88330a70ad50e10c97dba1fa56720db9b8d15f179f4',
                                                69129),
 'docs/HERITAGE_INVENTORY_20261114_zh-CN.md': ('7445c5c70c873b2ee4029d543c80c11b71157f2b4de5f3f16e8c5b1ee476f898',
                                               34428),
 'docs/LOCAL_TESTS_POLICY_zh-CN.md': ('bc4d52e8fdf46641fd3dca1b71c893f331368edaa0a920965d601c4d5b8268a5',
                                      1845),
 'docs/MIGRATION_zh-CN.md': ('3e046fedc4732603791be76d804b6f186144be0ec5a7009fdfe0484b467b238c',
                             4339),
 'docs/NEXT_RESEARCH_GATES_zh-CN.md': ('d2133c6ff3f4a160bc5545c3caeed659255044db04694dd849b17db64dfae937',
                                       4629),
 'docs/NINE_LINE_DEEP_READING_zh-CN.md': ('8993a1deb2f9d88abb69aaa2fdf606349b04c025b9e63496593fc0daf944bed8',
                                          39911),
 'docs/ONLINE_ACCEPTANCE_20261111_zh-CN.md': ('7c5365aff47b1fd48c75f550c4d7b8cd92a818bb9442ab64dfaef847535bcd29',
                                              3296),
 'docs/PHASE1_ACCEPTANCE_20261111_zh-CN.md': ('361a88d344ba51463363a54665901aebf9707b784b5e58ffbdd68f70bb7d27df',
                                              5595),
 'docs/PHASE1_INTEGRATION_zh-CN.md': ('c4a9dc4cefa6150e0cfc49945e316a6c995a3d44ea0c913570ccd41f20d02d8b',
                                      4814),
 'docs/PLATFORM_PURPOSE_zh-CN.md': ('4e222f9c5eaf36189ce0bb3fc5dc925db1c00704cda526778f7c3e368ec01c4e',
                                    5056),
 'docs/PLATFORM_ROADMAP_zh-CN.md': ('24209ec12e3688f86ec4098f304d5bd58aeeb3d9ce795f9e2805de81d6812ac0',
                                    6997),
 'docs/READER_JOURNEY_zh-CN.md': ('44a51d2a9ab9f33be6589da0b6fbd15a796bbeaae27d236bdc9ac96fe591598b',
                                  4122),
 'docs/READER_NAVIGATION_zh-CN.md': ('865e617439ab9f809417499dc0172458261a14bba4289f01ae0cd8828cd14f9c',
                                     3093),
 'docs/REMOTE_INITIAL_README_20261111.md': ('5c68d727ad01304bc0300506d78ba2790e0922a234ed4143a62654dbcdb39db8',
                                            497),
 'docs/REMOTE_INTEGRATION_20261111.md': ('7afd2a9a2867b090ae16d9c366fbd68f01e7f38d5618dff7000a7039c14a3b9a',
                                         983),
 'docs/REPRESENTATIVE_STUDIES_zh-CN.md': ('c595d86c98f27763ffe64f1edc57766a2d042d3b1600a26278a9361438bc759f',
                                          48021),
 'docs/RESEARCH_ROADMAP_zh-CN.md': ('e8a219f4b971b7d5862b986a1ee0b5ab9fef86352e7d3653ac2462271e322155',
                                    9584),
 'docs/WEBSITE_RESULT_CONTRACT_zh-CN.md': ('ac8b9e82fd30907a5ec55c003b9c5daa095dccfbc5e09588e668375e12d64883',
                                           6077),
 'docs/WSL2_ACCEPTANCE_zh-CN.md': ('3fe7e720b6a358570bad1fe1bc6303d492b5827bbb3421775b425cc838e30f05',
                                   3079),
 'docs/YOUMIND_A01_HANDOFF_20261113.md': ('4e453ac361cc0b414c2e26d910d89d09d8cc6e62e72313f7198caba03918a9e0',
                                          2249),
 'docs/YOUMIND_HANDOFF_zh-CN.md': ('15ba6adf07113d74439eba7e5e7e7764117a6c70061b245dbd61f3658a1f091e',
                                   1315),
 'literature/related_work.json': ('fa746224de1c6049fe975ae9c9dd0cd9e8e6a4cc5b372fde473ddd7f127e47a6',
                                  4848),
 'literature/search_log.json': ('fa71f956c394c0234c51c1f1719062c1213279ee7e4ed387e1c6ae296910fa17',
                                1160),
 'protocols/pftb1966_uv.json': ('3439dbf5d535663672afd034c888fce4aacc3c4314657199f40b90252568735c',
                                1520),
 'protocols/research_queue.json': ('3b123b5f14a4a8ba1bc94e4e7ade3ab87982f600a94c7c635f0bfd8be6e9c9f1',
                                   2658),
 'provenance/a01-first-report-previous/README.md': ('eec96a7d0d128190c289258bf12136b161ecf6792e0d3258ff6d9cdd6fe85a46',
                                                    6362),
 'provenance/a01-first-report-previous/markers/A01_HISTORY_HOME.html': ('667ab4b3e1f6c55a71e5ed70f73fb5bafc970a01bd8c28872822b589f659610e',
                                                                        1470),
 'provenance/a01-first-report-previous/markers/A01_HISTORY_SUMMARY.html': ('aba14e754ed6872346d33d6ff51c8bba13f09d0f09dfb262a0106b6bd01c8d34',
                                                                           1488),
 'provenance/a01-first-report-previous/markers/A01_HISTORY_TOPIC.html': ('ae97221e73aca6e2e12befbcadf5817695afd6d6fc585eabda3867befa861a84',
                                                                         55031),
 'provenance/a01-first-report-previous/research/a01/README.md': ('b203799322002384f74cc7a6b5717e5146b920f945112d69783504654c1e919d',
                                                                 5924),
 'provenance/a01-first-report-previous/scripts/render_a01_history.py': ('16c207c427850512935fb41c31a3867fdde5f8c3765dcacaa0198420201465c5',
                                                                        13055),
 'provenance/a01-history-previous/README.md': ('6d0554307543965795d9bf86cc7b33501cac966493275d5206c5bef82c031d57',
                                               5458),
 'provenance/a01-history-previous/site/achievements/index.html': ('f96e38b9f01ef38fd34ce573088fb72a16fd0f1d01c05f44575db08deb84e3b4',
                                                                  94360),
 'provenance/a01-history-previous/site/index.html': ('b06eb2063b278af084f8732f5316c010070749faa77f4a908940df250e734a10',
                                                     253360),
 'provenance/a01-history-previous/site/topics/early-fluoroketones/index.html': ('3bf89b24ddf8e32bc5b4174e344103b6574d99876a4bb504c0cb8455b069495f',
                                                                                182563),
 'provenance/a01-site-revision.v1.json': ('47c875aceb4b37b17a38bfd96eca694b08f3c321b396c2d0f5da4181a72b11bd',
                                          2820),
 'provenance/a01-site-revision.v2.json': ('9d1a800ae978b4eef814aa4c0b4c99f6faa35f79b7fd4315edc1aa430a2ad845',
                                          2039),
 'provenance/platform-presentation-v1-documents/PLATFORM_PURPOSE_zh-CN.md': ('85340277bafd18a5579a48176c7f1d44eb42259e2fd2ee547a956bb1451d576a',
                                                                             4855),
 'provenance/platform-presentation-v1-documents/PLATFORM_ROADMAP_zh-CN.md': ('c9ed69f246bfa8c9ca6ce956003eea9cacc712b8e6574ce8f390a39459326970',
                                                                             5576),
 'provenance/platform-presentation-v1-documents/README.md': ('c5879296ce8be32c1275e77eaebba2138e8a0b8df55cc058d80d9a1e6644b0fa',
                                                             4326),
 'provenance/platform-presentation-v2-documents/README.md': ('c7f7737d8b7bc431843e28490bf3bcb5c2548ddb3a78c0916c95fafcffbe207b',
                                                             5234),
 'provenance/platform-presentation-v5-documents/README.md': ('8ce55233163a68f912817072feb81c7b9f313f6d6d2103a9e7157975763f35b2',
                                                             6057),
 'provenance/platform-presentation.v1.json': ('1ade23238a23977b47eaa6a7dd585509fdca3e270615914292e2341721308782',
                                              6170),
 'provenance/platform-presentation.v10.json': ('65954e3ff6b484a010fa5052f5331eab55149d23a468ae354ab236462598ffd3',
                                               6611),
 'provenance/platform-presentation.v11.json': ('d6eb2a3faed6f030a28ca5b63e3f3512144c9246f39467d300fc279a967bb004',
                                               55236),
 'provenance/platform-presentation.v12.json': ('aa9efd831558b47646b687e12be30724c4b8be89a0f98ccb8d06ef56cf04e81f',
                                               77532),
 'provenance/platform-presentation.v13.json': ('263b465d22b1a56b8364a0540a65f742948664f9e50e64d759543685768468cc',
                                               132999),
 'provenance/platform-presentation.v14.json': ('3ea28579d130b065fb805942c5c62861d8f6cd24a0027df7fef7cdc41415750b',
                                               30883),
 'provenance/platform-presentation.v15.json': ('d21bad493ae97587c7b9493813af3393ed9ed98f5a8dfd3a8790270f7ba49aff',
                                               97475),
 'provenance/platform-presentation.v16.json': ('6b975e980d176ecc481449ca5a96ffadadfecae2eb64d97dfdafb75b85b4a3c0',
                                               91465),
 'provenance/platform-presentation.v17.json': ('b635b2950e37d5387e8fb68da12109ca585833b769eec38cf25911eb86563ee1',
                                               112706),
 'provenance/platform-presentation.v18.json': ('4fa6f43360d5343e119bb7b9e51e0671f1b4b4ef51ba065067459180a710dfd6',
                                               85784),
 'provenance/platform-presentation.v19.json': ('1a056390024ec41126e36c8b8e6a5275415331ec6eeec524da9df8785e23d59b',
                                               59890),
 'provenance/platform-presentation.v2.json': ('91434b5bc8fb51e96b604a6c6437cb363c92370347f22fcbd2a825e5498f0348',
                                              8527),
 'provenance/platform-presentation.v20.json': ('34814fabc405812bccc433018f8a197d181a3da9ac617f84cceda51513774b72',
                                               68305),
 'provenance/platform-presentation.v21.json': ('a353a25fc9586c3fe78de1ad42a20aee4a1c980de59eda4340df4466d9b45593',
                                               36965),
 'provenance/platform-presentation.v22.json': ('3a9a746a565f7942899f5fdffc244121608e39210c7e6eb466203775dc38cae6',
                                               66796),
 'provenance/platform-presentation.v23.json': ('392490c9d1ddc18942ef5b139eb094155a883f1a340e56adfc9512bfa5430a3d',
                                               26078),
 'provenance/platform-presentation.v24.json': ('118a96428bf0a0fce5467fffd8861c419f97ac078aed708b6fd3b5e6318cc242',
                                               200127),
 'provenance/platform-presentation.v25.json': ('61b8e4ebc4e4800253d886a617b98c9590c370c5ae494731edc8135ebf15e9c1',
                                               25079),
 'provenance/platform-presentation.v26.json': ('0215099d811ba22ee7224e17a2603d3fdccd7dd0b7473297d35ceb419966bd2d',
                                               170716),
 'provenance/platform-presentation.v27.json': ('a49d94aae9d1ab980a17506441fdb6d8629fd29da5ae798aa3737568f0c2344b',
                                               65604),
 'provenance/platform-presentation.v28.json': ('54449b28f3dfb1c2946872f959df5e8bb1fc4a9b8e04f20b9b0f9daacd8704f3',
                                               51592),
 'provenance/platform-presentation.v29.json': ('2206e301c22181e3e1a0d5bcce619dd590b4eca3d2968faee6cfbf9a08ed29b7',
                                               61507),
 'provenance/platform-presentation.v3.json': ('2b290301102abd8cacb5a2d73f7393d8c4f851285a882a08df42eecd960ed286',
                                              1855),
 'provenance/platform-presentation.v30.json': ('952cea23bb612648addc4ac5a5e5cc88acae24a67b8dc98661ae49f79710645b',
                                               89059),
 'provenance/platform-presentation.v31.json': ('2d1195067b1ed7cc9a454329cc499a0b07cc01de0d1f8bdfa001214d9cf2c5a4',
                                               61501),
 'provenance/platform-presentation.v32.json': ('437a1f8404c35af883fc29ac3155405ede4f2e7eb41b19b128b05dbeb06ed175',
                                               106100),
 'provenance/platform-presentation.v33.json': ('410c93a4fa52415c1345a05266eb79afc80484491aee0b51c3781df3b0c143a3',
                                               288659),
 'provenance/platform-presentation.v34.json': ('a337647a017f0eaf50f96d8328fc3c865e3e52d65e32ec65d86ce3f7066ce6eb',
                                               190588),
 'provenance/platform-presentation.v35.json': ('039d727d35d35664d3a90167b0bca5395d331af1ac3118f6fed304c55f6a68bd',
                                               182264),
 'provenance/platform-presentation.v36.json': ('f590eda047067c8af498f0086e154a6f37a93a9019f8e3c98654bf4ef28dfb44',
                                               547827),
 'provenance/platform-presentation.v37.json': ('69f22515280972d541ac7f3b8e697bdebdbc8dc27076c1658575e04ffd12059a',
                                               294080),
 'provenance/platform-presentation.v38.json': ('c5b25c4c85d30b87117b5863f3fa29b46e78bcd3d575a1d7b3b0583e8d68bcbb',
                                               374653),
 'provenance/platform-presentation.v39.json': ('e374e87c8bcb845d3f197f6da8de8d1d4e1cd06a7b969d131e3f5fbe99af3914',
                                               858362),
 'provenance/platform-presentation.v4.json': ('cfc0bc4d29c24a846bb76ceaf3246084d406393cc7d04ec105cad539c21e120b',
                                              8888),
 'provenance/platform-presentation.v40.json': ('3a8c97acc37fca6bc5c87ca8b80fdd23cbeb65410626466210b69f434f587ff4',
                                               126199),
 'provenance/platform-presentation.v41.json': ('2e5fd988bbdf86395d297bb4288eeb7736ea64ccae12d2e94d642c855f801213',
                                               126544),
 'provenance/platform-presentation.v42.json': ('9e93d177235c512cfe9bf442a62ab2edc4537ba0d74813abfdf864bcb05a23c2',
                                               131297),
 'provenance/platform-presentation.v43.json': ('ff8ef31a87ff384de97e30bfa74b6d7450e160cc2902fb81ab4af9cf976e6a8f',
                                               134350),
 'provenance/platform-presentation.v44.json': ('b595f0e9f736ee697ec4cb153d9f901d7346585eeae886996b4200241c5667dd',
                                               131697),
 'provenance/platform-presentation.v45.json': ('466d677143158d025b67d07af2869dd2ca2966d65d006ad53ab05da6df92e68e',
                                               188716),
 'provenance/platform-presentation.v5.json': ('7ac60223b0e540de62671017728acd54e66d07e8de2721006c476c8d1734bed9',
                                              9746),
 'provenance/platform-presentation.v6.json': ('1077f6b2e3a78be65ea4b50e81907b629f96c9b3599fcf440493c204b33dbcf3',
                                              9721),
 'provenance/platform-presentation.v7.json': ('2463a97b3bf74b629f1863892d75f36276c97bf9a111905b47cc6179b62eaa7f',
                                              3758),
 'provenance/platform-presentation.v8.json': ('ab2b362cb5c90dc4b782f8989cc127a31944c49998ee45fbded8b8a7ac77c962',
                                              13535),
 'provenance/platform-presentation.v9.json': ('462fdbfe1c4bd6f0c32f39e2597764037b4562904f0acec4cce00f08c9797017',
                                              5918),
 'provenance/public-presentation-previous/README.md': ('30548c6e966604028863beb58c39ae849c95c546d0bc047dc2d3dd4f0bd8dd3d',
                                                       6971),
 'provenance/public-presentation-previous/site/achievements/index.html': ('26efdd912492b9ef0055e2ba60589db4d373f5857398671e3d2d47e51fb23949',
                                                                          94418),
 'provenance/public-presentation-previous/site/index.html': ('2b9e4a22edb1a7d1c5bfe59af226a4815310354542dbf089f28f5d1b220613a5',
                                                             254164),
 'provenance/public-presentation-previous/site/pftb/index.html': ('0d4396b85f8cfd772edcf8fe9bc192d845268399e1ed3834e1d83562639ba372',
                                                                  97584),
 'provenance/public-presentation-previous/site/topics/chen-reagent/index.html': ('e5ef73695a890465fedf03da7a4d39984aae30a902da7e4e7d6eaf0600ef0149',
                                                                                 19830),
 'provenance/public-presentation-previous/site/topics/deoxyfluorination/index.html': ('6a448d3a052040e83fb2bb8b9497a75ed22151aee4c50d5456755c1320b63fb8',
                                                                                      5476),
 'provenance/public-presentation-previous/site/topics/early-fluoroketones/index.html': ('f40e31b9be7439c502854ad2b75ae6cf26d2d894e36cbb68b6d5d29aef0c0d11',
                                                                                        182585),
 'provenance/public-presentation-previous/site/topics/f53/index.html': ('a6349eb302e88d3176b086f83e9f1b62c008e8616f5f034365a4274756addeab',
                                                                        8111),
 'provenance/public-presentation-previous/site/topics/fluorinated-small-rings/index.html': ('abe1d15c5aedfe81531fc6b178b5e2ee98d1a598325ef2ffeeb3cff4b496f2f3',
                                                                                            5858),
 'provenance/public-presentation-previous/site/topics/fluoromonomers/index.html': ('baaf7d82224cea22e9da1205e193c24ab6c44b97f0e93da2748224251d4ce836',
                                                                                   10457),
 'provenance/public-presentation-previous/site/topics/fluoroporphyrins/index.html': ('4e5d37c031fc49224d5147a83a1a665119f2cbb4ac1456613f7411c7568364d3',
                                                                                     5944),
 'provenance/public-presentation-previous/site/topics/index.html': ('cfda9c0892c48082f8ec945d2b65bf46fdf419f2907653cfd91454e3c7fa09e0',
                                                                    4970),
 'provenance/public-presentation-previous/site/topics/perfluorosulfonates/index.html': ('e660092c3fcf6458092179e94144b0d21306a02303b2eb306b6fdcf02cc7f5f3',
                                                                                        8765),
 'provenance/public-presentation-previous/site/topics/refrigerants/index.html': ('1e032070347a39624fa6639d1bd3e7265709436922a12f358fbe497f1cc9abae',
                                                                                 10567),
 'provenance/public-presentation-previous/site/topics/single-electron-transfer/index.html': ('c3b6c7aa0124d50510abe7303f64e70e36dc6abd36788164c52d91f719538c01',
                                                                                             10271),
 'provenance/public-presentation-previous/site/topics/sulfonyl-fluoride/index.html': ('d091dc39d740c10a0fb65a85367b34ebe1a1a2fcb749905ea5cbb987778d40df',
                                                                                      4969),
 'provenance/website-baseline.json': ('5e3e70988d76ac1d777ff85ee7c1945341e2141767fc77560c6cea39eabab329',
                                      4464),
 'research/a01/KEY_PASSAGES_zh-CN.md': ('c4bb706737ed8ff000a0d0368e918c125b15f2f7d3cda4428999dcdd9ff5e1b7',
                                        1750),
 'research/a01/PRIMARY_READING_20261111_zh-CN.md': ('3006222f600c9f7c0cc09f4c7b5564870748210a707eeff3fb9b4d4c906699bd',
                                                    4693),
 'research/a01/PUBLIC_PROGRESS_INTERFACE_zh-CN.md': ('8255096e41d5e64ac9a6655cae960b7c080d896fed1c2f60def5b6b698d94d84',
                                                     4487),
 'research/a01/PUBLIC_PROGRESS_V2_INTERFACE_zh-CN.md': ('d5267399ae8f13cd4ef045e827406c9b279fe9afbe84e5ab5ef93366d1008031',
                                                        4823),
 'research/a01/README.md': ('2b868919fd404f0d7ab453bd48da9360509508b75bc5fc156cd62b822b79af66',
                            6227),
 'research/a01/STAGE_HISTORY_20261113_zh-CN.md': ('869642dde155b8f9176d583ca95ec69d5e0aff74848d0fcc4e650eeb0124bbe7',
                                                  3312),
 'research/a01/bisphenol-af-yield/README.md': ('17b4b7e2e2abc935dd893a3a5cf92b03ca2451fb2ad1ba5ec2fdce9fcf4e649d',
                                               3186),
 'research/a01/bisphenol-af-yield/observations.json': ('60d9c26ccf41448d908620600415a2ee7ad750c0cacf6b9ad788692f9d41d1e2',
                                                       1039),
 'research/a01/bisphenol-af-yield/protocol.json': ('0d1a9e3840f4bab9d9f7cf3e012519721d776156f4120b0acb198c62d1abc8ec',
                                                   2073),
 'research/a01/bisphenol-af-yield/replay.py': ('76658a5d5b541605ebc654f0068435a7cbf449cd590f0b4728e89e6eb0567054',
                                               7992),
 'research/a01/bisphenol-af-yield/result.json': ('8a8a40ee16679293655d36a197d8aab3afd67dda97a018abe253331f4dc78a7e',
                                                 3065),
 'research/a01/branches.v2.json': ('304def1cdfda303666337db8aea0e99b771b5ddaf5c83664600d993ad9adce9b',
                                   3439),
 'research/a01/molar-refraction/README.md': ('14d183ad1ebfb7c6ad2aa888c8cd6ce9b2cf270e6136dfd97437d208f26c13cb',
                                             2049),
 'research/a01/molar-refraction/observations.csv': ('5fb8b1ec1965ff86930b498454dbd9c38180c8a379805d17dd0187ce9f78da72',
                                                    1012),
 'research/a01/molar-refraction/protocol.json': ('606ac349e00f8a45741510310683b0a1f03443ac3b7cd01f1005d728efeb812d',
                                                 2683),
 'research/a01/molar-refraction/replay.py': ('a14ad2220e0c5b6fc73ca44104d6956a90f0af7b664d5c3f914bd3a71f069b72',
                                             7210),
 'research/a01/molar-refraction/result.json': ('e93eaeeb2596130f6c7504ea76c3f2770fa2d6635f8ff3733b3dac3a85c9aba5',
                                               14461),
 'research/a01/oxazolone-model/A01-P134-IV-CF3.sdf': ('c0653abe6f6f29ddeee4af9ac19682f5939cdf231544b99f3fc2e3486b490731',
                                                      2426),
 'research/a01/oxazolone-model/A01-P134-IV-CH3.sdf': ('26f8026e2c93cb3f4ba7b0236f9815b0738d2c569662a4913da99765b6486da4',
                                                      2426),
 'research/a01/oxazolone-model/README.md': ('314a47b99280dfcb435b698e4da11d791f58a4e7ce84b305c0c0fe925ee0282d',
                                            3438),
 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/PROTOCOL_zh-CN.md': ('0ec906edcc68e058d011a1155dccbd75f43b3e8024b72c6e3177add8dab35011',
                                                                                        3389),
 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/PUBLIC_FILES.v1.json': ('1fd4eb34c2fb288911638cf68da2deb0102ae8a022a39c13a945bf8e103af1d4',
                                                                                           13056),
 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/REPORT_zh-CN.md': ('87230c18ee350108357df3083e4bda03ee1cf228bc9636528c70560af235cfe9',
                                                                                      4529),
 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/archive_results.py': ('bfb235e1bfe4eef1fcc580ff28958c49948a2675c2a4cf574c77e2f070198df0',
                                                                                         19969),
 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/audit_checkpoint.py': ('7ae8569de082aad465c2ca95966e8c2609fd39b451145ecd85355beccdfa5973',
                                                                                          4650),
 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/center-comparison.v1.json': ('27677ddbd9b93d48c51dbf8a7905b9d20a4a22d5683edae7440b19a776b257e7',
                                                                                                2461),
 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/contract.v1.json': ('f57a7fe8ac237c4cf32c203a20ba324d0b3cf94cd020b0f7d9f901bc06802e81',
                                                                                       6778),
 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/controller.py': ('e1fafbc631e68d56a5b9f7083702aab0ac5ca1b9255e066e29f09d720e46bdec',
                                                                                    9405),
 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/entry-verification.v1.json': ('decacbf784deb0d440c9af39fc006419077549c179c869ae03f79218d0ef418f',
                                                                                                 2268),
 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/evidence-index.v1.json': ('d539b87a77db9b21b81fbb544995867dc4df86404cc19c73dd0e169bd2c87128',
                                                                                             5422),
 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/independent-checkpoint-review.v1.json': ('52f9a2cecd0e8088fbfc3a4fd3614d88fd9b8287c0420414c724609f3f89dce9',
                                                                                                            2047),
 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/input.v1.json': ('ba4c38c8421124c9e3d93efc742bff48c9c7ec655a5af6e751b6b56e1a35711e',
                                                                                    3944),
 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/launch-manifest.v1.json': ('95d2f9951934870a4eb419ae601eb12d34b2ac1f888e615ec55b74d4c3786159',
                                                                                              1489),
 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/native-exit-observation.v1.json': ('c6197433fd3bc83b38c6e46a7e93f8abe07a85a005495fbabf8269eef8e322f1',
                                                                                                      312),
 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/prelaunch-state.v1.json': ('6a98a990b04ef547acf9636f40bf9314cceae14b8c1b5b32d137544d5e897831',
                                                                                              456),
 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/preparation.v1.json': ('7e6eadad3cdab259d93e1c852f8e45e9e14aee70113f25665bb4465c786a040d',
                                                                                          362),
 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/prepare_scf_only.py': ('90e8debb254abe6335c342aaef325b626cff53cbe284c34ef9a10ba2e29cfe46',
                                                                                          11119),
 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/public-evidence/budget.v1.json': ('b6041a0961a069466a880196cde3c6563f7f62be21de1d693b50a0974a470cea',
                                                                                                     1118),
 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/public-evidence/center-result.v1.json': ('74dbe97903adba0db8aeccd0f711f3d14b3d11dfde394dde85f2e597fa30508e',
                                                                                                            1266),
 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/public-evidence/checkpoint-validation.v1.json': ('aa41eda439d5aef76d3e285f6fdb9435dcb027d0df0648d3749b70cfcebc2f22',
                                                                                                                    436),
 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/public-evidence/controller-result.v1.json': ('7c04f4742915032c063cf317fa45c4b5cd769440adb7932ad4a9761d32bbbe06',
                                                                                                                16176),
 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/public-evidence/electronic-history.v1.jsonl': ('f5a2911080cae524228b507460eef947ec39e0ceb6dc3b5d3a0fca369d84593f',
                                                                                                                  4536),
 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/public-evidence/final-scf-diagnostics.v1.json': ('cb72826d70441c128def22ad6d02f15ed24a875d485b3c600b0df920a2acbe29',
                                                                                                                    449),
 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/public-evidence/input.xyz': ('4202cdd0a6a3036ae7e1da0a646c5f0414f07a822440eb33ca944c26723adc88',
                                                                                                1409),
 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/public-evidence/point/result.json': ('1cd73bb41d7cea4c0704a0a93f1bca0bab4076dc8d41201fff710ad8a5ea0c4e',
                                                                                                        11996),
 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/public-evidence/process-result.v1.json': ('3e774adff2b93bc523119ea83eb56e4ec5096496bc711d1acdd8ab386f5eb949',
                                                                                                             467),
 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/public-evidence/pyscf.log': ('a48a332e2ff0bf70c88f00097810b3e3684e3c5d1db8b40176ed525fc9f793c2',
                                                                                                7591),
 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/public-evidence/requested-spec.v1.json': ('d4ee91aae2bb7014c84fc6636d07fd2f17efc32aa339fccb582c228a3119159a',
                                                                                                             927),
 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/public-evidence/source-map.v1.json': ('6edab0f10eefabefb971a374240b58d7fcac0b411fe0045d60331c6c4886a45b',
                                                                                                         3215),
 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/public-summary.v1.json': ('3de9e61cd9e05ab7764b14cbefb03251c28951bc8d9e645739ae53e438202803',
                                                                                             4823),
 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/research-record.v1.json': ('827f74c6c1f398e8a4f0745d0ecd9ffeb0ef42faaf2329256985bb32522b6c80',
                                                                                              14195),
 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/review-bundle-manifest.v1.json': ('e63d3321044347de6329cfff8cf984c466a3c488551ad572ba1aca09c9927377',
                                                                                                     13664),
 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/run_once_and_review.py': ('5e81e9ec54772c700059daf33b359f95732e5374eb2b3b41ee8974fbff7fdb1b',
                                                                                             1740),
 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/worker-from-prior.diff': ('843d53062fc731d0fc2ceca5e20d80436877b2fff7235fd3f326e2422762456f',
                                                                                             14087),
 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/worker_scf.py': ('83512006f1a6f0c3e5652ec1cfc55043e83407e4bd459c6a2087c31ed6a84423',
                                                                                    23131),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/PROTOCOL_zh-CN.md': ('2034edda3a1ce4b9bf9273bcdc0b4b03d4f7e16bd8f3c2580fd4afc333152773',
                                                                                             6453),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/PUBLIC_FILES.v1.json': ('24d6aceb513e99efd40ce1ed629deb1ef2008fe840a97e5a92972255984477d6',
                                                                                                37825),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/analyze_diagnosis.py': ('c59e454492e2600a6d4bfdee44efbefe5fe768e79753b418723493a500b1dfdf',
                                                                                                32036),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/contract.v1.json': ('c04697a81952d87fa7bacc2e3b07b59126650043556447a39625ec2ffa5e2a38',
                                                                                            2643),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/controller.py': ('1e192cd378d5913f05d8c8e69de70dc6561ceeeaa022bb9beb9e1bc00bbfe84f',
                                                                                         15668),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/evidence-index.v1.json': ('e88e5c2d41cd167c889944562a7ec40f4119d3301c15ed61a239f6fc2b109e88',
                                                                                                  45397),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/inputs.v1.json': ('9a8e783d56ab1602754f8c08372b9be648b7e363535f46fd41fc93e7f47a479a',
                                                                                          45646),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/launch-manifest.v1.json': ('d4fa69e0a34d69e77c94dc0356951be0fa146844c1a25526f0cf5afcfd96dc02',
                                                                                                   1349),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/baseline-light/old-A/C10-y-minus.result.json': ('20ac416628b0b768d3628e744af1e4380fe0061782dd1d86f2127216d44a7fed',
                                                                                                                                        13127),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/baseline-light/old-A/C10-y-plus.result.json': ('29eaddf6d3dff9a13552dc76749e326c7ceb08c6149ee8d61aa9210d2993d7e7',
                                                                                                                                       13118),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/baseline-light/old-A/C6-y-minus.result.json': ('9e6404daddabf58191fdcacf0486ce60b2bd84021d3ccae70e291fedcaadf43f',
                                                                                                                                       13110),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/baseline-light/old-A/C6-y-plus.result.json': ('a9b57d2a3c9a12308110b4eff2ce28747fb2eccf38041495350eab61ded506c2',
                                                                                                                                      13109),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/baseline-light/old-A/center.result.json': ('a95fda9ad8dcc8d91d4924429de9cd5a5ccfd0521e716bb1f75a08045a2823fb',
                                                                                                                                   13125),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/baseline-light/old-v3/C10-y-minus.result.json': ('5d47873a95485c430571e65be65a3ef6e7cdbe1c6d2a0708c1a9b1d34bb6474a',
                                                                                                                                         6565),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/baseline-light/old-v3/C10-y-plus.result.json': ('129090305857ffa6a2dfb2169a1817ca7a78323aa464a44d2b4baebfdfe0a569',
                                                                                                                                        6564),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/baseline-light/old-v3/C6-y-minus.result.json': ('05fd229cf851a11d92111b4fcc4daacf014fe9eaded9a29fcd837200b3f9b688',
                                                                                                                                        6565),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/baseline-light/old-v3/C6-y-plus.result.json': ('c19b9799582876491eda18390c0faf6963ef16cdf4420a91368c633fcc2b92e3',
                                                                                                                                       6551),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/baseline-light/old-v3/center.result.json': ('76b54b6d021f132f34e527dbfefdee54d4015990eacf34d54281a558a2f37360',
                                                                                                                                    6557),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/campaign-status.json': ('21692da37307aeee9cdfbe0f41db98d2f93c942739f20ddc2183a2ba9d769024',
                                                                                                                16021),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/controller-result.json': ('21692da37307aeee9cdfbe0f41db98d2f93c942739f20ddc2183a2ba9d769024',
                                                                                                                  16021),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/native-launch-result.json': ('622912cf2de67a383a41b7e17ab3364823fd5f3d10e4c7cf90fb8a926b8751e8',
                                                                                                                     355),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C10-y-minus/checkpoint-validation.json': ('615dc46b1b5c3b2f2f2f7757253e8f11b571977b5ce44c033b884ca6ae33e631',
                                                                                                                                         436),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C10-y-minus/electronic-history.jsonl': ('2d58069797640ab469a4a0fcba6d05d262145670598fd351882f709c66470117',
                                                                                                                                       10886),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C10-y-minus/electronic-result.json': ('a5568df7af38d99fc7319f6bbd8c93bbf990b94823bdd87f9ed3bdd48dc30ef3',
                                                                                                                                     11798),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C10-y-minus/final-scf-diagnostics.json': ('5a81759e03b92d5ce65897d3e78d77e9a6914af2ebda1f00b6cb33f1defb89c6',
                                                                                                                                         450),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C10-y-minus/input.xyz': ('41b0ddaeef123f1f743da43db36fe0232e292da66d469087ffbf86fa39809e30',
                                                                                                                        1409),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C10-y-minus/pyscf.log': ('675fcdafcd37c15f39098ba9c5aa99033cf8bb775a9fb97ca8822dbe23464705',
                                                                                                                        16816),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C10-y-minus/requested-spec.json': ('10e213df91fd60b05dac885f15bfdcb9bac6c20e3060d6c5d281f444f6519997',
                                                                                                                                  943),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C10-y-minus/result.json': ('a867abb6a299ba28e2f97f704a9bb3faf27f15eb60d2180bb8f8e301340d4e94',
                                                                                                                          15311),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C10-y-minus/status.json': ('a867abb6a299ba28e2f97f704a9bb3faf27f15eb60d2180bb8f8e301340d4e94',
                                                                                                                          15311),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C10-y-plus/checkpoint-validation.json': ('615dc46b1b5c3b2f2f2f7757253e8f11b571977b5ce44c033b884ca6ae33e631',
                                                                                                                                        436),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C10-y-plus/electronic-history.jsonl': ('4ec0f7c85c0e09835e7e5f93e8e12fbbb007494d12f00ee707fb572225a7549d',
                                                                                                                                      11076),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C10-y-plus/electronic-result.json': ('e4dbeb9981e66706f1a2956e3f73dde34afde919fbda2dbfa82753753e8fd117',
                                                                                                                                    11791),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C10-y-plus/final-scf-diagnostics.json': ('edad86c6774a7aade78d645f21dc0d77984c9ffbdd2d3412f418e78bd6ab1c80',
                                                                                                                                        448),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C10-y-plus/input.xyz': ('0000ca08076b4527725f58205d4729287808492bb7a832798886abee73ccb982',
                                                                                                                       1409),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C10-y-plus/pyscf.log': ('5325b13c12d9e066e01e4a8439ce19250c7b17e4515778b60c9599e4aea35a3b',
                                                                                                                       17031),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C10-y-plus/requested-spec.json': ('f07075c9db3889a9edb9f966744dd34abd3917d77b9cd5d6c2b7d3a5976bb93b',
                                                                                                                                 942),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C10-y-plus/result.json': ('540904123ee6d4e4ed0f99552a5965622f3709e18a01a12ac16e8bbeb242785e',
                                                                                                                         15301),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C10-y-plus/status.json': ('540904123ee6d4e4ed0f99552a5965622f3709e18a01a12ac16e8bbeb242785e',
                                                                                                                         15301),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C6-y-minus/checkpoint-validation.json': ('615dc46b1b5c3b2f2f2f7757253e8f11b571977b5ce44c033b884ca6ae33e631',
                                                                                                                                        436),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C6-y-minus/electronic-history.jsonl': ('fe19cf4f3089e54a9d356bc50cb5f335d02da5f8aabb4faef2c18de1b3d41979',
                                                                                                                                      8697),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C6-y-minus/electronic-result.json': ('3502de8a6869a5cded76ca5c41317744f6c8ac0e52ab729b79ad1f3f48028a1b',
                                                                                                                                    11788),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C6-y-minus/final-scf-diagnostics.json': ('a7fce2064d51e599ea7d04b3c0daf155bbe2f855b0864e613fa820e377f86d93',
                                                                                                                                        447),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C6-y-minus/input.xyz': ('d6df2804d8dd515dbb3642fbcebc56bb04b668effb7381e3dde0c31578c51ccb',
                                                                                                                       1409),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C6-y-minus/pyscf.log': ('750b4066752e89f9511f549bfd2e27700f960c77778ecda0faa2a35b7f7952fb',
                                                                                                                       14291),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C6-y-minus/requested-spec.json': ('42cb24789dd6a22b6d77a7ce1fbbaeb249f2985d7fff60a7892e1b5202188463',
                                                                                                                                 942),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C6-y-minus/result.json': ('f6e18f681eea3ca2ad6fa61f4f7f061aae3daf3675a08c93bd68b7f7cab684b3',
                                                                                                                         15304),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C6-y-minus/status.json': ('f6e18f681eea3ca2ad6fa61f4f7f061aae3daf3675a08c93bd68b7f7cab684b3',
                                                                                                                         15304),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C6-y-plus/checkpoint-validation.json': ('615dc46b1b5c3b2f2f2f7757253e8f11b571977b5ce44c033b884ca6ae33e631',
                                                                                                                                       436),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C6-y-plus/electronic-history.jsonl': ('f35511531b2371d0e097a4f03f2845881f142dca30b43c9417cc24a352d9a63a',
                                                                                                                                     10692),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C6-y-plus/electronic-result.json': ('212b5bfa58fe62d1c25720c2c67d4c21108f99031cbdf224155127fc48482660',
                                                                                                                                   11765),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C6-y-plus/final-scf-diagnostics.json': ('a99940c74f485dc4362e7bc1a1491de8a86833cab03cfe8682c4fd86c91fc77c',
                                                                                                                                       431),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C6-y-plus/input.xyz': ('5957bc1df57bca7914c47e58190666db27802147e69f58451ade1be36173a498',
                                                                                                                      1409),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C6-y-plus/pyscf.log': ('442001a471f02591ffc5038f1b33fa4e5e4a3714d21ee94afcab3278b7ab8b3a',
                                                                                                                      16514),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C6-y-plus/requested-spec.json': ('28953bb421bcf4122ac4b992bfef53f44b170f4b42465a7ad4c966d9821ff6f6',
                                                                                                                                941),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C6-y-plus/result.json': ('93a3782c4d3dbbca56cf253b321c5239079484155dd9b41a38d37f9e0fa5d650',
                                                                                                                        15274),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/C6-y-plus/status.json': ('93a3782c4d3dbbca56cf253b321c5239079484155dd9b41a38d37f9e0fa5d650',
                                                                                                                        15274),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/center/checkpoint-validation.json': ('aa41eda439d5aef76d3e285f6fdb9435dcb027d0df0648d3749b70cfcebc2f22',
                                                                                                                                    436),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/center/electronic-history.jsonl': ('58354023a751a6c86756ce04fd579cc478e0e14415a12884658aa15032afe11a',
                                                                                                                                  1768),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/center/electronic-result.json': ('772dffd63a80b20a4e5f25f9ac7219ddbd50e12ba1c72cd8e41af6d16dcd82af',
                                                                                                                                11788),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/center/final-scf-diagnostics.json': ('e3530f9dbf1f525b7e648726c36cd2e994b9af701a7179fc93108c4cefb42961',
                                                                                                                                    450),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/center/input.xyz': ('4202cdd0a6a3036ae7e1da0a646c5f0414f07a822440eb33ca944c26723adc88',
                                                                                                                   1409),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/center/pyscf.log': ('8fbbbda33b32188d4b8f2814250f63da4dc76882ba0b1fb8a7e312de3f0e9165',
                                                                                                                   6200),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/center/requested-spec.json': ('610139143c7a4c73eecb6f8eb119bb1759ff64f40572b00d99837ec6c3220eb7',
                                                                                                                             938),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/center/result.json': ('c5daa979f36751653e09bce416a69781f0f90148ee4a50e1a11973801249b0c6',
                                                                                                                     15346),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/points/center/status.json': ('c5daa979f36751653e09bce416a69781f0f90148ee4a50e1a11973801249b0c6',
                                                                                                                     15346),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/processes/C10-y-minus.json': ('6ea8bae4c68fbb91c3b0a75bcbe45a215fdcaee3f5d11b2563417dc5f5892a0c',
                                                                                                                      1140),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/processes/C10-y-minus.stderr.log': ('d89f959b6627955ae558c63afb6b315077a7ab742fe04a88af531be04f972769',
                                                                                                                            93),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/processes/C10-y-minus.stdout.log': ('3a0f7eec880207fc386153339304ec19e1a1082e366c3d0c9d614f3057782cb5',
                                                                                                                            62609),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/processes/C10-y-plus.json': ('9a43f3e424e56b1a5b30c14188ee2f52ca1e6b46fade3558b5ded3e8f8ced1ff',
                                                                                                                     1136),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/processes/C10-y-plus.stderr.log': ('d89f959b6627955ae558c63afb6b315077a7ab742fe04a88af531be04f972769',
                                                                                                                           93),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/processes/C10-y-plus.stdout.log': ('39219dd17065d21f7c53c0e39f37e0f10a640358fb6cb1a0cb40ab30d82c2a10',
                                                                                                                           62606),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/processes/C6-y-minus.json': ('629bde01b28d2f5c8916986b55adc85f12ec7feff390cfc277470c00999231a2',
                                                                                                                     1134),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/processes/C6-y-minus.stderr.log': ('d89f959b6627955ae558c63afb6b315077a7ab742fe04a88af531be04f972769',
                                                                                                                           93),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/processes/C6-y-minus.stdout.log': ('489b054774f9364de215018fd75fd70337e7344432e1fb17f423711b08f59fec',
                                                                                                                           62607),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/processes/C6-y-plus.json': ('400edfa72072d9ccd448fa9f4302e573c8e7415d804f945588c9dc2715054620',
                                                                                                                    1130),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/processes/C6-y-plus.stderr.log': ('d89f959b6627955ae558c63afb6b315077a7ab742fe04a88af531be04f972769',
                                                                                                                          93),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/processes/C6-y-plus.stdout.log': ('00e1a6d6e0e86d9121726d9a78daf80518b2ef18e58f709e71164f320cba3a58',
                                                                                                                          62605),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/processes/center.json': ('e719be9ee5ecbd04b65cdb9180b7d2b331fc44fbba6ca09e450997f6ad103b33',
                                                                                                                 1115),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/processes/center.stderr.log': ('d89f959b6627955ae558c63afb6b315077a7ab742fe04a88af531be04f972769',
                                                                                                                       93),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/processes/center.stdout.log': ('cdd8d59e7dd9105ac676f865ee65131a2f1dc1ae03d312a0575e6a975ad33157',
                                                                                                                       62599),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/shared-budget.json': ('2c6b81cc50740fda4ef7c58b01bbcc8b8422c448d8990ec865c50bcd94efd3ce',
                                                                                                              7730),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/source-map.v1.json': ('10de9626a028ecf41443fc954717f44230975071f0a8946366413b6ef67a8b65',
                                                                                                              41225),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/specs/C10-y-minus.json': ('10e213df91fd60b05dac885f15bfdcb9bac6c20e3060d6c5d281f444f6519997',
                                                                                                                  943),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/specs/C10-y-plus.json': ('f07075c9db3889a9edb9f966744dd34abd3917d77b9cd5d6c2b7d3a5976bb93b',
                                                                                                                 942),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/specs/C6-y-minus.json': ('42cb24789dd6a22b6d77a7ce1fbbaeb249f2985d7fff60a7892e1b5202188463',
                                                                                                                 942),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/specs/C6-y-plus.json': ('28953bb421bcf4122ac4b992bfef53f44b170f4b42465a7ad4c966d9821ff6f6',
                                                                                                                941),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-evidence/specs/center.json': ('610139143c7a4c73eecb6f8eb119bb1759ff64f40572b00d99837ec6c3220eb7',
                                                                                                             938),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/public-summary.v1.json': ('15d14c6cbbc15f824d4181dd6984c7c4047d85cfa44625ff0a376f9296903613',
                                                                                                  52959),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/results-v1/RESULTS_zh-CN.md': ('3935ea4c00fdba1e4132801bf2cade8d42e382be6047f599229fe5b42a1496c7',
                                                                                                       2265),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/results-v1/summary.json': ('8174834bed05f474a9718964130600f2c32b347e56412e494be20fffc9f391ce',
                                                                                                   187886),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/review-bundle-manifest.v1.json': ('d86b088b0381193da7f606c401151e75396db4370339e1d26919a72fc09c9f4d',
                                                                                                          937),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/run_once.py': ('a249efea79a24b664a4feb7039f5074f846e48a4c0b1e39cbd7b59540bd7a53d',
                                                                                       1744),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/saved-data-audit.v1.json': ('12701ccd4d98de131bdce78a7da67da179525053146c85830cf7a14c9265ffe5',
                                                                                                    9655),
 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/worker_points.py': ('69d64c5a4981213dd598285ea3973ed0f32d3fae6bfb294e48fdfa0c23924bd9',
                                                                                            26564),
 'research/a01/oxazolone-model/matched-pair.svg': ('8c7d7608c27dbfa933d264a959170c80acc5819ff29d94996618fdf3a01a6058',
                                                   32402),
 'research/a01/oxazolone-model/prepare_inputs.py': ('a3e35fb4dccae0883fe12406b8bacadb20609f839eb9dd53365838ab2253cc67',
                                                    3776),
 'research/a01/oxazolone-model/protocol-draft.json': ('d3a65526a263ff3520f1cfd2f7b54c5473d162f61234cbe0b20373ef272058f9',
                                                      4428),
 'research/a01/oxazolone-model/structures.json': ('22febde3f99fbc43e6edde4bdea69fa927e00af52f50c1e09514cb119c1de0af',
                                                  2148),
 'research/a01/primary-extracts.v2.json': ('d56249ed89188c9e0ce6158e2099dc84d420a68ec874d7032265596e3e09bf2d',
                                           3893),
 'research/a01/public-progress-contract.v1.json': ('cd7794cfe464e9866bfe5dfc6f8677cbcef787653ede4ff6819a42d439e736a1',
                                                   2211),
 'research/a01/public-progress-contract.v2.json': ('11a680d97316cbeb33fd0a4118cbbf6d5012310d7469815d35ec97c82489d680',
                                                   3040),
 'research/a01/public-progress.current.json': ('590b0df398766c8d5908d8cf9da775f71c6412e9364465b0b8b5fd34cd610f10',
                                               559),
 'research/a01/public-progress.v1.json': ('eca8d0ae472c3e49c99d7f8f03cb3e317bc860e5ec29ab95de65c7276f1cd7dd',
                                          19293),
 'research/a01/public-progress.v2.json': ('0168bad2419df9a16c18fa832116afa3722a783f0186f933c7e7d5b1f6eb7823',
                                          122382),
 'research/a01/sources.v1.json': ('d01629b0b15cd1e373230f84e97304f2da63ccb1146b476fd91b2b3c65cda8ba',
                                  4467),
 'research/a01/sources.v2.json': ('0b72a4a6c0cb201eee4c2ea94a9dc188ab377f63fd4690d81c9967ee8a5c5705',
                                  6011),
 'research/a01/stage-history.v1.json': ('97d0f907c1d989f15750d35bd009de1cb0885f480428bdfb4ba5e70382d08e41',
                                        5451),
 'research/a01/study.v1.json': ('1f12a0d7f9c3a298a241bfb0f72ad7c356dc41bb4bef2bdd1aceec3aa3bd5cad',
                                3769),
 'research/a01/study.v2.json': ('49e3b1f2470272129522a785cbc6f00c27e60bd3b1a7dd5cad55223dc81fc5c3',
                                2119),
 'results/REPLAY_REPORT_zh-CN.md': ('062aca44324f015450198a4bcc2ddba6aa98d896c31dbc81de407991d78b800b',
                                    2976),
 'results/environment.json': ('8cd6f137ee0bec64191d182f7492e9edd49c83d91fbd3e33b1ea134644776116',
                              460),
 'results/pftb1966-uv-replay.json': ('c83794634136e2bd08d09b806b400eea603cf1c27c753ca3db2951b9c2c99432',
                                     7691),
 'results/website-candidate.json': ('cd0ac49d0624cd5a8310c3d3bcadf7992fc677ec4d5e5a6644c0467d9a8f4ee1',
                                    3813),
 'scripts/a01_primary_publication.py': ('eb8a9163af1d6bf9ef6d8360b985c1e658fe899f78a0fc6447c84dfa2ff9387a',
                                        21159),
 'scripts/a01_progress_v2.py': ('0fcd0fcf11bdccc6b67353a8b6b96aec630cc7a98d46e7296a385083314ac2f7',
                                37475),
 'scripts/a01_publication_contract.py': ('5c7f6519ec0c5f5649bb4736430d97cc395f1c91a2dca8a57bf11b23f04751a1',
                                         320779),
 'scripts/a02_biography_publication.py': ('5e8e3dec005b381f1ac8991b5aa0e3e769c02afaa7530c6c8c3a381c5eee7a69',
                                          23974),
 'scripts/a03_biography_publication.py': ('4571904182c1ff73b8576f144a0bd1e1fbcd942b6a7964c8ed4c95e227060e6c',
                                          40452),
 'scripts/a03_navigation_publication.py': ('04383ed1ba331f308ff805cdacffab761d7cf427122722a7fc92f84f0feb8f68',
                                           157159),
 'scripts/a04_biography_publication.py': ('5d5c6b3385328ed13da046d30e808bf285d5d5142819db31607dd128ddccfcaa',
                                          24521),
 'scripts/a05_biography_publication.py': ('05bb55febc2cb62c07d5dbccba7ac61fc98bd459dc01e5846cf2869ee332506e',
                                          24725),
 'scripts/a06_biography_publication.py': ('2098ac8c8a7f49285870b401963d5efe51a79b4fad31a0e4d1b9ea7544c0daa7',
                                          27136),
 'scripts/a07_biography_publication.py': ('445c1b8650f7c343adeac19fda2de8acdf531431086923a9c071f2110ea493fb',
                                          25484),
 'scripts/a08_biography_publication.py': ('7be55f61e47db3e6c80054ebb70c9fdbe429d82de5cef801ab984ebda1d3bf3d',
                                          27675),
 'scripts/a09_biography_publication.py': ('b8ac9560a18d4a87b1703d7925a4e0fd7ae2f47f751ba82a672b71d0851af6e5',
                                          40307),
 'scripts/academic_deepening_publication.py': ('849f75df1329db537f79fe2005b20f8d06f07563f825c9e66407280df9334f9f',
                                               111380),
 'scripts/accept_phase1.py': ('b6beed60f1f74540c205db1bff0916d5337434732744536236684260ce91e976',
                              12645),
 'scripts/achievement_display_publication.py': ('3b024428dc255a137004384fac750eb08f4ba5da10130c9c46198cf73697cf58',
                                                267202),
 'scripts/build_a01_public_progress.py': ('0d58131dbda176235460f99b545fee8a38f9b61f82461bf0da457f7717dbfd91',
                                          19881),
 'scripts/build_a01_public_progress_v2.py': ('7157192541d57d142eb87e8c38ee4d3555090ddff9301b785d28245c2a8f7739',
                                             13047),
 'scripts/build_site.py': ('7bd1108c4e7f4e3e6d49c7572cdd270c8b39a9a40bc229d9cd79312e572b8443',
                           3126),
 'scripts/check_a01_progress.py': ('674532a2577d586b4b1545c457aac271b32cc38ed8aeae0d44520367a01886cb',
                                   24006),
 'scripts/check_navigation.py': ('64ea7d6020a11b8fed8731998a2d0b1f142333239844090ae3b0d7536e313636',
                                 9884),
 'scripts/check_site.py': ('7b8cacba655ae0cdb4c43faf834dd8300a9bd8ae99ca6be4387801e6e1649656',
                           23755),
 'scripts/home_entry_order_publication.py': ('f7044e2fa57919873f1a026d95f444f2112c6ccb81d72cf0b0aa80a7cbe18387',
                                             152120),
 'scripts/home_lifespan_format_publication.py': ('585b91b3870511f064edea8878f97ae86a9db51a534357d05d17f387bc9273b7',
                                                 156211),
 'scripts/home_portrait_publication.py': ('0fc97550c5a755dff789c86d9013f0b0e48c69a0e7dd0c77264315b91d0de288',
                                          160185),
 'scripts/home_portrait_replacement_publication.py': ('ddb977df0c3059968dadbfe3b4e08c9e6d2ea9bb5df2a4f4fda79c2b3a4ec0bd',
                                                      164282),
 'scripts/home_stories_deepening_publication.py': ('7559827adff72c50d7f01287a36eae71c7e24ae2d0ee0f057dabed12163921fb',
                                                   205870),
 'scripts/make_a01_site_revision.py': ('5a07de50dca32158d9ae46d6233b8586c0e90a9362dd968054d49e9ad68a4395',
                                       4255),
 'scripts/make_a01_site_revision_v2.py': ('78b35da3714ddb227e767e6010695b10443c6a4e432210fd01c67643994f9167',
                                          5067),
 'scripts/make_platform_presentation.py': ('2da5462d9fb6689bb2160cb502b81e3b47cde8070a7e59107df501122439e6a9',
                                           7004),
 'scripts/make_platform_presentation_v2.py': ('a7e027c1da068d406cf246ea8ce6834cdc1f5e4a740e9c9dce5ad79d62cf7cc8',
                                              8337),
 'scripts/nine_line_reading_publication.py': ('9f1c1ad8bc2af571ffb3b4598e759f73073d01d33fc92c38b5609c8122ec776e',
                                              58651),
 'scripts/public_line_labels.py': ('27776862621369ea922d97cc5a1d0ff927f1ec2aa5cbe93a0cacf66fee27f695',
                                   9737),
 'scripts/public_literature_update.py': ('2b6ba9390080b9893c3a57b3ebf457ae50784d57009f32372306825aea558138',
                                         46980),
 'scripts/reader_journey_publication.py': ('8ddebf539c2bfda40543c286df56d60679713c248e33ff835fabcc24d8fa647b',
                                           157765),
 'scripts/reader_navigation_publication.py': ('dbe302c999bf38f70e3c09428d4daa1465a54ae3914ced3190f1efd3274b212f',
                                              109511),
 'scripts/render_a01_history.py': ('500488c6906210e68a8d1478cadc8340d59b455c1b2103d6e34de4653b08bf4b',
                                   16032),
 'scripts/render_a01_primary_reading.py': ('425fe6fa324ab87a94408b2e813aebaa331a82e10d9ee66552967af60caad41f',
                                           7323),
 'scripts/render_a01_progress.py': ('ada60cc0ae158cc5ad25397eb734f43dc23419c37a7e3185720f4cc2f55fc31c',
                                    9458),
 'scripts/render_a02_biography.py': ('e96f30bac5ac91fcd2c04da0b01458c734743bbce299f27852e8539afaf19fe6',
                                     14464),
 'scripts/render_a02_history.py': ('ede516085ede5def83987ccf779b7b17207333280e793c13d5f6b2cede8bdfc1',
                                   22740),
 'scripts/render_a03_biography.py': ('872ecaedbf68f278495b6594fc9e65f1823e65077bd4b2ef301487f828857b9c',
                                     6491),
 'scripts/render_a04_biography.py': ('aed6a1f04aae291d816e2579ddb2f3be9a94374c13cc55e504e650c55d0c1c8a',
                                     9210),
 'scripts/render_a05_biography.py': ('9c0c06cc028d78fb41c9e0dae96754eefe59062d2f8f7c5ad00d35817f7fd2d4',
                                     9651),
 'scripts/render_a06_biography.py': ('b62797c827f8f9d175a5dab67850aa41105e0af7258913878b2bc041a3b3e92b',
                                     11428),
 'scripts/render_a07_biography.py': ('01f5e86435bc9f4eac7f04104892a2d875647f1dd6d3e270e38f3ed28d9dde8e',
                                     9726),
 'scripts/render_a08_biography.py': ('5d31f02e19edecfff1612d5656b1b2ed448e39f8a9d79447b88ee7aea4a407f7',
                                     11000),
 'scripts/render_a09_biography.py': ('2f53b1cae5de7e6b638ae7e557809057ed1f1524333589d3ca669152e6c916b3',
                                     18803),
 'scripts/render_achievement_display.py': ('c74534ffbab531414e4f76726e7d0b2dad19275af33efc19a8818ff3de233cd1',
                                           12076),
 'scripts/render_ai_research.py': ('4293b6cd39150c9e77a6b3c02591c34e83b5d86ecdec675ca9253578af0e2552',
                                   40735),
 'scripts/render_heritage.py': ('bc281999e0bd250eb23e3aa7d76fc08f86bcbcd1ce930c1e974380c5c5071bce',
                                45359),
 'scripts/render_nine_line_deep_reading.py': ('01b69145434fb3b0dae58c475b7dd7f4e4d27f25462134cac1e10bb68645795c',
                                              23018),
 'scripts/render_nine_line_reading.py': ('9c247b53b8cc17be837524a07a49462ea35a3a5699287b10a65d0d380c85e0d0',
                                         9650),
 'scripts/render_reader_journey.py': ('1730df8d63feed9af0616869c27564942efe19f4e907f9fa5839a0d101ee3758',
                                      12101),
 'scripts/render_reader_navigation.py': ('ff28fb202b4a322f8bcf5dfb87a9aef2bfba47ef46bd600f5942d27d41757830',
                                         9912),
 'scripts/render_representative_studies.py': ('827e4790e2f4c6a6d8a6fc9400600a609ef72f4f8b49091feac74ce1576a45c8',
                                              14673),
 'scripts/representative_studies_publication.py': ('648ac108aa16ade0d4ee66947a3dcb3e40275f834a247afd683569373ea8879f',
                                                   109774),
 'scripts/revise_a01_editorial.py': ('9e5170f8b1d305562465bae5b93f9c870380c8617cc05ed5aa5c20325fb7eadb',
                                     5649),
 'scripts/validate_wsl.py': ('94d6f9ab032f877bd5614e562fc7acd4c57078748e77903ab0ced54fdd20a593',
                             15927),
 'scripts/verify_delivery.py': ('0bb8ec49913a55faceabd7424d2672a450403cd410a917068aa96046949ec35d',
                                2400),
 'scripts/verify_online.py': ('98557e9f33575a99290b44d2714b93c2322301b968b563fcda6e5d4ff8c6bbc3',
                              12931),
 'site/.nojekyll': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 0),
 'site/IONIC-ENTRY-RETEST.txt': ('3462b056891a27c335cc2620deb87b245b6c9aea3bdaec607c8a14beca69fe9d',
                                 741),
 'site/QA.txt': ('a60b5f382b31689fa17e2518b7079ef0660674fb62bddbbf564c7b74dfe51067', 290),
 'site/README.txt': ('6e15068b7240ae47d633df3f777e81fbb9e46146ee5f4ab70011f09119b6bbc9', 336),
 'site/ROUTES.txt': ('a734c356877d4534285ab7d71b9fe0f7a17abbced4de3c52f8e60d335301e418', 949),
 'site/achievements/index.html': ('1d5e99f15988d1389cd88ddfb2129460d9ee8b7993fd0fc9dee9faa722cc0e35',
                                  70516),
 'site/assets/chen-qingyun-cas.png': ('0b0ab8e5fd21cddd775ed3fb409c5987704390eab5ce1a05691ec6a3a2d0aec2',
                                      123680),
 'site/assets/chen-qingyun-sioc.jpg': ('7f1b5a80e2c9becd296800ad195ab9b334565cd225849b321fdb34c33f083600',
                                       131476),
 'site/data/achievement-lines.json': ('1c9ec28bf41a7d79214e84a1c07f3bea1e0d91630dd3a88c93c39ff68a9bccec',
                                      39768),
 'site/data/public-sources.json': ('94f8b9f6d0849deb9f26f75947205cfc8c4eb0973045fe958f2121237d987062',
                                   33608),
 'site/index.html': ('c655c18edd7312a0a0434189d1a31f51455991348dce7cab7ccca9b04c947dac', 214083),
 'site/people/index.html': ('91ee7e572fd8de0f7492cdac6df7641ef8387ba2c51e295a5fc7249396d4a2ea',
                            25342),
 'site/people/stories/index.html': ('088f27414326d994599533bb5284f29de60056bfbe14eb302aafa3e2a8896fe5',
                                    13591),
 'site/pftb/index.html': ('84b69f6af5dae73ff2f7eb54d855ae3228f23bff87c24aa045fa283ac2490d90',
                          132594),
 'site/research/index.html': ('cbc946120f8fa53054d32aa7cfa013f52b0c15147954bfb4705023d910232d28',
                              84577),
 'site/topics/chen-reagent/index.html': ('84e5e78602d4060d4304a7365932ac9e33dccc12d92206f5f2fcfd8ecc9ec092',
                                         25543),
 'site/topics/deoxyfluorination/index.html': ('6979e03980b5cc8eabc7599c2396d876d3ff97733c5f78fc306663a99ff5cd25',
                                              16860),
 'site/topics/early-fluoroketones/index.html': ('df30786cf20118cdb48d3a8033372211dd50e455e69ac22d2574608253fddf22',
                                                251335),
 'site/topics/f53/index.html': ('eaf9647fa98c5c8df89e4ee598bf9325a2c0e4f65e89764acae9b35125a8293a',
                                30949),
 'site/topics/fluorinated-small-rings/index.html': ('cdc2962520cc8d62142c23862fe6251503c725a56636aa8674f59c8fdf8ca9fd',
                                                    10871),
 'site/topics/fluoromonomers/index.html': ('c7dd27cd5e2a80825fd7cf5084076ab86f7d2f4505f363c620306a238b2c2e17',
                                           33769),
 'site/topics/fluoroporphyrins/index.html': ('e409a7733b89f356f1f28bd06676215b154fd51ba38cdf38e4fb97927df76151',
                                             19435),
 'site/topics/index.html': ('9873ad87c1c46126755d9ee346b044e36eaa001394f1d5d1ed8043e1f4c584db',
                            5185),
 'site/topics/perfluorosulfonates/index.html': ('be5981c67c8350c0f6971225f9ed347dfbe333ae184719e5993e97275e033b62',
                                                18277),
 'site/topics/refrigerants/index.html': ('305fb84db709e4b6ff68986bb52b10b5097a8554a4d8794f39dd801f36e31605',
                                         24611),
 'site/topics/single-electron-transfer/index.html': ('57a5f16fd021bde3c33e01e6bad946c0021676d6ae7f8224c34f97c7593ba6d7',
                                                     24617),
 'site/topics/sulfonyl-fluoride/index.html': ('adb2871728449b7281cde158970ca221e4ae26cf72c5138f5f958fc21a1e7050',
                                              12193),
 'tools/check_js.mjs': ('78aec6da520080fc1e8f0da5aecdf8d1127e59c779193c7b1aa2f5426b68d39b', 1175),
 'tools/check_site.py': ('a14363401614b6928d4a56740f5ae2e919b569d4b1d888ad03daa8c8c4db2608', 7358),
 'tools/serve_site.py': ('8c9bce6d5751f3e01a49aa12a6432176a04d5d8ca60a683dce967b8ab31384b9', 1987),
 'upstream/chen-qingyun-a2-citations-candidate.zip': ('fa9740d7a244ab4d52885600a312487869d780a82517aa0d0a401215696c4d3e',
                                                      414473),
 'validation/20261111-browser/browser-observations.json': ('dc8e8b1810fea518fe0b01bd7a4bae4f4cac63aa08663f5f59b39cec3dcc40e8',
                                                           1629),
 'validation/20261111-browser/http-project-path.json': ('6637054cbd055a2af8ceec1524659b9b1cbd717be1c93766f5f17808188c9e87',
                                                        4129),
 'validation/20261111-host/host-evidence.json': ('f1ff2507682de33b528be2c13d258ca83ca1cfeca5a347fc24c9d4fa005a2837',
                                                 2552),
 'validation/20261111-host/windows-os.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                    0),
 'validation/20261111-host/windows-os.stdout.txt': ('c9cc626885cc8870035bf95f67fc125a2d819f68fffb3717d8679204c3e9b238',
                                                    128),
 'validation/20261111-host/wsl-list.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                  0),
 'validation/20261111-host/wsl-list.stdout.txt': ('44746d6288ab79914fdb1ef9131102d99a6bc7ad71d2ab51d23de4d2c7e8970f',
                                                  166),
 'validation/20261111-host/wsl-status.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                    0),
 'validation/20261111-host/wsl-status.stdout.txt': ('99069716cca17093ac62f6ec8debd6c13c199fd6729f6f2ae362911ad0893bec',
                                                    47),
 'validation/20261111-online/browser-observations.json': ('67121071ee5739f882cb79946233cfbc2e4c85fd1ac50fd114816be7e3ddab5c',
                                                          1719),
 'validation/20261111-online/ci-artifact/environment.json': ('bb58b3a054ab5ab26f72e8ded26d949e7be8055f188e676c06d9c6ba54948b00',
                                                             961),
 'validation/20261111-online/ci-artifact/logs/all-tests.stderr.txt': ('6f51cd07aa560a8f7e3b6464b1310636731129c62ac81b9d32e5b6d1a6d63604',
                                                                      3821),
 'validation/20261111-online/ci-artifact/logs/all-tests.stdout.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                      0),
 'validation/20261111-online/ci-artifact/logs/git-revision.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                         0),
 'validation/20261111-online/ci-artifact/logs/git-revision.stdout.txt': ('0cee0b7f8f24e7d0c641c0f7076d1abd3c3449235ad883cd8fe1f4a989db4167',
                                                                         41),
 'validation/20261111-online/ci-artifact/logs/git-status.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                       0),
 'validation/20261111-online/ci-artifact/logs/git-status.stdout.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                       0),
 'validation/20261111-online/ci-artifact/logs/numerical-replay.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                             0),
 'validation/20261111-online/ci-artifact/logs/numerical-replay.stdout.txt': ('ff6ea793dbdc488bdbae193307fcad222798527f24a5a03a56f49f97b820b48c',
                                                                             148),
 'validation/20261111-online/ci-artifact/logs/original-delivery-verifier.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                                       0),
 'validation/20261111-online/ci-artifact/logs/original-delivery-verifier.stdout.txt': ('9d55474e2f2cc571cb24195f870d3577bb843f6adb6c6399bafbe4526f160f71',
                                                                                       55),
 'validation/20261111-online/ci-artifact/replay/pftb1966-uv-replay.json': ('c83794634136e2bd08d09b806b400eea603cf1c27c753ca3db2951b9c2c99432',
                                                                           7691),
 'validation/20261111-online/ci-artifact/replay/website-candidate.json': ('cd0ac49d0624cd5a8310c3d3bcadf7992fc677ec4d5e5a6644c0467d9a8f4ee1',
                                                                          3813),
 'validation/20261111-online/ci-artifact/result-comparison.json': ('e24478df161519e6479f066b0ebcad03c6be2de6a6a616994b4756d4d3532e72',
                                                                   73727),
 'validation/20261111-online/ci-artifact/source-inventory.json': ('a26a02889c1f44984675e88eb8770311ccf78fbe68ca6d9939c088a89b65ae89',
                                                                  42960),
 'validation/20261111-online/ci-artifact/summary.json': ('5cd33133a1d44c108a357ab85a9d7a22c9e5aea0181e25299efc76ffd5c52b54',
                                                         3275),
 'validation/20261111-online/ci-artifact/upstream-integrity.json': ('c64d2d086a2c70ab80989587cfbf95877e96e2e64f65c181a451d74e4750b107',
                                                                    5091),
 'validation/20261111-online/github-release.json': ('42d55bd47636090f772c2505a114701ea1557ae5dbafec5decbe3f755f96268d',
                                                    10362),
 'validation/20261111-online/http-acceptance.json': ('81695e43eeac77509bd2ac96f77d7f3ecf8c1fadbcf069c43b46c077a4b198ba',
                                                     17117),
 'validation/20261111-online/http-resolution.json': ('ec329f2b4a25a8804ab6ee5d32f5b6ced0f84f44b241e75a0a8d5c41adcde5d7',
                                                     1017),
 'validation/20261111-online/online-summary.json': ('137fb188e203c63fb981abeeda687016c9d2ed879be7308bde51e00540a01b31',
                                                    909),
 'validation/20261111-remote-integration/integration/environment.json': ('b4c5adbd67030b173e9c912a18a13d08315c740fd12664218e12d85b0cfe6873',
                                                                         938),
 'validation/20261111-remote-integration/integration/logs/all-tests.stderr.txt': ('89045ff183150af5e0baf965f03a537dc78b1a3075c550ce07e5e397f053faf2',
                                                                                  3821),
 'validation/20261111-remote-integration/integration/logs/all-tests.stdout.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                                  0),
 'validation/20261111-remote-integration/integration/logs/git-revision.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                                     0),
 'validation/20261111-remote-integration/integration/logs/git-revision.stdout.txt': ('1bdcbea32b129e84519bc2f0cdca6f347bf528685305ad577e61534e9cfbc866',
                                                                                     41),
 'validation/20261111-remote-integration/integration/logs/git-status.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                                   0),
 'validation/20261111-remote-integration/integration/logs/git-status.stdout.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                                   0),
 'validation/20261111-remote-integration/integration/logs/numerical-replay.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                                         0),
 'validation/20261111-remote-integration/integration/logs/numerical-replay.stdout.txt': ('ff6ea793dbdc488bdbae193307fcad222798527f24a5a03a56f49f97b820b48c',
                                                                                         148),
 'validation/20261111-remote-integration/integration/logs/original-delivery-verifier.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                                                   0),
 'validation/20261111-remote-integration/integration/logs/original-delivery-verifier.stdout.txt': ('9d55474e2f2cc571cb24195f870d3577bb843f6adb6c6399bafbe4526f160f71',
                                                                                                   55),
 'validation/20261111-remote-integration/integration/replay/pftb1966-uv-replay.json': ('c83794634136e2bd08d09b806b400eea603cf1c27c753ca3db2951b9c2c99432',
                                                                                       7691),
 'validation/20261111-remote-integration/integration/replay/website-candidate.json': ('cd0ac49d0624cd5a8310c3d3bcadf7992fc677ec4d5e5a6644c0467d9a8f4ee1',
                                                                                      3813),
 'validation/20261111-remote-integration/integration/result-comparison.json': ('25a09e2b86a0b49c81b02d0e0b98fb3d140e3cad972fa5a123550a2399c8b5ca',
                                                                               73747),
 'validation/20261111-remote-integration/integration/source-inventory.json': ('caeead05e39f279aa1e1531a902a1ca5946921200e6ca4646c2f9e095cd2df30',
                                                                              30215),
 'validation/20261111-remote-integration/integration/summary.json': ('c12b8b35f985a62a451284593a4ba800f7d149b4534ecf2914c18138b54687d6',
                                                                     3114),
 'validation/20261111-remote-integration/integration/upstream-integrity.json': ('c64d2d086a2c70ab80989587cfbf95877e96e2e64f65c181a451d74e4750b107',
                                                                                5091),
 'validation/20261111-remote-integration/logs/clone-committed-integration.stderr.txt': ('3ac9d93f3f490bd0685fb287443b0b79dd959c3130562a217f6fc03dfb818c9b',
                                                                                        67),
 'validation/20261111-remote-integration/logs/clone-committed-integration.stdout.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                                        0),
 'validation/20261111-remote-integration/logs/cloned-commit.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                          0),
 'validation/20261111-remote-integration/logs/cloned-commit.stdout.txt': ('1bdcbea32b129e84519bc2f0cdca6f347bf528685305ad577e61534e9cfbc866',
                                                                          41),
 'validation/20261111-remote-integration/logs/integrated-acceptance.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                                  0),
 'validation/20261111-remote-integration/logs/integrated-acceptance.stdout.txt': ('80576b32b75a04a63fd7a615199ffb67d496633d9ed19fa80b2b3d9c9a1a4222',
                                                                                  263),
 'validation/20261111-remote-integration/logs/linux-filesystem.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                             0),
 'validation/20261111-remote-integration/logs/linux-filesystem.stdout.txt': ('c75271b9397639a9d9d1263796016b924b5a58759121894a893a565fa875b9e9',
                                                                             10),
 'validation/20261111-remote-integration/logs/linux-node-runtime.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                               0),
 'validation/20261111-remote-integration/logs/linux-node-runtime.stdout.txt': ('8f4b3b2f2108b53f1e16656e2236979d1618896de80ca38af5dfe32bfe6988d6',
                                                                               145),
 'validation/20261111-remote-integration/logs/linux-node-version.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                               0),
 'validation/20261111-remote-integration/logs/linux-node-version.stdout.txt': ('adc2fc6c2cfc7713e5d938152d45594a33c82a28857fb99667a5a5388c399e1a',
                                                                               9),
 'validation/20261111-remote-integration/logs/original-integrity.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                               0),
 'validation/20261111-remote-integration/logs/original-integrity.stdout.txt': ('9d55474e2f2cc571cb24195f870d3577bb843f6adb6c6399bafbe4526f160f71',
                                                                               55),
 'validation/20261111-remote-integration/logs/original-replay.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                            0),
 'validation/20261111-remote-integration/logs/original-replay.stdout.txt': ('ff6ea793dbdc488bdbae193307fcad222798527f24a5a03a56f49f97b820b48c',
                                                                            148),
 'validation/20261111-remote-integration/logs/original-tests.stderr.txt': ('749903a3ec7d455ebe8577a21584b763b8b57af169f1a334cf673044b94d258a',
                                                                           1406),
 'validation/20261111-remote-integration/logs/original-tests.stdout.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                           0),
 'validation/20261111-remote-integration/logs/source-branch.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                          0),
 'validation/20261111-remote-integration/logs/source-branch.stdout.txt': ('6403203dd5a0867eb14d104ee8a73730bd72dd9ad92e78d996a6dba0a5dcfc01',
                                                                          5),
 'validation/20261111-remote-integration/logs/source-commit.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                          0),
 'validation/20261111-remote-integration/logs/source-commit.stdout.txt': ('1bdcbea32b129e84519bc2f0cdca6f347bf528685305ad577e61534e9cfbc866',
                                                                          41),
 'validation/20261111-remote-integration/logs/source-status.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                          0),
 'validation/20261111-remote-integration/logs/source-status.stdout.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                          0),
 'validation/20261111-remote-integration/logs/website-build.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                          0),
 'validation/20261111-remote-integration/logs/website-build.stdout.txt': ('133cadd7ae97b996db619d6ec185f00038f443ece4038d987f224270a1ae3ac1',
                                                                          936),
 'validation/20261111-remote-integration/logs/website-static-check.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                                 0),
 'validation/20261111-remote-integration/logs/website-static-check.stdout.txt': ('3948da5e47ae51a2380399c615da192eb6e37fdb62f063dc4c941ac0e69baae2',
                                                                                 387),
 'validation/20261111-remote-integration/node-runtime/SHASUMS256.txt': ('496b662fcf38fca596f8d1dd2e95245ac1597dd49e0c3c60235b0b6f2c072900',
                                                                        2967),
 'validation/20261111-remote-integration/node-runtime/provenance.json': ('18d97e960f84002b8588039ef8bef99e408a05817583dced7cce24d2ac13ef9d',
                                                                         1161),
 'validation/20261111-remote-integration/node-runtime/retrieval.json': ('359f3229b03f67ae7960d411e01008fadb07a87e5880604864067ab3016ba13e',
                                                                        536),
 'validation/20261111-remote-integration/original-replay/pftb1966-uv-replay.json': ('c83794634136e2bd08d09b806b400eea603cf1c27c753ca3db2951b9c2c99432',
                                                                                    7691),
 'validation/20261111-remote-integration/original-replay/website-candidate.json': ('cd0ac49d0624cd5a8310c3d3bcadf7992fc677ec4d5e5a6644c0467d9a8f4ee1',
                                                                                   3813),
 'validation/20261111-remote-integration/original-result-comparison.json': ('6dab67091eb3347253853aa8c1ac039a51032b4d941d6f906975dbcbd596929a',
                                                                            73785),
 'validation/20261111-remote-integration/site-check.json': ('0f17e24a2e5986dc383c057678e8a529d600601c3c75f8c9655e6c8331e02b40',
                                                            176507),
 'validation/20261111-remote-integration/site-dist/.nojekyll': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                0),
 'validation/20261111-remote-integration/site-dist/achievements/index.html': ('d9b4024ff8bbe8519d8d77b0c6785165db3ae9fe4ed70214ca60ea218872107d',
                                                                              22706),
 'validation/20261111-remote-integration/site-dist/data/achievement-lines.json': ('1c9ec28bf41a7d79214e84a1c07f3bea1e0d91630dd3a88c93c39ff68a9bccec',
                                                                                  39768),
 'validation/20261111-remote-integration/site-dist/data/public-sources.json': ('94f8b9f6d0849deb9f26f75947205cfc8c4eb0973045fe958f2121237d987062',
                                                                               33608),
 'validation/20261111-remote-integration/site-dist/index.html': ('2d13bae2c39b5b41964fc6c50481309dd62eb058a6f68e61051e5d42539344a9',
                                                                 142901),
 'validation/20261111-remote-integration/site-dist/pftb/index.html': ('0d4396b85f8cfd772edcf8fe9bc192d845268399e1ed3834e1d83562639ba372',
                                                                      97584),
 'validation/20261111-remote-integration/site-dist/topics/chen-reagent/index.html': ('649a7e6f3b3431982eba13d5036e3cd2acc22fc40cfe791c0bb9a91aabfd7553',
                                                                                     10199),
 'validation/20261111-remote-integration/site-dist/topics/deoxyfluorination/index.html': ('0c71ad2500ae5f094be1cd10cfd9415a376deb905e9d936d2628ef8143edad66',
                                                                                          5510),
 'validation/20261111-remote-integration/site-dist/topics/early-fluoroketones/index.html': ('fcdc4df61f18e12ac168c4aab65b9f0438e987bd9f311997755c875cc615093b',
                                                                                            7023),
 'validation/20261111-remote-integration/site-dist/topics/f53/index.html': ('942b97805e2e785192face1ef3718b4180c276f77b5133f526c70532cfd83175',
                                                                            8145),
 'validation/20261111-remote-integration/site-dist/topics/fluorinated-small-rings/index.html': ('a98fe98626644e80de5b4584114e32aa0842cc3a877a41f8a76f6543571bd239',
                                                                                                5892),
 'validation/20261111-remote-integration/site-dist/topics/fluoromonomers/index.html': ('366a55eba14a054cc678016f8c71cd391921e1eaef4cd1fd0e22cc2ce42dd904',
                                                                                       6450),
 'validation/20261111-remote-integration/site-dist/topics/fluoroporphyrins/index.html': ('84b4b2ed0e59fdb940bfa38e5d9c0326f3fce1335ba9d71b1b19108f57a63bbf',
                                                                                         5969),
 'validation/20261111-remote-integration/site-dist/topics/index.html': ('3b891eb056f7d5d76681ff5395149e474ec934b0d9ab2d4729df9c0441d580ad',
                                                                        1367),
 'validation/20261111-remote-integration/site-dist/topics/perfluorosulfonates/index.html': ('6618d0d4d7a135e88c924ae3ecd420338e9613190447676f608af9939aea84ec',
                                                                                            5272),
 'validation/20261111-remote-integration/site-dist/topics/refrigerants/index.html': ('4d41e38398b8ec12584c6700fd84da1c1b42f9bc1c722fba64a2c151ed6af6e7',
                                                                                     6227),
 'validation/20261111-remote-integration/site-dist/topics/single-electron-transfer/index.html': ('64c162a1ccc9c69bc82bd2ff9de0b70aa12e1ac103fc7f0a56123b134d699bbb',
                                                                                                 5839),
 'validation/20261111-remote-integration/site-dist/topics/sulfonyl-fluoride/index.html': ('62beb639cb5448473dd799cf5e23d3a4a42b8e4ccd0204b02cadeb2b7d6d6032',
                                                                                          5003),
 'validation/20261111-remote-integration/summary.json': ('203c4f77aa5a09ec54c5f5834a6772d6f5904b75b2b64d1a7712aa9848861e71',
                                                         7553),
 'validation/20261111-wsl2-migration/integration/environment.json': ('58d0786113664772002c67d2719dc460766ed4eaee0e1350aac1cbdbc34f6bbb',
                                                                     938),
 'validation/20261111-wsl2-migration/integration/logs/all-tests.stderr.txt': ('6bb1dc4e80e3b2859cc55d1602ede83e7153f52200545dc3aec39d0e0003172b',
                                                                              3183),
 'validation/20261111-wsl2-migration/integration/logs/all-tests.stdout.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                              0),
 'validation/20261111-wsl2-migration/integration/logs/git-revision.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                                 0),
 'validation/20261111-wsl2-migration/integration/logs/git-revision.stdout.txt': ('9b6f3208c76732d173c65ec073786a6973093e5759122fe866f1cf77cb7803fa',
                                                                                 41),
 'validation/20261111-wsl2-migration/integration/logs/git-status.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                               0),
 'validation/20261111-wsl2-migration/integration/logs/git-status.stdout.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                               0),
 'validation/20261111-wsl2-migration/integration/logs/numerical-replay.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                                     0),
 'validation/20261111-wsl2-migration/integration/logs/numerical-replay.stdout.txt': ('ff6ea793dbdc488bdbae193307fcad222798527f24a5a03a56f49f97b820b48c',
                                                                                     148),
 'validation/20261111-wsl2-migration/integration/logs/original-delivery-verifier.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                                               0),
 'validation/20261111-wsl2-migration/integration/logs/original-delivery-verifier.stdout.txt': ('9d55474e2f2cc571cb24195f870d3577bb843f6adb6c6399bafbe4526f160f71',
                                                                                               55),
 'validation/20261111-wsl2-migration/integration/replay/pftb1966-uv-replay.json': ('c83794634136e2bd08d09b806b400eea603cf1c27c753ca3db2951b9c2c99432',
                                                                                   7691),
 'validation/20261111-wsl2-migration/integration/replay/website-candidate.json': ('cd0ac49d0624cd5a8310c3d3bcadf7992fc677ec4d5e5a6644c0467d9a8f4ee1',
                                                                                  3813),
 'validation/20261111-wsl2-migration/integration/result-comparison.json': ('2346e4d1381d29875b5c43661323eee61231bbfd36cb17ce16b39b6e85ce52c0',
                                                                           73739),
 'validation/20261111-wsl2-migration/integration/source-inventory.json': ('72f86a986d10c7ba174f99fa29e52ffa724f23995c36284550632d39bd115fa7',
                                                                          15470),
 'validation/20261111-wsl2-migration/integration/summary.json': ('ca663be39f7e14946e292063ad81705252714b12f10f3e67c582821296742520',
                                                                 3110),
 'validation/20261111-wsl2-migration/integration/upstream-integrity.json': ('c64d2d086a2c70ab80989587cfbf95877e96e2e64f65c181a451d74e4750b107',
                                                                            5091),
 'validation/20261111-wsl2-migration/logs/clone-committed-integration.stderr.txt': ('0f8c9caa31b268030ddecc4b0457f1d962e2eeb7bebdc0243aef8ea43792f6e5',
                                                                                    67),
 'validation/20261111-wsl2-migration/logs/clone-committed-integration.stdout.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                                    0),
 'validation/20261111-wsl2-migration/logs/cloned-commit.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                      0),
 'validation/20261111-wsl2-migration/logs/cloned-commit.stdout.txt': ('9b6f3208c76732d173c65ec073786a6973093e5759122fe866f1cf77cb7803fa',
                                                                      41),
 'validation/20261111-wsl2-migration/logs/integrated-acceptance.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                              0),
 'validation/20261111-wsl2-migration/logs/integrated-acceptance.stdout.txt': ('f3bcb4e8764a8e82fe7d1617d53fd3701d2b942f8e36fee243ffae0cfef8f975',
                                                                              259),
 'validation/20261111-wsl2-migration/logs/linux-filesystem.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                         0),
 'validation/20261111-wsl2-migration/logs/linux-filesystem.stdout.txt': ('c75271b9397639a9d9d1263796016b924b5a58759121894a893a565fa875b9e9',
                                                                         10),
 'validation/20261111-wsl2-migration/logs/linux-node-runtime.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                           0),
 'validation/20261111-wsl2-migration/logs/linux-node-runtime.stdout.txt': ('27244b6fc949d92b931c8778e356a2df14cc72cc579ca530cceeab60792598f2',
                                                                           145),
 'validation/20261111-wsl2-migration/logs/linux-node-version.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                           0),
 'validation/20261111-wsl2-migration/logs/linux-node-version.stdout.txt': ('adc2fc6c2cfc7713e5d938152d45594a33c82a28857fb99667a5a5388c399e1a',
                                                                           9),
 'validation/20261111-wsl2-migration/logs/original-integrity.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                           0),
 'validation/20261111-wsl2-migration/logs/original-integrity.stdout.txt': ('9d55474e2f2cc571cb24195f870d3577bb843f6adb6c6399bafbe4526f160f71',
                                                                           55),
 'validation/20261111-wsl2-migration/logs/original-replay.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                        0),
 'validation/20261111-wsl2-migration/logs/original-replay.stdout.txt': ('ff6ea793dbdc488bdbae193307fcad222798527f24a5a03a56f49f97b820b48c',
                                                                        148),
 'validation/20261111-wsl2-migration/logs/original-tests.stderr.txt': ('e3db95ec654b1f1ea5637a32f368afe4df47e01c10c997e85175078b007911cd',
                                                                       1406),
 'validation/20261111-wsl2-migration/logs/original-tests.stdout.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                       0),
 'validation/20261111-wsl2-migration/logs/source-branch.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                      0),
 'validation/20261111-wsl2-migration/logs/source-branch.stdout.txt': ('2fee2715acf586ce3802afb3a39fdfa6305e89f26cea48257a5dbcb2024a5835',
                                                                      30),
 'validation/20261111-wsl2-migration/logs/source-commit.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                      0),
 'validation/20261111-wsl2-migration/logs/source-commit.stdout.txt': ('9b6f3208c76732d173c65ec073786a6973093e5759122fe866f1cf77cb7803fa',
                                                                      41),
 'validation/20261111-wsl2-migration/logs/source-status.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                      0),
 'validation/20261111-wsl2-migration/logs/source-status.stdout.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                      0),
 'validation/20261111-wsl2-migration/logs/website-build.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                      0),
 'validation/20261111-wsl2-migration/logs/website-build.stdout.txt': ('4b9065d64f9e110d7c65aeb6082577efc4043118df75d852219218252e060d77',
                                                                      932),
 'validation/20261111-wsl2-migration/logs/website-static-check.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                             0),
 'validation/20261111-wsl2-migration/logs/website-static-check.stdout.txt': ('9fea05f8d5200cea3922aa1019923303bd8b5c9985128c52cf4e93c13d3c07c0',
                                                                             383),
 'validation/20261111-wsl2-migration/node-runtime/SHASUMS256.txt': ('496b662fcf38fca596f8d1dd2e95245ac1597dd49e0c3c60235b0b6f2c072900',
                                                                    2967),
 'validation/20261111-wsl2-migration/node-runtime/provenance.json': ('8d35e283d418d335b87b8159de4f23fab3350cedc5da492648cc6f70ef2da9a8',
                                                                     1161),
 'validation/20261111-wsl2-migration/node-runtime/retrieval.json': ('359f3229b03f67ae7960d411e01008fadb07a87e5880604864067ab3016ba13e',
                                                                    536),
 'validation/20261111-wsl2-migration/original-replay/pftb1966-uv-replay.json': ('c83794634136e2bd08d09b806b400eea603cf1c27c753ca3db2951b9c2c99432',
                                                                                7691),
 'validation/20261111-wsl2-migration/original-replay/website-candidate.json': ('cd0ac49d0624cd5a8310c3d3bcadf7992fc677ec4d5e5a6644c0467d9a8f4ee1',
                                                                               3813),
 'validation/20261111-wsl2-migration/original-result-comparison.json': ('58572a26dd613a657e2838ca56b94106bfc1610ce02e5dfe2194e03ac31492f6',
                                                                        73777),
 'validation/20261111-wsl2-migration/site-check.json': ('5ec52e0d44c858b74f70f1b887a7f347fcc7340bcf0bc324be96567607e6944e',
                                                        176264),
 'validation/20261111-wsl2-migration/site-dist/.nojekyll': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                            0),
 'validation/20261111-wsl2-migration/site-dist/achievements/index.html': ('d9b4024ff8bbe8519d8d77b0c6785165db3ae9fe4ed70214ca60ea218872107d',
                                                                          22706),
 'validation/20261111-wsl2-migration/site-dist/data/achievement-lines.json': ('1c9ec28bf41a7d79214e84a1c07f3bea1e0d91630dd3a88c93c39ff68a9bccec',
                                                                              39768),
 'validation/20261111-wsl2-migration/site-dist/data/public-sources.json': ('94f8b9f6d0849deb9f26f75947205cfc8c4eb0973045fe958f2121237d987062',
                                                                           33608),
 'validation/20261111-wsl2-migration/site-dist/index.html': ('2d13bae2c39b5b41964fc6c50481309dd62eb058a6f68e61051e5d42539344a9',
                                                             142901),
 'validation/20261111-wsl2-migration/site-dist/pftb/index.html': ('0d4396b85f8cfd772edcf8fe9bc192d845268399e1ed3834e1d83562639ba372',
                                                                  97584),
 'validation/20261111-wsl2-migration/site-dist/topics/chen-reagent/index.html': ('649a7e6f3b3431982eba13d5036e3cd2acc22fc40cfe791c0bb9a91aabfd7553',
                                                                                 10199),
 'validation/20261111-wsl2-migration/site-dist/topics/deoxyfluorination/index.html': ('0c71ad2500ae5f094be1cd10cfd9415a376deb905e9d936d2628ef8143edad66',
                                                                                      5510),
 'validation/20261111-wsl2-migration/site-dist/topics/early-fluoroketones/index.html': ('fcdc4df61f18e12ac168c4aab65b9f0438e987bd9f311997755c875cc615093b',
                                                                                        7023),
 'validation/20261111-wsl2-migration/site-dist/topics/f53/index.html': ('942b97805e2e785192face1ef3718b4180c276f77b5133f526c70532cfd83175',
                                                                        8145),
 'validation/20261111-wsl2-migration/site-dist/topics/fluorinated-small-rings/index.html': ('a98fe98626644e80de5b4584114e32aa0842cc3a877a41f8a76f6543571bd239',
                                                                                            5892),
 'validation/20261111-wsl2-migration/site-dist/topics/fluoromonomers/index.html': ('366a55eba14a054cc678016f8c71cd391921e1eaef4cd1fd0e22cc2ce42dd904',
                                                                                   6450),
 'validation/20261111-wsl2-migration/site-dist/topics/fluoroporphyrins/index.html': ('84b4b2ed0e59fdb940bfa38e5d9c0326f3fce1335ba9d71b1b19108f57a63bbf',
                                                                                     5969),
 'validation/20261111-wsl2-migration/site-dist/topics/index.html': ('3b891eb056f7d5d76681ff5395149e474ec934b0d9ab2d4729df9c0441d580ad',
                                                                    1367),
 'validation/20261111-wsl2-migration/site-dist/topics/perfluorosulfonates/index.html': ('6618d0d4d7a135e88c924ae3ecd420338e9613190447676f608af9939aea84ec',
                                                                                        5272),
 'validation/20261111-wsl2-migration/site-dist/topics/refrigerants/index.html': ('4d41e38398b8ec12584c6700fd84da1c1b42f9bc1c722fba64a2c151ed6af6e7',
                                                                                 6227),
 'validation/20261111-wsl2-migration/site-dist/topics/single-electron-transfer/index.html': ('64c162a1ccc9c69bc82bd2ff9de0b70aa12e1ac103fc7f0a56123b134d699bbb',
                                                                                             5839),
 'validation/20261111-wsl2-migration/site-dist/topics/sulfonyl-fluoride/index.html': ('62beb639cb5448473dd799cf5e23d3a4a42b8e4ccd0204b02cadeb2b7d6d6032',
                                                                                      5003),
 'validation/20261111-wsl2-migration/summary.json': ('fd15629d7b5acab769e22101cca6c1a68d785a8566c0e7b5e75fe233a9a94d90',
                                                     7583),
 'validation/20261111-wsl2/integration/environment.json': ('58fa3114f988796ea0ee4f556eda1d40da8547519b55333e036fb0719a103bf8',
                                                           938),
 'validation/20261111-wsl2/integration/logs/all-tests.stderr.txt': ('6bb1dc4e80e3b2859cc55d1602ede83e7153f52200545dc3aec39d0e0003172b',
                                                                    3183),
 'validation/20261111-wsl2/integration/logs/all-tests.stdout.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                    0),
 'validation/20261111-wsl2/integration/logs/git-revision.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                       0),
 'validation/20261111-wsl2/integration/logs/git-revision.stdout.txt': ('acb55234cec5398de441dd7a40bf422de0ce0a7c82f684cdadeb50d0f725f042',
                                                                       41),
 'validation/20261111-wsl2/integration/logs/git-status.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                     0),
 'validation/20261111-wsl2/integration/logs/git-status.stdout.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                     0),
 'validation/20261111-wsl2/integration/logs/numerical-replay.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                           0),
 'validation/20261111-wsl2/integration/logs/numerical-replay.stdout.txt': ('ff6ea793dbdc488bdbae193307fcad222798527f24a5a03a56f49f97b820b48c',
                                                                           148),
 'validation/20261111-wsl2/integration/logs/original-delivery-verifier.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                                     0),
 'validation/20261111-wsl2/integration/logs/original-delivery-verifier.stdout.txt': ('9d55474e2f2cc571cb24195f870d3577bb843f6adb6c6399bafbe4526f160f71',
                                                                                     55),
 'validation/20261111-wsl2/integration/replay/pftb1966-uv-replay.json': ('c83794634136e2bd08d09b806b400eea603cf1c27c753ca3db2951b9c2c99432',
                                                                         7691),
 'validation/20261111-wsl2/integration/replay/website-candidate.json': ('cd0ac49d0624cd5a8310c3d3bcadf7992fc677ec4d5e5a6644c0467d9a8f4ee1',
                                                                        3813),
 'validation/20261111-wsl2/integration/result-comparison.json': ('3168ffe92c43084ebdd2a1f7c00eb226d64418b4c6a18d0c6504178c69c5976a',
                                                                 73719),
 'validation/20261111-wsl2/integration/source-inventory.json': ('917b768a990d751e5642616c55cd27497bc7898f31a4a7931d7ba4da0c168cbe',
                                                                3813),
 'validation/20261111-wsl2/integration/summary.json': ('e1315a0cb2e0b4fee32c72b795acf80e058c78d7db77928ac7c5cb00e072f72a',
                                                       3100),
 'validation/20261111-wsl2/integration/upstream-integrity.json': ('c64d2d086a2c70ab80989587cfbf95877e96e2e64f65c181a451d74e4750b107',
                                                                  5091),
 'validation/20261111-wsl2/logs/clone-committed-integration.stderr.txt': ('d81b63fba8a4515289f0af828e301358e1c0890b84324d8a011e7889273021e5',
                                                                          67),
 'validation/20261111-wsl2/logs/clone-committed-integration.stdout.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                          0),
 'validation/20261111-wsl2/logs/cloned-commit.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                            0),
 'validation/20261111-wsl2/logs/cloned-commit.stdout.txt': ('acb55234cec5398de441dd7a40bf422de0ce0a7c82f684cdadeb50d0f725f042',
                                                            41),
 'validation/20261111-wsl2/logs/integrated-acceptance.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                    0),
 'validation/20261111-wsl2/logs/integrated-acceptance.stdout.txt': ('775bf6f2dc3317d104ab1d56578b74f281c81f5a107fe37f01aa83bf1cb0d534',
                                                                    249),
 'validation/20261111-wsl2/logs/linux-filesystem.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                               0),
 'validation/20261111-wsl2/logs/linux-filesystem.stdout.txt': ('c75271b9397639a9d9d1263796016b924b5a58759121894a893a565fa875b9e9',
                                                               10),
 'validation/20261111-wsl2/logs/original-integrity.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                                 0),
 'validation/20261111-wsl2/logs/original-integrity.stdout.txt': ('9d55474e2f2cc571cb24195f870d3577bb843f6adb6c6399bafbe4526f160f71',
                                                                 55),
 'validation/20261111-wsl2/logs/original-replay.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                              0),
 'validation/20261111-wsl2/logs/original-replay.stdout.txt': ('ff6ea793dbdc488bdbae193307fcad222798527f24a5a03a56f49f97b820b48c',
                                                              148),
 'validation/20261111-wsl2/logs/original-tests.stderr.txt': ('e3db95ec654b1f1ea5637a32f368afe4df47e01c10c997e85175078b007911cd',
                                                             1406),
 'validation/20261111-wsl2/logs/original-tests.stdout.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                             0),
 'validation/20261111-wsl2/logs/source-branch.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                            0),
 'validation/20261111-wsl2/logs/source-branch.stdout.txt': ('2fee2715acf586ce3802afb3a39fdfa6305e89f26cea48257a5dbcb2024a5835',
                                                            30),
 'validation/20261111-wsl2/logs/source-commit.stderr.txt': ('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                                                            0),
 'validation/20261111-wsl2/logs/source-commit.stdout.txt': ('acb55234cec5398de441dd7a40bf422de0ce0a7c82f684cdadeb50d0f725f042',
                                                            41),
 'validation/20261111-wsl2/original-replay/pftb1966-uv-replay.json': ('c83794634136e2bd08d09b806b400eea603cf1c27c753ca3db2951b9c2c99432',
                                                                      7691),
 'validation/20261111-wsl2/original-replay/website-candidate.json': ('cd0ac49d0624cd5a8310c3d3bcadf7992fc677ec4d5e5a6644c0467d9a8f4ee1',
                                                                     3813),
 'validation/20261111-wsl2/original-result-comparison.json': ('6e0532b1546fa9de72b3bfdab8a35e611a779ea2e91ce6d8678f026188c23a72',
                                                              73757),
 'validation/20261111-wsl2/summary.json': ('5a488708ac4df977a661224729b29557118ba7e1847188aab5bfb3812125922c',
                                           4759),
 'validation/a01-progress-20261113/README_zh-CN.md': ('4e4c1c8d262ae89b9ee674d4f8c31ef73f7001a3842f6e9cb86e43f88a3fa643',
                                                      829),
 'validation/a01-progress-20261113/browser-check.json': ('19d828845e771203e2109cd54d84ae7b60ee18955ab05a10c1b5c7e13dc96b54',
                                                         6396),
 'validation/a01-progress-20261113/node-tool-record.json': ('fe12902231b0e11bd8482d74d73d416c9cf3e624bcbca64c649b4349e08fb9bf',
                                                            1308),
 'validation/a01-progress-20261113/overview.json': ('50deb4025f169eb97049e3b6bddb8e846ea1556a54a05c2f18386dc443612297',
                                                    4602),
 'validation/a01-progress-20261113/windows-checks.json': ('c85d265ab53c9b2c9d37dad13eaf4f87de028dbde800f681e6b97345ab01653c',
                                                          4150),
 'validation/a01-progress-20261113/windows-newline-diagnosis.json': ('86c38231fd2afc03ca94d928717dfa7e5a410d393520385302802f905d911189',
                                                                     504),
 'validation/a01-progress-20261113/wsl-initial-checks.json': ('613d05fcf6dab6ebdd657339de8ee8945f14f4d6dc057f31414b6a8bd383f1f0',
                                                              3557),
 'validation/a01-progress-20261113/wsl-native-node-checks.json': ('78726cba9bce597eda4e03bbbb3a7f0cbffde4bbed014ba03b8a319575cd3c5d',
                                                                  3262),
 'validation/a01-progress-20261113/wsl-source-summary.json': ('50d6c2c366374e07dfc891a070345a2a1bb2d51ca0ae503fd9003db3b14dba85',
                                                              2385),
 'validation/protected-parent-files.json': ('37ddfed166f8c62ec1d9fa2691a28108a33b389a24125ce894d88a8a1172b8ee',
                                            2510)}
REVIEWED_FILES = {'site/index.html': ('a918d39e3e0229dcbc52f1f03f71eeab67469b2adbdd1dbeab0ce5b6f6f80b1e', 213131),
 'site/achievements/index.html': ('efdc240f3a9b36e01b683fbd5156d78e4c9a47c580125fe087c4f9dae848d8e6',
                                  70136),
 'site/research/index.html': ('653c8198b8deb22a521f57afd952a9ef29307b17772c9aa90e4d37b82f397ecf',
                              83073),
 'scripts/a01_publication_contract.py': ('4667c5f4ce452b54165d0172769aa11f8a1244a99a26238596ef8df22255e9f4',
                                         321941),
 'scripts/check_site.py': ('44658821c849861ff8f24f608d656b4136e3f85cbfae65e1cb1c49557ec1447d',
                           23751)}
APPROVED_EDITS = {'site/index.html': [{'old': '<article class="heritage-card" id="heritage-story-st09"><p '
                             'class="heritage-meta">材料开拓与分工协作</p><h3>把少量六氟丙烯变成可用单体</h3><p '
                             'class="heritage-meta">人物：陈庆云、蒋锡夔、胡亚东、氟橡胶课题组同事</p><p>从裂解产物中的少量六氟丙烯，到可用于材料研究的单体，制取条件和低温分离需要同时解决。陈庆云、蒋锡夔等人的研究，与技术人员的分馏实验、同事的物资保障相互接续。</p><span '
                             'class="heritage-tag">A02（含氟单体、氟橡胶与氟油）</span><p><a '
                             'href="people/stories/index.html#stories-st09" '
                             'aria-label="阅读全文：把少量六氟丙烯变成可用单体">阅读全文 →</a></p></article>',
                      'new': '<article class="heritage-card" id="heritage-story-st09"><p '
                             'class="heritage-meta">材料开拓与分工协作</p><h3>把少量六氟丙烯变成可用单体</h3><p '
                             'class="heritage-meta">人物：陈庆云、蒋锡夔、胡亚东、氟橡胶课题组同事</p><p>六氟丙烯从裂解产物走向材料原料，需要制取、低温分离与同事的协作。</p><span '
                             'class="heritage-tag">A02（含氟单体、氟橡胶与氟油）</span><p><a '
                             'href="people/stories/index.html#stories-st09" '
                             'aria-label="阅读全文：把少量六氟丙烯变成可用单体">阅读全文 →</a></p></article>',
                      'count': 1,
                      'reason': 'shorten st09 lead; preserve stable anchor and named participants'},
                     {'old': '<article class="heritage-card" id="heritage-story-st03"><p '
                             'class="heritage-meta">科研与工程协作</p><h3>从实验室到实验厂：与顾子恺共同推进F-53</h3><p '
                             'class="heritage-meta">人物：陈庆云、顾子恺、研究组与工厂同事</p><p>F-53样品先到电镀厂试用，再进入实验厂扩大试验。陈庆云跟随成果走向转化，特别肯定总工程师顾子恺的作用；化学路线、工程设备与使用单位共同推进了这项工作。</p><span '
                             'class="heritage-tag">A04（F-53铬雾抑制剂）</span><p><a '
                             'href="people/stories/index.html#stories-st03" '
                             'aria-label="阅读全文：从实验室到实验厂：与顾子恺共同推进F-53">阅读全文 →</a></p></article>',
                      'new': '<article class="heritage-card" id="heritage-story-st03"><p '
                             'class="heritage-meta">科研与工程协作</p><h3>从实验室到实验厂：与顾子恺共同推进F-53</h3><p '
                             'class="heritage-meta">人物：陈庆云、顾子恺、研究组与工厂同事</p><p>F-53从实验室走向工厂，陈庆云与顾子恺、实验厂和电镀厂共同衔接化学研究与工程转化。</p><span '
                             'class="heritage-tag">A04（F-53铬雾抑制剂）</span><p><a '
                             'href="people/stories/index.html#stories-st03" '
                             'aria-label="阅读全文：从实验室到实验厂：与顾子恺共同推进F-53">阅读全文 →</a></p></article>',
                      'count': 1,
                      'reason': 'shorten st03 lead; preserve stable anchor and named participants'},
                     {'old': '<article class="heritage-card" id="heritage-story-st10"><p '
                             'class="heritage-meta">中试接力与跨单位合作</p><h3>把制冷剂、润滑油与冰箱接起来</h3><p '
                             'class="heritage-meta">人物：陈庆云、林永达、杨映松、上海有机所实验厂、嘉兴冰箱厂、广州化学所</p><p>林永达、杨映松继续参加实验厂中试；陈庆云与林永达研究配套冷冻机油，并与嘉兴冰箱厂等单位协作。材料从合成走向应用，需要把连续工艺、润滑油和整机试用衔接起来。</p><span '
                             'class="heritage-tag">A05（制冷剂与配套技术）</span><p><a '
                             'href="people/stories/index.html#stories-st10" '
                             'aria-label="阅读全文：把制冷剂、润滑油与冰箱接起来">阅读全文 →</a></p></article>',
                      'new': '<article class="heritage-card" id="heritage-story-st10"><p '
                             'class="heritage-meta">中试接力与跨单位合作</p><h3>把制冷剂、润滑油与冰箱接起来</h3><p '
                             'class="heritage-meta">人物：陈庆云、林永达、杨映松、上海有机所实验厂、嘉兴冰箱厂、广州化学所</p><p>制冷剂的应用把合成、中试、配套冷冻机油和冰箱试用连在一起，也连接了不同人员与单位。</p><span '
                             'class="heritage-tag">A05（制冷剂与配套技术）</span><p><a '
                             'href="people/stories/index.html#stories-st10" '
                             'aria-label="阅读全文：把制冷剂、润滑油与冰箱接起来">阅读全文 →</a></p></article>',
                      'count': 1,
                      'reason': 'shorten st10 lead; preserve stable anchor and named participants'},
                     {'old': '<article class="heritage-card" id="heritage-story-st05"><p '
                             'class="heritage-meta">启发式育人</p><h3>刘超的选题：先读资料，再提出自己的方向</h3><p '
                             'class="heritage-meta">人物：陈庆云、刘超</p><p>刘超进组后，陈庆云先介绍方向、交给资料，再约一周后讨论。阅读和交流之后，刘超选择了含氟卟啉。导师提供起点，也把提出意见和作出选择的空间交给学生。</p><span '
                             'class="heritage-tag">A09（学科建设与人才培养）</span><span '
                             'class="heritage-tag">A08（交叉研究与晚年拓展）</span><p><a '
                             'href="people/stories/index.html#stories-st05" '
                             'aria-label="阅读全文：刘超的选题：先读资料，再提出自己的方向">阅读全文 →</a></p></article>',
                      'new': '<article class="heritage-card" id="heritage-story-st05"><p '
                             'class="heritage-meta">启发式育人</p><h3>刘超的选题：先读资料，再提出自己的方向</h3><p '
                             'class="heritage-meta">人物：陈庆云、刘超</p><p>从阅读资料到共同讨论，刘超参与选择含氟卟啉方向，逐步形成自己的研究判断。</p><span '
                             'class="heritage-tag">A09（学科建设与人才培养）</span><span '
                             'class="heritage-tag">A08（交叉研究与晚年拓展）</span><p><a '
                             'href="people/stories/index.html#stories-st05" '
                             'aria-label="阅读全文：刘超的选题：先读资料，再提出自己的方向">阅读全文 →</a></p></article>',
                      'count': 1,
                      'reason': 'shorten st05 lead; preserve stable anchor and named participants'},
                     {'old': '<article class="heritage-card" id="heritage-story-st07"><p '
                             'class="heritage-meta">交叉研究与终身学习</p><h3>进入卟啉领域，老师也和学生一起学习</h3><p '
                             'class="heritage-meta">人物：陈庆云、郭灿城、刘超</p><p>陈庆云把氟化学积累与郭灿城等人的卟啉研究基础相接。进入新领域后，他自己系统阅读、做笔记，再结合学生的实验反馈讨论问题；合作与共同学习逐步通向具体研究成果。</p><span '
                             'class="heritage-tag">A08（交叉研究与晚年拓展）</span><span '
                             'class="heritage-tag">A09（学科建设与人才培养）</span><p><a '
                             'href="people/stories/index.html#stories-st07" '
                             'aria-label="阅读全文：进入卟啉领域，老师也和学生一起学习">阅读全文 →</a></p></article>',
                      'new': '<article class="heritage-card" id="heritage-story-st07"><p '
                             'class="heritage-meta">交叉研究与终身学习</p><h3>进入卟啉领域，老师也和学生一起学习</h3><p '
                             'class="heritage-meta">人物：陈庆云、郭灿城、刘超</p><p>进入卟啉领域后，陈庆云继续读书、做笔记，与合作者和学生共同学习。</p><span '
                             'class="heritage-tag">A08（交叉研究与晚年拓展）</span><span '
                             'class="heritage-tag">A09（学科建设与人才培养）</span><p><a '
                             'href="people/stories/index.html#stories-st07" '
                             'aria-label="阅读全文：进入卟啉领域，老师也和学生一起学习">阅读全文 →</a></p></article>',
                      'count': 1,
                      'reason': 'shorten st07 lead; preserve stable anchor and named participants'},
                     {'old': '<article class="heritage-card" id="heritage-story-st14"><p '
                             'class="heritage-meta">科研写作与独立判断</p><h3>春节的一周改稿：郭勇记忆中的研究训练</h3><p '
                             'class="heritage-meta">人物：陈庆云、郭勇</p><p>郭勇回忆，学生时期一篇初稿需要修改，陈先生在春节期间花了一周审改。要求学生自己动笔，也认真承担指导责任，让论文写作成为发现问题、组织论据和解释结果的训练。</p><span '
                             'class="heritage-tag">A09（学科建设与人才培养）</span><p><a '
                             'href="people/stories/index.html#stories-st14" '
                             'aria-label="阅读全文：春节的一周改稿：郭勇记忆中的研究训练">阅读全文 →</a></p></article>',
                      'new': '<article class="heritage-card" id="heritage-story-st14"><p '
                             'class="heritage-meta">科研写作与独立判断</p><h3>春节的一周改稿：郭勇记忆中的研究训练</h3><p '
                             'class="heritage-meta">人物：陈庆云、郭勇</p><p>郭勇记忆中，陈先生曾在春节花一周改稿，让论文指导成为科研训练的一部分。</p><span '
                             'class="heritage-tag">A09（学科建设与人才培养）</span><p><a '
                             'href="people/stories/index.html#stories-st14" '
                             'aria-label="阅读全文：春节的一周改稿：郭勇记忆中的研究训练">阅读全文 →</a></p></article>',
                      'count': 1,
                      'reason': 'shorten st14 lead; preserve stable anchor and named participants'},
                     {'old': '<article class="heritage-card" id="heritage-story-st08"><p '
                             'class="heritage-meta">应用责任与后续方向</p><h3>对已有产品继续提出新问题</h3><p '
                             'class="heritage-meta">人物：陈庆云、郭勇</p><p>陈庆云晚年继续关注长链含氟表面活性剂的持久性问题，并提及郭勇的替代化学研究。应用产生的新问题，仍需后人以具体分子和实验研究继续追问。</p><span '
                             'class="heritage-tag">A04（F-53铬雾抑制剂）</span><span '
                             'class="heritage-tag">A08（交叉研究与晚年拓展）</span><p '
                             'class="heritage-locator">历史研制故事与具体结构、性能及环境评价分开，不由此宣称某替代品安全或已完成替代。</p><p><a '
                             'href="achievements/index.html#heritage-story-st08">继续阅读这则故事 '
                             '→</a></p></article>',
                      'new': '<article class="heritage-card" id="heritage-story-st08"><p '
                             'class="heritage-meta">应用责任与后续方向</p><h3>对已有产品继续提出新问题</h3><p '
                             'class="heritage-meta">人物：陈庆云、郭勇</p><p>从F-53的工业应用，读到陈先生晚年对长链含氟表面活性剂持久性和后续方向的关注。</p><span '
                             'class="heritage-tag">A04（F-53铬雾抑制剂）</span><span '
                             'class="heritage-tag">A08（交叉研究与晚年拓展）</span><p><a '
                             'href="achievements/index.html#heritage-story-st08">阅读故事与相关成果 '
                             '→</a></p></article>',
                      'count': 1,
                      'reason': 'shorten st08 lead; preserve stable anchor and named '
                                'participants'}],
 'site/achievements/index.html': [{'old': '<article class="heritage-card" '
                                          'id="heritage-story-st03"><p '
                                          'class="heritage-meta">科研与工程协作</p><h3>看见工程师和工厂的贡献</h3><p '
                                          'class="heritage-meta">人物：陈庆云、顾子恺、研究组与工厂同事</p><p>从电镀现场的铬雾问题出发，F-53研究经历路线探索、工厂试用和实验厂转化。陈庆云回忆这段工作时，特别肯定总工程师顾子恺的作用。研究组、工程人员与工厂共同完成了从样品走向生产的接续。</p><span '
                                          'class="heritage-tag">A04（F-53铬雾抑制剂）</span><p '
                                          'class="heritage-locator">工厂应用效果限于相应产品与工况。</p><p '
                                          'class="heritage-deep-entry"><a '
                                          'href="../people/stories/index.html#stories-st03">阅读全文：从实验室到实验厂：与顾子恺共同推进F-53 '
                                          '→</a></p></article>',
                                   'new': '<article class="heritage-card" '
                                          'id="heritage-story-st03"><p '
                                          'class="heritage-meta">科研与工程协作</p><h3>看见工程师和工厂的贡献</h3><p '
                                          'class="heritage-meta">人物：陈庆云、顾子恺、研究组与工厂同事</p><p>F-53从电镀现场的需求走向实验厂扩大试验，这则经历展示研究组、顾子恺等工程人员与使用单位怎样接力。</p><span '
                                          'class="heritage-tag">A04（F-53铬雾抑制剂）</span><p '
                                          'class="heritage-locator">工厂应用效果限于相应产品与工况。</p><p '
                                          'class="heritage-deep-entry"><a '
                                          'href="../people/stories/index.html#stories-st03">阅读全文：从实验室到实验厂：与顾子恺共同推进F-53 '
                                          '→</a></p></article>',
                                   'count': 1,
                                   'reason': 'shorten st03 lead; preserve stable anchor and named '
                                             'participants'},
                                  {'old': '<article class="heritage-card" '
                                          'id="heritage-story-st05"><p '
                                          'class="heritage-meta">启发式育人</p><h3>先读资料，再提出自己的方向</h3><p '
                                          'class="heritage-meta">人物：陈庆云、刘超</p><p>刘超回忆，陈庆云先给资料、介绍研究方向，再听取学生的兴趣。刘超阅读后选择含氟卟啉；从阅读走向自主选题，成为培养独立研究能力的具体经历。</p><span '
                                          'class="heritage-tag">A09（学科建设与人才培养）</span><span '
                                          'class="heritage-tag">A08（交叉研究与晚年拓展）</span><p '
                                          'class="heritage-locator">这是具名回忆中的一次研究经历，不推广为所有学生的固定流程。</p><p '
                                          'class="heritage-deep-entry"><a '
                                          'href="../people/stories/index.html#stories-st05">阅读全文：刘超的选题：先读资料，再提出自己的方向 '
                                          '→</a></p></article>',
                                   'new': '<article class="heritage-card" '
                                          'id="heritage-story-st05"><p '
                                          'class="heritage-meta">启发式育人</p><h3>先读资料，再提出自己的方向</h3><p '
                                          'class="heritage-meta">人物：陈庆云、刘超</p><p>一次选题经历呈现导师与学生怎样共同确定方向：陈先生介绍研究情况，刘超阅读资料后提出自己的兴趣。</p><span '
                                          'class="heritage-tag">A09（学科建设与人才培养）</span><span '
                                          'class="heritage-tag">A08（交叉研究与晚年拓展）</span><p '
                                          'class="heritage-locator">这是具名回忆中的一次研究经历，不推广为所有学生的固定流程。</p><p '
                                          'class="heritage-deep-entry"><a '
                                          'href="../people/stories/index.html#stories-st05">阅读全文：刘超的选题：先读资料，再提出自己的方向 '
                                          '→</a></p></article>',
                                   'count': 1,
                                   'reason': 'shorten st05 lead; preserve stable anchor and named '
                                             'participants'},
                                  {'old': '<article class="heritage-card" '
                                          'id="heritage-story-st07"><p '
                                          'class="heritage-meta">交叉研究与终身学习</p><h3>进入新领域，和学生一起学习</h3><p '
                                          'class="heritage-meta">人物：陈庆云、郭灿城、刘超</p><p>开展含氟卟啉研究时，陈庆云希望结合郭灿城的卟啉研究基础。刘超回忆，老师也系统阅读新领域文献、做笔记，并与学生讨论。跨入新方向，同时也是师生与合作者共同学习的过程。</p><span '
                                          'class="heritage-tag">A08（交叉研究与晚年拓展）</span><span '
                                          'class="heritage-tag">A09（学科建设与人才培养）</span><p '
                                          'class="heritage-locator">回忆中的文献阅读和通信呈现学习与合作，不用作独立成果评价。</p><p '
                                          'class="heritage-deep-entry"><a '
                                          'href="../people/stories/index.html#stories-st07">阅读全文：进入卟啉领域，老师也和学生一起学习 '
                                          '→</a></p></article>',
                                   'new': '<article class="heritage-card" '
                                          'id="heritage-story-st07"><p '
                                          'class="heritage-meta">交叉研究与终身学习</p><h3>进入新领域，和学生一起学习</h3><p '
                                          'class="heritage-meta">人物：陈庆云、郭灿城、刘超</p><p>氟化学与卟啉研究经验在合作中相接，刘超的回忆还记录了陈先生系统阅读新领域资料的习惯。</p><span '
                                          'class="heritage-tag">A08（交叉研究与晚年拓展）</span><span '
                                          'class="heritage-tag">A09（学科建设与人才培养）</span><p '
                                          'class="heritage-locator">回忆中的文献阅读和通信呈现学习与合作，不用作独立成果评价。</p><p '
                                          'class="heritage-deep-entry"><a '
                                          'href="../people/stories/index.html#stories-st07">阅读全文：进入卟啉领域，老师也和学生一起学习 '
                                          '→</a></p></article>',
                                   'count': 1,
                                   'reason': 'shorten st07 lead; preserve stable anchor and named '
                                             'participants'},
                                  {'old': '<article class="heritage-card" '
                                          'id="heritage-story-st09"><p '
                                          'class="heritage-meta">材料开拓与分工协作</p><h3>先补单体与分离环节，再推进材料</h3><p '
                                          'class="heritage-meta">人物：陈庆云、蒋锡夔、胡亚东、氟橡胶课题组同事</p><p>蒋锡夔、胡亚东带领的团队已有氟橡胶1号前期成果。陈庆云加入后，继续探索六氟丙烯的制取与低温分离；自制仪器、原料保障和实验操作由不同同事协作，使单体研究接续到材料工作。</p><span '
                                          'class="heritage-tag">A02（含氟单体、氟橡胶与氟油）</span><p '
                                          'class="heritage-locator">氟橡胶1号是陈先生加入前的工作，与他后来参与的研究分别归属。</p><p '
                                          'class="heritage-deep-entry"><a '
                                          'href="../people/stories/index.html#stories-st09">阅读全文：把少量六氟丙烯变成可用单体 '
                                          '→</a></p></article>',
                                   'new': '<article class="heritage-card" '
                                          'id="heritage-story-st09"><p '
                                          'class="heritage-meta">材料开拓与分工协作</p><h3>先补单体与分离环节，再推进材料</h3><p '
                                          'class="heritage-meta">人物：陈庆云、蒋锡夔、胡亚东、氟橡胶课题组同事</p><p>团队已有氟橡胶1号前期成果，陈庆云加入后参与六氟丙烯制取与低温分离，为后续材料研究接续原料环节。</p><span '
                                          'class="heritage-tag">A02（含氟单体、氟橡胶与氟油）</span><p '
                                          'class="heritage-locator">氟橡胶1号是陈先生加入前的工作，与他后来参与的研究分别归属。</p><p '
                                          'class="heritage-deep-entry"><a '
                                          'href="../people/stories/index.html#stories-st09">阅读全文：把少量六氟丙烯变成可用单体 '
                                          '→</a></p></article>',
                                   'count': 1,
                                   'reason': 'shorten st09 lead; preserve stable anchor and named '
                                             'participants'},
                                  {'old': '<article class="heritage-card" '
                                          'id="heritage-story-st10"><p '
                                          'class="heritage-meta">中试接力与跨单位合作</p><h3>制冷剂合成之后，还要让工艺和整机接得上</h3><p '
                                          'class="heritage-meta">人物：陈庆云、林永达、杨映松、上海有机所实验厂、嘉兴冰箱厂、广州化学所</p><p>在HFC-134a研究中，林永达、杨映松接续实验室工作，参加实验厂的扩大生产和连续中试。陈庆云与林永达研究配套冷冻机油，并与嘉兴冰箱厂、广州化学所等协作，把分子合成、工艺、润滑油相容性和整机试用连接起来。</p><span '
                                          'class="heritage-tag">A05（制冷剂与配套技术）</span><p '
                                          'class="heritage-locator">连续中试规模不等同年产量；历史材料中的“HCFC-134a”写法，与具体物质HFC-134a分别辨认。</p><p '
                                          'class="heritage-deep-entry"><a '
                                          'href="../people/stories/index.html#stories-st10">阅读全文：把制冷剂、润滑油与冰箱接起来 '
                                          '→</a></p></article>',
                                   'new': '<article class="heritage-card" '
                                          'id="heritage-story-st10"><p '
                                          'class="heritage-meta">中试接力与跨单位合作</p><h3>制冷剂合成之后，还要让工艺和整机接得上</h3><p '
                                          'class="heritage-meta">人物：陈庆云、林永达、杨映松、上海有机所实验厂、嘉兴冰箱厂、广州化学所</p><p>HFC-134a的研究经历合成、中试和配套应用，各环节由研究人员、实验厂及合作单位共同推进。</p><span '
                                          'class="heritage-tag">A05（制冷剂与配套技术）</span><p '
                                          'class="heritage-locator">连续中试规模不等同年产量；历史材料中的“HCFC-134a”写法，与具体物质HFC-134a分别辨认。</p><p '
                                          'class="heritage-deep-entry"><a '
                                          'href="../people/stories/index.html#stories-st10">阅读全文：把制冷剂、润滑油与冰箱接起来 '
                                          '→</a></p></article>',
                                   'count': 1,
                                   'reason': 'shorten st10 lead; preserve stable anchor and named '
                                             'participants'},
                                  {'old': '<article class="heritage-card" '
                                          'id="heritage-story-st14"><p '
                                          'class="heritage-meta">科研写作与独立判断</p><h3>把写论文当成再检查一次实验</h3><p '
                                          'class="heritage-meta">人物：陈庆云、郭勇</p><p>陈庆云让学生自己写论文，因为组织论证时发现的问题可能同时关乎表达和实验。郭勇回忆，一篇初稿曾让老师在春节期间修改了一周。反复写作与讨论，也是检查研究、训练独立判断的过程。</p><span '
                                          'class="heritage-tag">A09（学科建设与人才培养）</span><p '
                                          'class="heritage-locator">具名回忆呈现导师改稿的投入，不替代对某篇论文质量的独立评价。</p><p '
                                          'class="heritage-deep-entry"><a '
                                          'href="../people/stories/index.html#stories-st14">阅读全文：春节的一周改稿：郭勇记忆中的研究训练 '
                                          '→</a></p></article>',
                                   'new': '<article class="heritage-card" '
                                          'id="heritage-story-st14"><p '
                                          'class="heritage-meta">科研写作与独立判断</p><h3>把写论文当成再检查一次实验</h3><p '
                                          'class="heritage-meta">人物：陈庆云、郭勇</p><p>要求学生自己写稿，同时在困难处给予具体修改指导，体现陈先生对独立研究能力和论文质量的重视。</p><span '
                                          'class="heritage-tag">A09（学科建设与人才培养）</span><p '
                                          'class="heritage-locator">具名回忆呈现导师改稿的投入，不替代对某篇论文质量的独立评价。</p><p '
                                          'class="heritage-deep-entry"><a '
                                          'href="../people/stories/index.html#stories-st14">阅读全文：春节的一周改稿：郭勇记忆中的研究训练 '
                                          '→</a></p></article>',
                                   'count': 1,
                                   'reason': 'shorten st14 lead; preserve stable anchor and named '
                                             'participants'},
                                  {'old': '<article class="heritage-card" '
                                          'id="heritage-story-st08"><p '
                                          'class="heritage-meta">应用责任与后续方向</p><h3>对已有产品继续提出新问题</h3><p '
                                          'class="heritage-meta">人物：陈庆云、郭勇</p><p>陈庆云晚年继续关注长链含氟表面活性剂的持久性问题，并提及郭勇的替代化学研究。应用产生的新问题，仍需后人以具体分子和实验研究继续追问。</p><span '
                                          'class="heritage-tag">A04（F-53铬雾抑制剂）</span><span '
                                          'class="heritage-tag">A08（交叉研究与晚年拓展）</span><p '
                                          'class="heritage-locator">历史研制故事与具体结构、性能及环境评价分开，不由此宣称某替代品安全或已完成替代。</p></article>',
                                   'new': '<article class="heritage-card" '
                                          'id="heritage-story-st08"><p '
                                          'class="heritage-meta">应用责任与后续方向</p><h3>对已有产品继续提出新问题</h3><p '
                                          'class="heritage-meta">人物：陈庆云、郭勇</p><p>陈庆云晚年继续关注长链含氟表面活性剂的持久性问题，并提及郭勇的替代化学研究。应用产生的新问题，仍需后人以具体分子和实验研究继续追问。</p><span '
                                          'class="heritage-tag">A04（F-53铬雾抑制剂）</span><span '
                                          'class="heritage-tag">A08（交叉研究与晚年拓展）</span><p '
                                          'class="heritage-locator">历史研制故事与具体结构、性能及环境评价分开，不由此宣称某替代品安全或已完成替代。</p><p '
                                          'class="heritage-deep-entry"><a '
                                          'href="../topics/f53/index.html#record-industrial-application">A04（F-53铬雾抑制剂）：历史工业应用 '
                                          '→</a> · <a '
                                          'href="../topics/sulfonyl-fluoride/index.html#record-late-functional-groups">A08（交叉研究与晚年拓展）：晚年方法与表面活性分子 '
                                          '→</a></p></article>',
                                   'count': 1,
                                   'reason': 'ST08 retains its sole full account and gains '
                                             'relevant scientific reading'},
                                  {'old': '<p>氟磺酰基二氟乙酸甲酯（MFSDA）被称为“陈试剂”。1989年，陈庆云与吴生文报道其在碘化亚铜体系中的三氟甲基化用途，使该试剂成为向有机分子引入–CF₃的合成工具。</p>',
                                   'new': '<p>“陈试剂”是A06（磺酸酯、二氟卡宾与三氟甲基化）中由反应研究发展为合成工具的代表成果；其甲酯身份、1989年共同工作及后来的研究接续，可在专题中阅读。</p>',
                                   'count': 1,
                                   'reason': 'summary feature is a concise scientific entry rather '
                                             'than copied homepage text'}],
 'site/research/index.html': [{'old': '<p>历史实验与理论研究归原作者。以下呈现平台完成的原文、表格和附件对照，保持 '
                                      '<code>review_required</code>、<code>release_eligible=false</code>；文献核校不授予实验、结构或机理验证资格。</p>',
                               'new': '',
                               'count': 7,
                               'reason': 'remove seven repeated common collation notices; keep all '
                                         'individual result limits'},
                              {'old': '<p>平台新增释读与分析保持待科学审阅；这一状态不作为陈庆云院士及合作者历史成果成立的前提。</p>',
                               'new': '<p '
                                      'id="ai-collation-scope">历史实验与理论研究归原作者。以下呈现平台完成的原文、表格和附件对照，保持 '
                                      '<code>review_required</code>、<code>release_eligible=false</code>；文献核校不授予实验、结构或机理验证资格。这一状态不作为陈庆云院士及合作者历史成果成立的前提。</p>',
                               'count': 1,
                               'reason': 'place shared historical attribution and review boundary '
                                         'once in page introduction'}]}
SHARED_RESEARCH_NOTICE = '<p id="ai-collation-scope">历史实验与理论研究归原作者。以下呈现平台完成的原文、表格和附件对照，保持 <code>review_required</code>、<code>release_eligible=false</code>；文献核校不授予实验、结构或机理验证资格。这一状态不作为陈庆云院士及合作者历史成果成立的前提。</p>'
# SITE_DEDUPLICATION_FROZEN_CONSTANTS:END

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}

_CACHE: dict[str, Path] = {}
_LEGACY_CACHE: dict[tuple, tuple] = {}
_TEMPORARIES: list[tuple[Path, Path]] = []


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _identity(value: bytes) -> tuple[str, int]:
    return _sha(value), len(value)


def _file(root: Path, name: str) -> Path:
    relative = PurePosixPath(name)
    candidate = root/name
    if (not name or relative.is_absolute() or '..' in relative.parts
            or '\\' in name or relative.as_posix() != name
            or candidate.is_symlink() or not candidate.is_file()
            or not candidate.resolve().is_relative_to(root.resolve())):
        raise ValueError('Unsafe or missing lifespan publication file: '+str(name))
    return candidate


def _binding(root: Path, name: str) -> dict:
    value = _file(root, name).read_bytes()
    return {'path': name, 'sha256': _sha(value), 'bytes': len(value)}


def _records(data: dict) -> tuple[dict, list]:
    rows, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if (not isinstance(rows, list) or len(rows) != len(CHANGED_FILES)
            or any(not isinstance(row, dict) for row in rows)
            or {row.get('path') for row in rows} != set(CHANGED_FILES)
            or not isinstance(pool, list) or not pool):
        raise ValueError('Site deduplication requires exactly one homepage HTML and two integration edits')
    for pair in pool:
        if (not isinstance(pair, dict) or set(pair) != {'old', 'new'}
                or any(not isinstance(pair[key], str) for key in ('old', 'new'))
                or pair['old'] == pair['new']):
            raise ValueError('Invalid lifespan reverse replacement pool')
    indexed, used = {}, set()
    for row in rows:
        if (set(row) != {'path', 'old_sha256', 'old_bytes', 'new_sha256', 'new_bytes', 'edits'}
                or any(type(row[key]) is not int or row[key] <= 0 for key in ('old_bytes', 'new_bytes'))
                or any(not isinstance(row[key], str) or not re.fullmatch('[0-9a-f]{64}', row[key])
                       for key in ('old_sha256', 'new_sha256'))
                or not isinstance(row['edits'], list) or not row['edits']):
            raise ValueError('Incomplete lifespan old/new identity')
        for edit in row['edits']:
            if (not isinstance(edit, dict) or set(edit) != {'old_offset', 'replacement'}
                    or type(edit['old_offset']) is not int or edit['old_offset'] < 0
                    or type(edit['replacement']) is not int
                    or not 0 <= edit['replacement'] < len(pool)):
                raise ValueError('Invalid exact lifespan reverse edit')
            used.add(edit['replacement'])
        indexed[row['path']] = row
    if used != set(range(len(pool))):
        raise ValueError('lifespan replacement pool contains unused entries')
    return indexed, pool


def _reconstruct(current: bytes, row: dict, pool: list) -> bytes:
    if _identity(current) != (row['new_sha256'], row['new_bytes']):
        raise ValueError('lifespan current identity changed: '+row['path'])
    parts, cursor, old_end, delta = [], 0, 0, 0
    for edit in row['edits']:
        offset = edit['old_offset']
        pair = pool[edit['replacement']]
        before, after = pair['old'].encode('utf-8'), pair['new'].encode('utf-8')
        position = offset+delta
        if (offset < old_end or offset+len(before) > row['old_bytes']
                or position < cursor or position+len(after) > len(current)
                or current[position:position+len(after)] != after):
            raise ValueError('lifespan reverse edit differs at exact offset: '+row['path'])
        parts.extend((current[cursor:position], before))
        cursor, old_end = position+len(after), offset+len(before)
        delta += len(after)-len(before)
    rebuilt = b''.join((*parts, current[cursor:]))
    if _identity(rebuilt) != (row['old_sha256'], row['old_bytes']):
        raise ValueError('lifespan 44cf595 reconstruction failed: '+row['path'])
    return rebuilt



def _check_integrations(root: Path, indexed: dict, pool: list) -> None:
    name = INTEGRATIONS[0]
    current = _file(root, name).read_bytes()
    original = _reconstruct(current, indexed[name], pool)
    before, after = ast.parse(original), ast.parse(current)
    mapping = {'effective_website_entries': '_effective_website_entries_v45',
               'publication_members': '_publication_members_v45'}
    wrappers = {'effective_website_entries': ENTRY_WRAPPER, 'publication_members': MEMBERS_WRAPPER}
    for old_name, helper_name in mapping.items():
        old = [node for node in before.body if isinstance(node, ast.FunctionDef) and node.name == old_name]
        helpers = [node for node in after.body if isinstance(node, ast.FunctionDef) and node.name == helper_name]
        public = [node for node in after.body if isinstance(node, ast.FunctionDef) and node.name == old_name]
        if len(old) != 1 or len(helpers) != 1 or len(public) != 1:
            raise ValueError('Missing fixed lifespan integration function: '+old_name)
        restored = deepcopy(helpers[0])
        restored.name = old_name
        if ast.dump(old[0], include_attributes=False) != ast.dump(restored, include_attributes=False):
            raise ValueError('Lifespan integration changed complete v45 function: '+old_name)
        if ast.dump(public[0], include_attributes=False) != ast.dump(ast.parse(wrappers[old_name]).body[0], include_attributes=False):
            raise ValueError('Lifespan integration exceeds its fixed wrapper: '+old_name)
    normalized = deepcopy(after)
    normalized.body = [node for node in normalized.body if not (isinstance(node, ast.FunctionDef) and node.name in mapping)]
    for node in normalized.body:
        if isinstance(node, ast.FunctionDef) and node.name in mapping.values():
            node.name = next(name for name, helper in mapping.items() if helper == node.name)
    if ast.dump(before, include_attributes=False) != ast.dump(normalized, include_attributes=False):
        raise ValueError('Lifespan integration changed contract code outside the two fixed wrappers')
    name = INTEGRATIONS[1]
    current = _file(root, name).read_bytes()
    original = _reconstruct(current, indexed[name], pool)
    old = b'from home_stories_deepening_publication import historical_root'
    new = b'from site_deduplication_publication import historical_root'
    if original.count(old) != 1 or original.replace(old, new, 1) != current:
        raise ValueError('Lifespan checker may only replace the historical-root import')


class _DOM(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source, self.nodes, self.stack = source, [], []
        self.lines = [0]+[match.end() for match in re.finditer('\n', source)]
        self.feed(source)

    def position(self):
        line, column = self.getpos()
        return self.lines[line-1]+column

    def handle_starttag(self, tag, attrs):
        node = {'tag': tag, 'attrs': dict(attrs), 'start': self.position(), 'end': None,
                'parent': self.stack[-1] if self.stack else None}
        self.nodes.append(node)
        if tag in VOID:
            node['end'] = self.position()+len(self.get_starttag_text())
        else:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for index in range(len(self.stack)-1, -1, -1):
            if self.stack[index]['tag'] == tag:
                end = self.source.index('>', self.position())+1
                for node in self.stack[index:]:
                    node['end'] = end
                self.stack = self.stack[:index]
                break

    def raw(self, node):
        if node['end'] is None:
            raise ValueError('Unclosed element')
        return self.source[node['start']:node['end']]

    def by_id(self, ident):
        matches = [node for node in self.nodes if node['attrs'].get('id') == ident]
        if len(matches) != 1:
            raise ValueError('Missing or duplicate ID: '+ident)
        return matches[0]




def _validate_deduplication_policy() -> None:
    if not isinstance(APPROVED_EDITS, dict) or set(APPROVED_EDITS) != {'site/'+route for route in ROUTES}:
        raise ValueError('Deduplication requires exactly the three approved HTML paths')
    for rows in APPROVED_EDITS.values():
        if not isinstance(rows, list) or not rows:
            raise ValueError('Each approved page needs finite exact edits')
        for row in rows:
            if (not isinstance(row, dict) or set(row) != {'old', 'new', 'count', 'reason'}
                    or any(not isinstance(row[key], str) for key in ('old', 'new', 'reason'))
                    or not row['old'] or not row['reason'].strip() or row['old'] == row['new']
                    or type(row['count']) is not int or row['count'] <= 0):
                raise ValueError('Invalid exact approved deduplication operation')
    if not isinstance(SHARED_RESEARCH_NOTICE, str) or not SHARED_RESEARCH_NOTICE:
        raise ValueError('The one shared research notice must be explicitly reviewed')


class _VisibleText(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.hidden, self.parts = 0, []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag in ('script', 'style') and self.hidden:
            self.hidden -= 1

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def _numbers(source):
    return Counter(re.findall(r'(?<![A-Za-z0-9_])[-−+]?\d+(?:[.,]\d+)*(?:[eE][-+]?\d+)?',
                              '\n'.join(_VisibleText(source).parts)))


def _state_attributes(parsed):
    values = []
    for node in parsed.nodes:
        attrs = tuple(sorted((key, value) for key, value in node['attrs'].items()
                     if key.startswith(('data-', 'aria-')) or key in ('class', 'role', 'hidden', 'open', 'disabled')))
        if attrs:
            values.append((node['tag'], attrs))
    return Counter(values)


def _check_html(route: str, before: bytes, after: bytes) -> None:
    _validate_deduplication_policy()
    old, new = before.decode('utf-8'), after.decode('utf-8')
    expected = old
    for row in APPROVED_EDITS['site/'+route]:
        if expected.count(row['old']) != row['count']:
            raise ValueError('Reviewed deduplication snippet count changed: '+row['reason'])
        expected = expected.replace(row['old'], row['new'], row['count'])
    if expected != new:
        raise ValueError('HTML differs outside the exact approved deduplication operations: '+route)
    previous, current = _DOM(old), _DOM(new)
    old_ids = [node['attrs']['id'] for node in previous.nodes if node['attrs'].get('id')]
    new_ids = [node['attrs']['id'] for node in current.nodes if node['attrs'].get('id')]
    if not set(old_ids).issubset(new_ids) or len(new_ids) != len(set(new_ids)):
        raise ValueError('Deduplication lost or duplicated a prior anchor: '+route)
    for tag in ('script', 'style'):
        pattern = r'<'+tag+r'\b[^>]*>.*?</'+tag+r'\s*>'
        if re.findall(pattern, old, re.I|re.S) != re.findall(pattern, new, re.I|re.S):
            raise ValueError('Deduplication changed original '+tag+' bytes: '+route)
    for tag in ('svg', 'table', 'canvas'):
        pattern = r'<'+tag+r'\b[^>]*>.*?</'+tag+r'\s*>'
        if Counter(re.findall(pattern, old, re.I|re.S)) != Counter(re.findall(pattern, new, re.I|re.S)):
            raise ValueError('Deduplication changed a scientific '+tag+': '+route)
    if Counter(re.findall(r'<img\b[^>]*>', old, re.I|re.S)) != Counter(re.findall(r'<img\b[^>]*>', new, re.I|re.S)):
        raise ValueError('Deduplication changed an image: '+route)
    if route in ('index.html', 'achievements/index.html'):
        hrefs = lambda parsed: Counter(node['attrs']['href'] for node in parsed.nodes
            if node['tag'] == 'a' and 'people/stories/index.html#stories-st' in node['attrs'].get('href', ''))
        if hrefs(previous) != hrefs(current):
            raise ValueError('The six canonical story reading links must remain exact: '+route)
    if route == 'index.html':
        for ident in ('top', 'home-portrait', 'home-portrait-style', 'people', 'chen-reagent-achievement',
                      'achievement-lines-preview', 'achievement-detail', 'overview'):
            if previous.raw(previous.by_id(ident)) != current.raw(current.by_id(ident)):
                raise ValueError('Deduplication changed a protected home block: '+ident)
    if route == 'research/index.html':
        blocks = lambda parsed: [parsed.raw(node) for node in parsed.nodes
                                if 'result-evidence' in node['attrs'].get('class', '').split()]
        if not blocks(previous) or blocks(previous) != blocks(current):
            raise ValueError('Research result-evidence blocks must retain their exact bytes and order')
        if _numbers(old) != _numbers(new):
            raise ValueError('Research visible numeric data changed')
        if _state_attributes(previous) != _state_attributes(current):
            raise ValueError('Research status/role/data/aria attributes changed')
        if new.count(SHARED_RESEARCH_NOTICE) != 1 or current.raw(current.by_id('ai-collation-scope')) != SHARED_RESEARCH_NOTICE:
            raise ValueError('Research must retain the one exact shared introduction notice')
    if re.search(r'private-sources|current-item-register|file://|[CD]:[\\/]', new, re.I):
        raise ValueError('Private evidence/tracking paths entered deduplication HTML')

def _validated_data(root: Path) -> tuple[dict, dict, list]:
    if (not FROZEN or len(PREDECESSOR_FILES) != 645
            or set(REVIEWED_FILES) != set(CHANGED_FILES)):
        raise ValueError('Site deduplication v46 has not been frozen')
    _validate_deduplication_policy()
    data = json.loads(_file(root, MANIFEST).read_bytes())
    required = {
        'schema_version': '46.0', 'presentation_id': PRESENTATION_ID,
        'publication_kind': 'platform_site_deduplication',
        'previous_presentation_commit': PREVIOUS_COMMIT,
        'previous_presentation': {'path': PREVIOUS_MANIFEST, 'sha256': PREDECESSOR_FILES[PREVIOUS_MANIFEST][0]},
        'allowed_html_paths': list(ROUTES), 'added_html_paths': [],
        'allowed_integration_paths': list(INTEGRATIONS), 'allowed_new_files': list(NEW_FILES),
        'reconstruction_kind': 'deduplicated_exact_utf8_text_edits',
        'predecessor_files': {name: {'sha256': value[0], 'bytes': value[1]}
                              for name, value in PREDECESSOR_FILES.items()},
        'publication_module': _binding(root, NEW_FILES[0]),
        'approved_HTML_edits': APPROVED_EDITS, 'shared_research_notice': SHARED_RESEARCH_NOTICE,
        'scientific_review_status': 'review_required', 'release_eligible': False,
        'scientific_data_unchanged': True, 'historical_achievement_independent_of_AI_review': True,
        'M0_resumed': False, 'Nemotron_training_resumed': False,
        'new_quantum_calls': 0, 'new_model_API_calls': 0, 'new_model_training_runs': 0,
    }
    extras = {'authorization', 'reversible_text_files', 'reverse_text_patch_pool', 'change_reason'}
    if (not isinstance(data, dict) or set(data) != set(required)|extras
            or any(data.get(key) != value or type(data.get(key)) is not type(value)
                   for key, value in required.items())
            or any(not isinstance(data.get(key), str) or not data[key].strip()
                   for key in ('authorization', 'change_reason'))):
        raise ValueError('Unsupported bounded Site deduplication v46 manifest')
    indexed, pool = _records(data)
    for name, expected in PREDECESSOR_FILES.items():
        current = _file(root, name).read_bytes()
        if name in indexed:
            row = indexed[name]
            if ((row['old_sha256'], row['old_bytes']) != expected
                    or (row['new_sha256'], row['new_bytes']) != REVIEWED_FILES[name]):
                raise ValueError('Site deduplication differs from frozen reviewed identity: '+name)
            restored = _reconstruct(current, row, pool)
            if name.startswith('site/'):
                _check_html(name[5:], restored, current)
        elif _identity(current) != expected:
            raise ValueError('Site deduplication changed a protected v45 member: '+name)
    _check_integrations(root, indexed, pool)
    actual = tuple(sorted(path.relative_to(root/'site').as_posix()
                         for path in (root/'site').rglob('*') if path.is_file() or path.is_symlink()))
    expected = tuple(sorted(name[5:] for name in PREDECESSOR_FILES if name.startswith('site/')))
    if actual != expected:
        raise ValueError('Site deduplication cannot add or remove website members')
    return data, indexed, pool


def _cleanup() -> None:
    for parent, path in reversed(_TEMPORARIES):
        target = path.resolve()
        if target.parent != parent.resolve() or not target.name.startswith('du46-') or path.is_symlink():
            continue
        if target.exists():
            shutil.rmtree(target)
    _TEMPORARIES.clear()
    _CACHE.clear()
    _LEGACY_CACHE.clear()


atexit.register(_cleanup)


def projection_root(root: Path) -> Path:
    """Validate current bytes and reconstruct all 645 exact v45 data members."""
    root = root.resolve()
    _, indexed, pool = _validated_data(root)
    key = str(root)+'|'+_sha(_file(root, MANIFEST).read_bytes())
    if key in _CACHE and _CACHE[key].is_dir():
        for name, expected in PREDECESSOR_FILES.items():
            if _identity(_file(_CACHE[key], name).read_bytes()) != expected:
                raise ValueError('Cached Site deduplication predecessor projection changed: '+name)
        return _CACHE[key]
    parent = root.parent
    target = Path(tempfile.mkdtemp(prefix='du46-', dir=parent))
    _TEMPORARIES.append((parent, target))
    if max(len(str(target/name)) for name in PREDECESSOR_FILES) > 250:
        raise ValueError('Site deduplication projection path exceeds the verified limit')
    for name, expected in PREDECESSOR_FILES.items():
        value = _file(root, name).read_bytes()
        if name in indexed:
            value = _reconstruct(value, indexed[name], pool)
        if _identity(value) != expected:
            raise ValueError('Site deduplication projection differs from exact 44cf595: '+name)
        destination = target/name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(value)
    if (target/MANIFEST).exists():
        raise ValueError('An exact v45 projection cannot contain v46 manifest')
    _CACHE[key] = target
    return target


def historical_root(root: Path) -> Path:
    from home_stories_deepening_publication import historical_root as v45_historical_root
    predecessor = projection_root(root) if (root/MANIFEST).is_file() else root
    return v45_historical_root(predecessor)


def _legacy_entries(root: Path, baseline: dict, callback, arguments: dict) -> tuple:
    predecessor = projection_root(root)
    if baseline != json.loads(_file(predecessor, 'provenance/website-baseline.json').read_bytes()):
        raise ValueError('Site deduplication baseline differs from the immutable full baseline')
    key = (str(predecessor), _sha(json.dumps(baseline, sort_keys=True, separators=(',', ':')).encode()),
           _sha(json.dumps(arguments, sort_keys=True, separators=(',', ':')).encode()), callback)
    if key not in _LEGACY_CACHE:
        _LEGACY_CACHE[key] = deepcopy(callback(predecessor, deepcopy(baseline), **deepcopy(arguments)))
    entries, report = deepcopy(_LEGACY_CACHE[key])
    return predecessor, entries, report


def apply(root: Path, baseline: dict, callback, *, verify_current=True,
          revision_chain=None, include_presentation=True) -> tuple[dict, dict]:
    predecessor, entries, previous = _legacy_entries(root, baseline, callback,
        {'verify_current': verify_current, 'revision_chain': revision_chain,
         'include_presentation': include_presentation})
    if not include_presentation:
        return entries, previous
    updated = deepcopy(entries)
    for route in ROUTES:
        before, after = _file(predecessor, 'site/'+route).read_bytes(), _file(root, 'site/'+route).read_bytes()
        if (entries[route]['sha256'], entries[route]['bytes']) != _identity(before):
            raise ValueError('Deduplication does not continue the complete v45 member: '+route)
        _check_html(route, before, after)
        updated[route] = {**updated[route], 'sha256': _sha(after), 'bytes': len(after), 'presentation_id': PRESENTATION_ID}
    for name, row in updated.items():
        if _identity(_file(root, 'site/'+name).read_bytes()) != (row['sha256'], row['bytes']):
            raise ValueError('Site deduplication changed an unlisted website member: '+name)
    earlier = previous.get('presentation') or {}
    report = {
        'path': MANIFEST, 'sha256': _sha(_file(root, MANIFEST).read_bytes()),
        'presentation_id': PRESENTATION_ID, 'publication_kind': 'platform_site_deduplication',
        'changed_paths': list(ROUTES), 'added_paths': [], 'previous_presentation_commit': PREVIOUS_COMMIT,
        'exact_v45_projection': True, 'all_v1_v45_checks_replayed': True,
        'exact_approved_deduplication_operations_only': True,
        'research_evidence_tables_numeric_data_and_state_attributes_preserved': True,
        'scientific_review_status': 'review_required', 'release_eligible': False,
        'scientific_data_unchanged': True, 'historical_achievement_independent_of_AI_review': True,
        'M0_resumed': False, 'Nemotron_training_resumed': False,
    }
    return updated, {**previous, 'changed_paths': sorted(set(previous.get('changed_paths', []))|set(ROUTES)),
        'presentation': {**report, 'presentation_chain': [*earlier.get('presentation_chain', []), report]}}


ENTRY_WRAPPER = '''def effective_website_entries(root: Path, baseline: dict, *, verify_current=True,
                              revision_chain=None, include_presentation=True) -> tuple[dict, dict]:
    """Replay the complete v45 chain before the bounded Site deduplication fix."""
    arguments = {'verify_current': verify_current, 'revision_chain': revision_chain,
                 'include_presentation': include_presentation}
    if (root/'provenance/platform-presentation.v46.json').is_file():
        from site_deduplication_publication import apply
        return apply(root, baseline, _effective_website_entries_v45, **arguments)
    return _effective_website_entries_v45(root, baseline, **arguments)
'''

def publication_members(root: Path, entries: dict, callback) -> list[dict]:
    """Delegate the unchanged 22-member allowlist through the exact v45 view."""
    predecessor = projection_root(root)
    members = callback(predecessor, deepcopy(entries))
    if (len(members) != 22 or len({row['path'] for row in members}) != 22
            or any(row != entries.get(row['path']) for row in members)):
        raise ValueError('Site deduplicationting must preserve all 22 prior publication members')
    return members


MEMBERS_WRAPPER = '''def publication_members(root: Path, entries: dict) -> list[dict]:
    """Use the exact v45 view while retaining the complete existing allowlist."""
    if (root/'provenance/platform-presentation.v46.json').is_file():
        from site_deduplication_publication import publication_members as lifespan_publication_members
        return lifespan_publication_members(root, entries, _publication_members_v45)
    return _publication_members_v45(root, entries)
'''
