# Local WSL 2 tests, not distributed test sources

The captured command actually ran 81 tests under Ubuntu-24.04 / WSL 2 and
completed successfully, with no skips. Execution metadata identifies source
commit `c7aed91e9d553a45fb1a13752d0fa61cd68a8106`; the only concurrent source-tree
edit was the website contract documentation. Python source bytes were frozen.

The test files remain ignored on this local machine and are not published.
These logs are evidence of this local run, not evidence that GitHub CI ran 81
tests. Distributed-source CI deliberately runs zero unit tests. The original
ZIP's separate nine-test run is recorded by the formal WSL acceptance wrapper.
