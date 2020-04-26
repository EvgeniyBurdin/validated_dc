# ValidatedDC

Dataclass with data validation.
Checks the value of its fields by their annotations.

## Capabilities:

1. Support for standard and custom Python classes.
2. Support for some aliases from the `typing` module, namely: `Any`, `List`, `Literal`, `Optional`, `Union`.
3. Replacing the `dict` with an instance of the dataclass.

`ValidatedDC` is a regular Python dataclass, but with the ability to check the validity of the data by which this dataclass was initialized. Also, you can check the data at any time during the life of the instance.
