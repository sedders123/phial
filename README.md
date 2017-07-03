# phial

[![Documentation Status](https://readthedocs.org/projects/phial/badge/?version=develop)](http://phial.readthedocs.io/en/develop/)
[![CircleCI](https://circleci.com/gh/sedders123/phial.svg?style=svg)](https://circleci.com/gh/sedders123/phial)
[![Coverage Status](https://coveralls.io/repos/github/sedders123/phial/badge.svg?branch=develop)](https://coveralls.io/github/sedders123/phial?branch=develop)


> A simple framework for building slack bots

Phial is a slack bot framework, modelled loosely on [flask](https://github.com/pallets/flask/).
## Table of Contents

- [Install](#install)
- [Usage](#usage)
- [Contribute](#contribute)
- [Project TODO](#todo)
- [License](#license)

## Install

```
  $ pip install git+https://github.com/sedders123/phial
```

## Usage

### Python:

```python
import Phial, command, Response

bot = Phial('---slack token here---')

@bot.command('greet <name>')
def greet(name):
    '''Simple command with argument which replies to a message'''
    return Response(text="hello {}".format(name),
                   channel=command.channel)

bot.run()

```

### Slack:

By default the bot requires a prefix of `!` before its commands. This can be changed in the config.
```
> youruser: !greet jim
> bot: Hello Jim
```


More example bots can be found in the [examples](examples/) folder

## Contribute

If a feature is missing, or you can improve the code please submit a PR or raise an Issue

## TODO:
 - Tests
 - PyPi Package


## License

MIT © 2017 James Seden Smith
