# PyILInt

## Description

**PyILInt** is a pure **Python** implementation of the
[InterlockLedger ILInt](https://github.com/interlockledger/specification/tree/master/ILInt)
integer encoding standard.

This implementation is based on the [reference implementation](https://github.com/interlockledger/specification/tree/master/ILInt/reference)
shipped with the official definition of the standard
and the [rust-il2-ilint](https://github.com/interlockledger/rust-il2-ilint).

## Requirements

This program was developed for Python 3.8 or higher (it may work on older versions). No
external dependencies are required.

## Installation

To install this library, you may download the code from 
[github](https://github.com/interlockledger/pyilint) and copy
the contents of the directory ``src`` into your module's directory.

You can also use **pip** to install it by running the command:

```
$ pip install pyilint
```

## How to use it

A simple example program is:

```python
import random
from pyilint import MAX_UINT64, ilint_encode, ilint_decode

v = random.randrange(0, MAX_UINT64)
buff = bytearray()
size = ilint_encode(v, buff)
print(f'{v} was encoded to {buff} in {size} bytes...')
dec, dec_size = ilint_decode(buff)
print(f'...and was decoded to {dec} using {dec_size} bytes.')

```

The documentation of this library can be found in the source code and in its
unit-tests.

## License

This program is licensed under the BSD 3-Clause License.
