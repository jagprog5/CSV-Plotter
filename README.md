# CSV Plotter

This script provides a shell utility for plotting csv data.

For example:

```bash
echo -n $'1\n2\n3\n' | ./plot.py "{'0': 'position_x'}" -s "$PWD/img.png"
```

Docs:

```bash
./plot.py -h
```