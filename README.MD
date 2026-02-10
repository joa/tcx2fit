# tcx2fit converter

```
usage: tcx2fit.py [-h] [-i INPUT] [--age AGE] [--weight WEIGHT] [--vo2max VO2MAX] [--gender {m,f}]

takes the Coxswain TCX file and export it as FIT file

options:
  -h, --help         show this help message and exit
  -i, --input INPUT  give file path to the Coxswain TCX file
  --age AGE          Age of the user for calorie calculation (default: 33)
  --weight WEIGHT    Weight of the user in kg for calorie calculation (default: 78)
  --vo2max VO2MAX    VO2max of the user for calorie calculation (default: 45)
  --gender {m,f}     Gender of the user (m for male, f for female) for calorie calculation (default: m)
```

See [original project](https://github.com/inonoob/Coxswain2Fit) for more details. 

Works with variety TCX files now (that contain floating point data), exports to a file along side the given TCX, support for different age, weight, VO2max and gender.


## Requirements

project has been done with python 3.8 

needed modules: 
- lxml (for reading the TCX file)
- numpy (to do the math stuff)

## Installation or Getting Started

	git clone https://github.com/joa/tcx2fit
	
## Usage
In order to use the script, call the scirpt with python3.8 use the --input command and give the path to the TCX file.

    python3 tcx2fit.py --input /path/to/file.tcx --age 40 --vo2max 61 --weight 66 --gender m
    
    >>> main header created
    >>> file_id message + data created
    >>> write data for session
    >>> write data for activity
    <<< file is : 124273 bytes
    >>> file size placed into the header with removed 14 bytes of header from the size file
    <<< checksum calculated:                                     6bf3
    >>> checksum placed at the end of the file
    >>> file exported to /path/to/file.fit
    finished    

## License

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Coxswain exports to FIT converter"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
