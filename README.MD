# tcx2fit converter

```
usage: tcx2fit.py [-h] -i INPUT [--age AGE] [--weight WEIGHT] [--vo2max VO2MAX] [--gender {m,f}]
                  [--workout WORKOUT] [--warmup WARMUP]

Convert a Coxswain TCX file to FIT format

options:
  -h, --help            show this help message and exit
  -i, --input INPUT     Path to the Coxswain TCX file
  --age AGE             Age of the user (default: 33)
  --weight WEIGHT       Weight in kg (default: 78)
  --vo2max VO2MAX       VO2max (default: 45)
  --gender {m,f}        Gender: m or f (default: m)
  --workout WORKOUT     Path to a FIT workout file for workout-aware lap splitting
  --warmup WARMUP       Warmup duration in minutes (used with --workout to set the open warmup
                        step; remaining time becomes the cooldown)
```

See [original project](https://github.com/inonoob/Coxswain2Fit) for more details. 

Works with variety TCX files now (that contain floating point data), exports to a file along side the given TCX, support for different age, weight, VO2max and gender.


## Requirements

project has been done with python 3.8 

needed modules:
- lxml (for reading the TCX file)
- numpy (to do the math stuff)
- fitparse (for reading FIT workout files with `--workout`)

## Installation or Getting Started

	git clone https://github.com/joa/tcx2fit
	
## Usage

### Standard conversion

Call the script with `--input` and the path to the TCX file. The FIT file is written next to the TCX file.

    python3 tcx2fit.py --input /path/to/file.tcx --age 40 --vo2max 61 --weight 66 --gender m

### Workout-aware lap splitting (`--workout`)

Pass a FIT workout file with `--workout` to split the activity into laps that match the workout steps instead of the default 500 m laps. Each workout step becomes one lap in the output FIT file.

    python3 tcx2fit.py --input /path/to/file.tcx --workout /path/to/workout.fit

### Setting the warmup duration (`--warmup`)

If the workout contains an open-ended warmup step (no fixed duration), use `--warmup` to specify how many minutes to assign to it. Any remaining time at the end of the activity is treated as the cooldown.

    python3 tcx2fit.py --input /path/to/file.tcx --workout /path/to/workout.fit --warmup 10

## License

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Coxswain exports to FIT converter"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
