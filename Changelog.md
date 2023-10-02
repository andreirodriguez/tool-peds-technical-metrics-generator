# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added Readme file
  - Insert instruction to recreate project and process
- path_utils.py
- Changelog

### Fixed

- Exclude idea files into .gitignore
- Directories path in function of O.S.
- Remove speciality for survey

```js
    "input/cr/" + self.specialty + "survey" + self.process_month + ".csv",
    input_cr_survey = get_root_dir(["../../input/cr/", "survey", self.process_month, ".csv"])
```

[unreleased]: https://github.com/olivierlacan/keep-a-changelog/compare/v1.1.0...HEAD