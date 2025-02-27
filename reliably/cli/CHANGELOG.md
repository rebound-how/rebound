# Changelog

## [Unreleased][]

[Unreleased]: https://github.com/reliablyhq/cli/compare/0.28.1...HEAD

## [0.28.1][]

[0.28.1]: https://github.com/reliablyhq/cli/compare/0.28.0...0.28.1

### Changed

* Use Python 3.12 in Dockerfile

## [0.28.0][]

[0.28.0]: https://github.com/reliablyhq/cli/compare/0.27.0...0.28.0

### Changed

* Bump dependencies

## [0.27.0][]

[0.27.0]: https://github.com/reliablyhq/cli/compare/0.26.0...0.27.0

### Changed

* Bump dependencies

## [0.26.0][]

[0.26.0]: https://github.com/reliablyhq/cli/compare/0.25.2...0.26.0

### Added

* The `reliably snapshot scout` commands to discover and return snapshots of
  system resources back to Reliably to populate the builder

### Fixed

* Command `config init` as it failed if config didn't already exist

### Changed

* Bump dependencies
* Adjusted for chaostoolkit-lib 1.42.0 changes around logging

## [0.25.2][]

[0.25.2]: https://github.com/reliablyhq/cli/compare/0.25.1...0.25.2

### Fixed

* Add missing settings.yaml file

## [0.25.1][]

[0.25.1]: https://github.com/reliablyhq/cli/compare/0.25.0...0.25.1

### Fixed

* Dockerfile for full image

## [0.25.0][]

[0.25.0]: https://github.com/reliablyhq/cli/compare/0.24.0...0.25.0

### Added

* Import into starter library your own extensions for easily building new
  experiments
* Also build a container image with most major Chaos Toolkit extensions, ready
  to be used by Reliably plans

### Changed

* Bump dependencies

## [0.24.0][]

[0.24.0]: https://github.com/reliablyhq/cli/compare/0.23.0...0.24.0

### Fixed

