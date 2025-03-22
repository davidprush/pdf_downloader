# PDF Downloader

A Python script to download PDF files from web pages listed in a text file, specifically targeting sections labeled "Accessing the Records".

## Features

- Downloads PDFs from multiple URLs listed in `url_list.txt`
- Extracts release/doc dates from the webpage and appends to filenames
- Numbers downloaded files sequentially
- Handles pagination to download from all available pages
- Comprehensive error handling and logging
- Verbose mode with colored console output
- Maintains a detailed log file

## Requirements

- Python 3.6+
- Required packages:
- requests
- beautifulsoup4

## Installation

1. Clone or download this repository
2. Install dependencies:
 ```bash
 pip install requests beautifulsoup4
```
3. Create a `url_list.txt` file in the same directory as the script

## Usage

Add URLs to url_list.txt, one per line

Run the script:
```bash
python pdf_downloader.py [-v]
```

## Command Line Options
`-v`, `--verbose`: Enable verbose output with colored console logging

## Output

- PDFs are downloaded to the current working directory
- Log file: pdf_downloader.log contains detailed execution information
- Console output (with -v):
```bash
Cyan: Date/time
Green: Successful downloads and info
Yellow: Warnings
Red: Errors and failures
Filename Format
```
- originalname: Original PDF filename from URL
- date: Extracted release/doc date (if found, in YYYY-MM-DD format)
- counter: Sequential download number

## Example
`url_list.txt`
```bash
https://example.com/records/page1
https://example.com/records/page2
```
### Running
```bash
python pdf_downloader.py -v
```
### Sample Output Files
```bash
document1_2023-05-15_1.pdf
document2_2023-05-16_2.pdf
report_3.pdf
```

## Logging

### The script creates pdf_downloader.log with:
- Timestamped entries for all actions
- Success/failure status for each download
- Page processing information
- Total statistics
- Error details

## Notes
- Requires internet connection
- Respects server load with 1-second delay between page requests
- Skips existing files to avoid duplicates
- Verifies downloaded files are actually PDFs via content-type
- Date extraction assumes date is in same table row as PDF link

## Troubleshooting

### If PDFs aren't downloading:
- Check pdf_downloader.log for errors
- Run with -v to see detailed output
- Verify URLs in url_list.txt are correct
- Ensure "Accessing the Records" section exists or adjust script logic

## Limitations
- Pagination assumes "Next" button/link
- Date formats supported: YYYY-MM-DD, MM/DD/YYYY, MM-DD-YYYY
- Color output may not work in some older terminals

## License

### MIT License

```
Copyright 2025 David Rush

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```
