import os
from app.extractor import HeadingExtractor
from typing import List, Tuple

def process_pdfs(input_dir: str, output_dir: str) -> List[str]:
    """Process all PDF files in the input directory and save results to output directory.

    Args:
        input_dir (str): Directory containing PDF files
        output_dir (str): Directory where JSON files will be saved

    Returns:
        List[str]: List of processed files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    processed_files = []
    extractor = HeadingExtractor()

    # Process each PDF file
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(input_dir, filename)
            output_filename = os.path.splitext(filename)[0] + '.json'
            output_path = os.path.join(output_dir, output_filename)

            print(f"\nProcessing {filename}...")
            title, headings = extractor.extract_headings(pdf_path)
            
            if headings:
                extractor.save_to_json(output_path, title)
                processed_files.append(filename)
                print(f"Extracted {len(headings)} headings from {filename}")
                print(f"Document title: {title}")
            else:
                print(f"No headings found in {filename}")

    return processed_files

def main():
    # Define input and output directories relative to script location
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(base_dir, 'input')
    output_dir = os.path.join(base_dir, 'output')

    # Create input directory if it doesn't exist
    os.makedirs(input_dir, exist_ok=True)

    # Check if input directory has PDF files
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"\nNo PDF files found in {input_dir}")
        print("Please add PDF files to the input directory and run the script again.")
        return

    print(f"\nFound {len(pdf_files)} PDF files in input directory")
    processed_files = process_pdfs(input_dir, output_dir)

    # Print summary
    print(f"\nProcessing complete!")
    print(f"Processed {len(processed_files)} files")
    print(f"Results saved in: {output_dir}")

if __name__ == '__main__':
    main()