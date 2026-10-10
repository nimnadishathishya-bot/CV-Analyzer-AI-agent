import os
from utils.extractor import extract_text_from_file

def test_extraction():
    print("Testing text extraction from sample DOCX files...")
    alex_path = "sample_cvs/Alex_Morgan_CV.docx"
    jordan_path = "sample_cvs/Jordan_Lee_CV.docx"
    
    with open(alex_path, "rb") as f:
        alex_bytes = f.read()
    alex_text = extract_text_from_file("Alex_Morgan_CV.docx", alex_bytes)
    print(f"\n--- Extracted Alex CV ({len(alex_text)} chars) ---")
    print(alex_text[:200])
    assert "Figma" in alex_text, "Figma should be extracted from Alex's CV"
    assert "Photoshop" in alex_text, "Photoshop should be extracted from Alex's CV"
    
    with open(jordan_path, "rb") as f:
        jordan_bytes = f.read()
    jordan_text = extract_text_from_file("Jordan_Lee_CV.docx", jordan_bytes)
    print(f"\n--- Extracted Jordan CV ({len(jordan_text)} chars) ---")
    print(jordan_text[:200])
    assert "Photoshop" in jordan_text, "Photoshop should be extracted from Jordan's CV"
    
    print("\n[SUCCESS] All text extraction unit tests passed successfully!")

if __name__ == "__main__":
    test_extraction()