* Respect the runtime strategy for the hypothesis when it is
  `"during-method-only"` [#11][11]

[11]: https://github.com/reliablyhq/cli/issues/11

### Changed

* Bump dependencies

## [0.23.0][]

[0.23.0]: https://github.com/reliablyhq/cli/compare/0.22.0...0.23.0

### Changed

* Bump dependencies
* Use `RELIABLY_CATCH_SIGTERM_BEFORE_CHAOSTOOLKIT` to catch `SIGTERM` first
  before the Chaos Toolkit has a chance. This is useful because by default the
  CTK waits for pending activities before fully terminating when receiving
  that signal. However, in some cases, such as a non-tty environment, there
  is no second signal to force the termination and therefore the process
  hangs and the plan isn't terminated properly.

## [0.22.0][]

[0.22.0]: https://github.com/reliablyhq/cli/compare/0.21.0...0.22.0

### Changed

* Bump dependencies

## [0.21.0][]

[0.21.0]: https://github.com/reliablyhq/cli/compare/0.20.0...0.21.0

### Changed

* Bump dependencies

## [0.20.0][]

[0.20.0]: https://github.com/reliablyhq/cli/compare/0.19.0...0.20.0

### Fixed

* Method call from pydantic v2 changed to `model_dump_json`

### Changed

* Bump dependencies
* Set exit code of `reliably service plan execute` to match the status
  of the experiment: `0` when it completed, `1` when it deviated and `2`
  otherwise

## [0.19.0][]

[0.19.0]: https://github.com/reliablyhq/cli/compare/0.18.0...0.19.0

### Changed

* Bump dependencies

## [0.18.0][]

[0.18.0]: https://github.com/reliablyhq/cli/compare/0.17.0...0.18.0

### Changed

* Bump dependencies

## [0.17.0][]

[0.17.0]: https://github.com/reliablyhq/cli/compare/0.16.1...0.17.0

### Changed

* Bump dependencies

## [0.16.1][]

[0.16.1]: https://github.com/reliablyhq/cli/compare/0.16.0...0.16.1

### Changed

* Bump dependencies

## [0.16.0][]

[0.16.0]: https://github.com/reliablyhq/cli/compare/0.15.1...0.16.0

### Changed

* Bump dependencies
* Log the entire execution now

## [0.15.1][]

[0.15.1]: https://github.com/reliablyhq/cli/compare/0.15.0...0.15.1

### Changed

* Bump dependencies

## [0.15.0][]

[0.15.0]: https://github.com/reliablyhq/cli/compare/0.14.1...0.15.0

### Changed

* Bump dependencies

## [0.14.1][]

[0.14.1]: https://github.com/reliablyhq/cli/compare/0.14.0...0.14.1

### Fixed

* Wrong positionning of call

## [0.14.0][]

[0.14.0]: https://github.com/reliablyhq/cli/compare/0.13.1...0.14.0

### Changed

* Extended support for `dry` in the `runtime` block:
  
  ```json
  {
    "runtime": {
        "dry": "probes"
    }
  }
  ```
* Extended support for `fail_fast` and `freq` in the `runtime` block


## [0.13.1][]

[0.13.1]: https://github.com/reliablyhq/cli/compare/0.10.0...0.13.1

### Changed

* GitHub deployment can also take a Reliably environment id now

## [0.10.0][]

[0.10.0]: https://github.com/reliablyhq/cli/compare/0.9.0...0.10.0

### Added

* The `reliably service plan execute` now reads the following env variable:
  * `RELIABLY_CLI_DRY_STRATEGY` one of: `"probes", "actions", "activities", "pause"`
  * `RELIABLY_CLI_ROLLBACK_STRATEGY` one of : `"default", "always", "never" or "deviated"`
  * `RELIABLY_CLI_HYPOTHESIS_STRATEGY` one of : `"default", "before-method-only", "after-method-only", "during-method-only", "continuously"`
  * `RELIABLY_CLI_HYPOTHESIS_STRATEGY_FREQ` which is only required when
    `RELIABLY_CLI_HYPOTHESIS_STRATEGY` is `continuously`
  * `RELIABLY_CLI_HYPOTHESIS_STRATEGY_FAIL_FAST` which is only required when
    `RELIABLY_CLI_HYPOTHESIS_STRATEGY` is `continuously`

## [0.9.0][]

[0.9.0]: https://github.com/reliablyhq/cli/compare/0.8.9...0.9.0

### Changed

* Bump dependencies

## [0.8.9][]

[0.8.9]: https://github.com/reliablyhq/cli/compare/0.8.8...0.8.9

### Changed

* Bump dependencies

## [0.8.8][]

[0.8.8]: https://github.com/reliablyhq/cli/compare/0.8.7...0.8.8

### Fixed

* swapped `parse_obj` to `model_validate` for Environment as per Pydantic v2

### Changed

* Bump dependencies

## [0.8.7][]

[0.8.7]: https://github.com/reliablyhq/cli/compare/0.8.6...0.8.7

### Fixed

* using new root model approach from Pydantic v2

### Changed

* Bump dependencies

## [0.8.6][]

[0.8.6]: https://github.com/reliablyhq/cli/compare/0.8.5...0.8.6

### Changed

* remove trailing print statement

## [0.8.5][]

[0.8.5]: https://github.com/reliablyhq/cli/compare/0.8.4...0.8.5

### Changed

* Bump dependencies

## [0.8.4][]

[0.8.4]: https://github.com/reliablyhq/cli/compare/0.8.3...0.8.4

### Changed

* Pydantic requires default value when optional is set
* Bump dependencies

## [0.8.2][]

[0.8.2]: https://github.com/reliablyhq/cli/compare/0.8.1...0.8.2

### Changed

* Bump dependencies
* Enable PyPI trusted publisher
* Automate release with changelog

## [0.8.1][]

[0.8.1]: https://github.com/reliablyhq/cli/compare/0.8.0...0.8.1

### Changed

* Bump dependencies

## [0.8.0][]

[0.8.0]: https://github.com/reliablyhq/cli/compare/0.7.1...0.8.0

### Changed

* Bump dependencies
* Load integration environment variables and secrets into memory when requested
- Reworked the Dockerfile to use pdm.lock

## [0.7.1][]

[0.7.1]: https://github.com/reliablyhq/cli/compare/0.7.0...0.7.1

### Changed

* Bump dependencies

## [0.7.0][]

[0.7.0]: https://github.com/reliablyhq/cli/compare/0.6.2...0.7.0

### Added

* The `--load-environment` flag to the `plan execute` command so that the CLI
  automatically fetches the environment, if any provided, for the given plan.
  This will fetch environment variables and secrets and load them into memory
  for Chaos Toolkit to use

## [0.6.2][]

[0.6.2]: https://github.com/reliablyhq/cli/compare/0.6.1...0.6.2

### Fixed

* Give more time for Pypi to propagate the new release

## [0.6.1][]

[0.6.1]: https://github.com/reliablyhq/cli/compare/0.6.0...0.6.1

### Fixed

* Dockerfile so it builds from the tag just released
* Fixed GitHub action ity uses buildx and sets the right tags

## [0.5.0][]

[0.5.0]: https://github.com/reliablyhq/cli/compare/0.4.0...0.5.0

### Added

* Extended the `config` command

## [0.4.0][]

[0.4.0]: https://github.com/reliablyhq/cli/compare/0.3.0...0.4.0

### Changed

- Various fixes to handling chaostoolkit execution properly
- Better messages when some config keys aren't set
- Added help messages to commands

## [0.3.0][]

[0.3.0]: https://github.com/reliablyhq/cli/compare/0.2.6...0.3.0

### Changed

- Ensure we can load Python libraries using pyoxdizer even when they rely
  on the `__file__` value

## [0.2.6][]

[0.2.6]: https://github.com/reliablyhq/cli/compare/0.2.6...HEAD

### Changed

- Add changelog file
- Bump dependencies
- Fix readme badges