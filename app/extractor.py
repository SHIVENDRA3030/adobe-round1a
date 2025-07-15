import pdfplumber
from typing import List, Dict, Tuple
import json
import os
from tqdm import tqdm
import re

class HeadingExtractor:
    def __init__(self):
        self.headings = []
        # Common heading patterns in different languages
        self.heading_patterns = {
            'en': ['Chapter', 'Section', 'Part', 'Overview', 'Summary', 'Conclusion', 'Appendix'],
            'es': ['Capítulo', 'Sección', 'Parte', 'Resumen', 'Conclusión', 'Apéndice'],
            'fr': ['Chapitre', 'Section', 'Partie', 'Aperçu', 'Résumé', 'Conclusion', 'Annexe'],
            'de': ['Kapitel', 'Abschnitt', 'Teil', 'Überblick', 'Zusammenfassung', 'Fazit', 'Anhang'],
            'zh': ['章', '节', '部分', '概述', '摘要', '结论', '附录'],
            'ja': ['章', '節', '部', '概要', '要約', '結論', '付録'],
            'ko': ['장', '절', '부분', '개요', '요약', '결론', '부록']
        }
        # Font size thresholds for heading levels
        self.size_thresholds = {}

    def _is_heading(self, line: str, font_size: float, font_name: str) -> bool:
        """Determine if a line is likely a heading using improved rules.

        Args:
            line (str): Line of text
            font_size (float): Font size of the line
            font_name (str): Font name/family

        Returns:
            bool: True if line appears to be a heading
        """
        if not line or len(line) > 100:
            return False

        # Update size thresholds based on observed font sizes
        if font_size > 0:
            if font_size not in self.size_thresholds:
                self.size_thresholds[font_size] = 1
            else:
                self.size_thresholds[font_size] += 1

        # Common heading keywords in all languages
        if any(any(line.startswith(k) for k in patterns) for patterns in self.heading_patterns.values()):
            return True

        # Numbered patterns (e.g., 1., 1.1, 1.1.1)
        if line[:6].strip().replace('.', '').isdigit() and '.' in line[:6]:
            return True

        # ALL CAPS lines (likely headings)
        if line.isupper() and len(line.split()) <= 6:
            return True

        # Title case with few words (likely section titles)
        if line.istitle() and len(line.split()) <= 8:
            return True

        # Short lines with larger font size
        if len(line.split()) <= 5 and font_size >= self._get_average_font_size():
            return True

        # Bold font indicators
        if font_name.lower().find('bold') != -1 and len(line.split()) <= 8:
            return True

        # Exclude form fields and labels
        if ':' in line and not line.endswith('.'):
            return False

        return False

    def _get_average_font_size(self) -> float:
        """Calculate the average font size from observed sizes.

        Returns:
            float: Average font size, or 12 if no sizes recorded
        """
        if not self.size_thresholds:
            return 12.0
        
        sizes = list(self.size_thresholds.keys())
        return sum(sizes) / len(sizes)

    def extract_headings(self, pdf_path: str) -> Tuple[str, List[Dict]]:
        """Extract headings from a PDF file using pdfplumber.

        Args:
            pdf_path (str): Path to the PDF file

        Returns:
            Tuple[str, List[Dict]]: Document title and list of headings with their properties
        """
        self.headings = []  # Clear previous headings
        self.size_thresholds = {}  # Reset font size observations
        title = "Untitled"

        try:
            with pdfplumber.open(pdf_path) as pdf:
                # First pass: gather font statistics
                for page in pdf.pages:
                    for char in page.chars:
                        if char["size"] > 0:
                            size = round(float(char["size"]), 1)
                            if size not in self.size_thresholds:
                                self.size_thresholds[size] = 1
                            else:
                                self.size_thresholds[size] += 1

                # Second pass: extract headings
                for page_num in tqdm(range(len(pdf.pages)), desc=f'Processing {os.path.basename(pdf_path)}'):
                    page = pdf.pages[page_num]
                    lines_by_font = {}

                    for char in page.chars:
                        font_size = round(float(char["size"]), 1)
                        font_name = char.get("fontname", "")
                        text = char["text"].strip()

                        # Group chars by line position + font size
                        top_key = round(char["top"], 1)
                        if top_key not in lines_by_font:
                            lines_by_font[top_key] = {
                                "text": "",
                                "size": font_size,
                                "font": font_name,
                                "page": page_num + 1
                            }

                        lines_by_font[top_key]["text"] += text

                    for entry in lines_by_font.values():
                        line = entry["text"].strip()
                        if not line or len(line) > 100:
                            continue

                        if self._is_heading(line, entry["size"], entry["font"]):
                            level = self._determine_level(entry["size"])
                            if title == "Untitled" and entry["size"] >= self._get_title_threshold():
                                title = line
                            self.headings.append({
                                "text": line,
                                "page": entry["page"],
                                "level": level
                            })

                return title, self.headings

        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
            return "Untitled", []

    def _determine_level(self, size: float) -> str:
        """Determine heading level based on font size distribution.

        Args:
            size (float): Font size

        Returns:
            str: Heading level (H1, H2, or H3)
        """
        if not self.size_thresholds:
            return "H3"

        sizes = sorted(self.size_thresholds.keys(), reverse=True)
        if not sizes:
            return "H3"

        largest = sizes[0]
        threshold_h1 = largest * 0.9
        threshold_h2 = largest * 0.8

        if size >= threshold_h1:
            return "H1"
        elif size >= threshold_h2:
            return "H2"
        else:
            return "H3"

    def _get_title_threshold(self) -> float:
        """Calculate the threshold for title font size.

        Returns:
            float: Font size threshold for titles
        """
        if not self.size_thresholds:
            return 18.0

        sizes = sorted(self.size_thresholds.keys(), reverse=True)
        if not sizes:
            return 18.0

        return sizes[0] * 0.95

    def save_to_json(self, output_path: str, title: str = "Untitled"):
        """Save extracted headings to a JSON file.

        Args:
            output_path (str): Path where JSON file will be saved
            title (str): Document title
        """
        result = {
            "title": title,
            "outline": self.headings
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)