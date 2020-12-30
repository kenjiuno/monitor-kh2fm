# pcsx2-execmon monitor scripts

## run inside pcsx2

No additional package will be required.

## run standalone

Install required packages from pypi.

```bat
py -m pip install -r requirements.txt
```

Also you want to install invoke too.

```bat
py -m pip install invoke
```

Run some generator tasks thru invoke.

```bat
py -m invoke xml sinc
```
