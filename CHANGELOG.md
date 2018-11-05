# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## Unreleased
### Changed
 - Allow configuration to be partially updated ([@RealOrangeOne](https://github.com/RealOrangeOne) in [#81](https://github.com/sedders123/phial/pull/81))
### Fixed
 - Scheduled events using `every().day().at()`, now run on the day that the program is started on. ([@runz0rd](https://github.com/runz0rd) in [#90](https://github.com/sedders123/phial/pull/90))

## [0.6.0](https://github.com/sedders123/phial/releases/tag/0.6.0) - 2018-10-10
### Changed
 - SlackClient now attempts to auto reconnect by default. This can be turned off in the settings.
 - Logs outputted using the default logger no longer duplicate.
 - SlackClient no longer asks for team state as phial does not use this. Should speed up connection times espically in larger teams.

## [0.5.0](https://github.com/sedders123/phial/releases/tag/0.5.0) - 2018-09-14
### Changed
 - Help command now works better with multiline doc strings. The command now ignores single new lines and converts double new lines into single new lines, similar to markdown.
 - Parameters of commands can now be wrapped in double quotation marks to allow for values containing whitespace.

## [0.4.0](https://github.com/sedders123/phial/releases/tag/0.4.0) - 2018-08-30
### Added
 - Built-in help command. Uses docstrings as help text unless overridden
 - Added the ability to specify a 'fallback' command for when a user attempts to use an invalid command
### Changed
 - Default logger level changed to INFO

## [0.3.0](https://github.com/sedders123/phial/releases/tag/0.3.0) - 2018-08-05
### Added
 - Scheduled functions
 - Send [Message Attachments](https://api.slack.com/docs/message-attachments)
 - Send [ephemeral](https://api.slack.com/methods/chat.postEphemeral) messages
 - Type hints
 - Support for logging

## [0.2.1](https://github.com/sedders123/phial/releases/tag/0.2.0) - 2018-04-09
### Changed
- Upgraded to slackclient 1.2.1
- Lowered minimum Python version to 3.4

## [0.2.0](https://github.com/sedders123/phial/releases/tag/0.2.0) - 2018-04-05
### Added
- Optional Case Sensitivity for commands. Commands are now no longer case sensitive by default, they have an optional parameter to turn on case sensitivity if desired.
### Changed
- Minimum Python version now 3.4

## [0.1.3](https://github.com/sedders123/phial/releases/tag/0.1.3) - 2018-04-05
### Changed
- Changed f-strings to `.format()` to prepare for supporting Python 3.4


## [0.1.0](https://github.com/sedders123/phial/releases/tag/0.1.0) - 2018-04-04
- Initial release of project
