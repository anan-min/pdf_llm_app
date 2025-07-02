import fitz
import re
from pathlib import Path
import ollama

SYSTEM_ROLE = """You are an expert Business Analyst (BA) with a deep understanding of business processes and software development lifecycles. You specialize in identifying, eliciting, analyzing, and documenting business needs and requirements from various stakeholders. Your goal is to translate business objectives into clear, actionable specifications, ensuring alignment between business goals and technical solutions."""

PROMPT = """Please extract the test cases from the following document, focusing on the following aspects:
1. Test case scenarios (describe the situation being tested)
2. Expected outcomes or results for each test case
3. Input data and conditions required for the test
4. Steps to execute the test case
5. Any assumptions or constraints for each test case
6. Additional notes or considerations related to the test cases
Please format your response in a clear, structured manner with proper headings and bullet points."""

MODELS = [
    "llama3.2",
    "qwen2.5vl:latest",
    "scb10x/typhoon2.1-gemma3-12b:latest",
    "scb10x/llama3.1-typhoon2-8b-instruct:latest",
    "mistral:7b"
    "gemma3:27b",
    "scb10x/typhoon-ocr-7b:latest"
]


def send_to_ollama(text, model="llama3.2", system_role=SYSTEM_ROLE, prompt_prefix="Extract and analyze test cases from this document:", temp=0.7):
    messages = [
        {"role": "system", "content": system_role},
        {"role": "user", "content": f"{prompt_prefix}\n\n{text}"}
    ]

    try:
        response = ollama.chat(
            model=model,
            messages=messages,
            options={
                "temperature": temp,
                "top_p": 0.9,
                "top_k": 40
            }
        )
        return response['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"


def pdf_to_text(pdf_path):
    """Convert PDF file to text using PyMuPDF (fitz)"""
    try:
        # Open the PDF file
        doc = fitz.open(pdf_path)
        text = ""

        # Extract text from each page
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += f"\n--- Page {page_num + 1} ---\n"
            text += page.get_text()

        doc.close()
        return text
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"


def create_result_folder():
    """Create result folder if it doesn't exist"""
    result_folder = Path("result")
    result_folder.mkdir(exist_ok=True)
    return result_folder


def save_text_to_file(text, filename, folder):
    """Save text content to a file"""
    try:
        file_path = folder / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
        return file_path
    except Exception as e:
        print(f"Error saving file: {str(e)}")
        return None


def process_single_pdf(pdf_path, result_folder, extract_test_cases=True, model="llama3.2"):
    """Process a single PDF file"""
    print(f"Processing: {pdf_path}")

    # Convert PDF to text
    text_content = pdf_to_text(pdf_path)

    if text_content.startswith("Error"):
        print(f"Failed to extract text: {text_content}")
        return None

    pdf_name = Path(pdf_path).stem

    # Extract test cases using Ollama (optional)
    if extract_test_cases:
        print(f"Extracting test cases using model: {model}")
        test_cases = send_to_ollama(
            text_content,
            model=model,
            system_role=SYSTEM_ROLE,
            prompt_prefix=PROMPT
        )

        # Save test cases
        model_name = re.sub(r'[^\w\.-]', '_', model)
        test_cases_file = f"{pdf_name}_{model_name}.txt"
        test_cases_path = save_text_to_file(
            test_cases, test_cases_file, result_folder)
        print(f"Test cases saved to: {test_cases_path}")

        return {
            "pdf_path": pdf_path,
            "test_cases_path": test_cases_path,
            "text_content": text_content,
            "test_cases": test_cases
        }

    return {
        "pdf_path": pdf_path,
        "text_content": text_content
    }


def process_all_pdfs(pdf_folder="static/pdfs", extract_test_cases=True, model="llama3.2"):
    """Process all PDF files in the specified folder"""
    pdf_folder = Path(pdf_folder)
    result_folder = create_result_folder()

    if not pdf_folder.exists():
        print(f"PDF folder '{pdf_folder}' does not exist!")
        return []

    # Find all PDF files
    pdf_files = list(pdf_folder.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in '{pdf_folder}'")
        return []

    print(f"Found {len(pdf_files)} PDF files to process")

    results = []
    for pdf_file in pdf_files:
        result = process_single_pdf(
            pdf_file, result_folder, extract_test_cases, model)
        if result:
            results.append(result)
        print("-" * 50)

    return results


def main():
    """Main function to run the PDF processing"""
    for model in MODELS:
        print(f"\nProcessing with model: {model}")
        print("=" * 50)

        # Process all PDFs in static/pdfs folder
        results = process_all_pdfs(
            pdf_folder="static/pdfs",
            extract_test_cases=True,  # Set to False if you only want text extraction
            model=model  # Choose from MODELS list
        )

        print(
            f"\nProcessing complete! {len(results)} files processed successfully.")
        print("Check the 'result' folder for output files.")


if __name__ == "__main__":
    main()
