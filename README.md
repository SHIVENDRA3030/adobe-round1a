# PDF Heading Extractor

A Python tool that extracts headings from PDF files and outputs them in a structured JSON format. The tool uses various heuristics to identify headings and creates a hierarchical outline of the document's structure.

## Features

- Extracts headings from PDF files using multiple detection methods:
  - Common heading patterns (Chapter, Section, etc.)
  - Numbered headings (1., 1.1, etc.)
  - ALL CAPS text
  - Short, standalone lines
- Determines heading levels (H1, H2, H3)
- Identifies document title
- Generates JSON output with document structure
- Progress tracking for large documents
- Batch processing support

## Output Format

```json
{
  "title": "Document Title",
  "outline": [
    {
      "text": "Heading Text",
      "page": 1,
      "level": "H1"
    }
  ]
}
```

## Requirements

- Python 3.9 or higher
- Required packages (specified in requirements.txt):
  - PyPDF2==3.0.1
  - python-dotenv==1.0.0
  - tqdm==4.65.0

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Place PDF files in the `input` directory
2. Run the script:
   ```bash
   python run.py
   ```
3. Find extracted headings in the `output` directory as JSON files

## Docker Support

To run using Docker:

1. Build the image:
   ```bash
   docker build -t pdf-heading-extractor .
   ```

2. Run the container:
   ```bash
   docker run -v "$(pwd)/input:/app/input" -v "$(pwd)/output:/app/output" pdf-heading-extractor
   ```

## Limitations

- Heading detection is heuristic-based and may not catch all edge cases
- Font information is not currently used for heading detection
- Some PDF formatting may not be preserved in the extraction process

## Future Improvements

- Add support for font-based heading detection using pdfplumber
- Improve accuracy of heading level determination
- Add support for more heading patterns
- Implement custom heading rules configuration