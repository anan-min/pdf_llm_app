import pymupdf as fitz
import re
from pathlib import Path
import ollama

# SYSTEM_ROLE = """You are an expert Business Analyst (BA) with a deep understanding of business processes and software development lifecycles. You specialize in identifying, eliciting, analyzing, and documenting business needs and requirements from various stakeholders. Your goal is to translate business objectives into clear, actionable specifications, ensuring alignment between business goals and technical solutions."""

# # Comprehensive prompt for generating test cases from system documentation
# GENERATE_TEST_CASES_PROMPT = """Create comprehensive test cases based on the provided system documentation. Analyze the document and generate test cases to validate the system's functionality."""

SYSTEM_ROLE = """คุณเป็นนักวิเคราะห์ธุรกิจ (Business Analyst) ระดับผู้เชี่ยวชาญที่มีความเข้าใจลึกซึ้งเกี่ยวกับกระบวนการทางธุรกิจและวงจรการพัฒนาซอฟต์แวร์ คุณเชี่ยวชาญในการระบุ, ค้นหา, วิเคราะห์ และจัดทำเอกสารความต้องการทางธุรกิจจากผู้มีส่วนเกี่ยวข้องต่างๆ เป้าหมายของคุณคือการแปลวัตถุประสงค์ทางธุรกิจให้เป็นข้อกำหนดที่ชัดเจนและสามารถนำไปปฏิบัติได้พร้อมทั้งสร้างความสอดคล้องระหว่างเป้าหมายทางธุรกิจและโซลูชันทางเทคนิค"""

# Comprehensive prompt for generating test cases from system documentation
GENERATE_TEST_CASES_PROMPT = """จงเขียน test case ของระบบที่จะต้องทดสอบ เพื่อให้ compile tor ทั้งหมดนี้ให้หน่อย"""


MODELS = [
    "llama3.2",
    "qwen2.5vl:latest",
    "scb10x/llama3.1-typhoon2-8b-instruct:latest",
    "mistral:7b",
    "gemma3:27b",
    "qwen2.5vl:32b",
]


def preprocess_text(text):
    """Preprocess text to improve extraction quality"""
    # Clean up excessive whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r' +', ' ', text)

    # Try to identify test case sections
    test_keywords = [
        'test case', 'test scenario', 'testing', 'validation', 'verification',
        'quality assurance', 'qa', 'acceptance criteria', 'test plan',
        'test procedure', 'test script', 'test data', 'expected result'
    ]

    # Check if document likely contains test cases
    text_lower = text.lower()
    has_test_content = any(keyword in text_lower for keyword in test_keywords)

    return text, has_test_content


def send_to_ollama(text, model="llama3.2", system_role=SYSTEM_ROLE, prompt_prefix="", temp=0.3):
    """Send text to Ollama with improved parameters for extraction"""
    messages = [
        {"role": "system", "content": system_role},
        {"role": "user", "content": f"{prompt_prefix}\n\n{text}"}
    ]

    try:
        response = ollama.chat(
            model=model,
            messages=messages,
            options={
                "temperature": temp,  # Lower temperature for more focused extraction
                "top_p": 0.8,
                "top_k": 30,
                "repeat_penalty": 1.1
            }
        )
        return response['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"


def generate_test_cases_from_documentation(text_content, model="llama3.2"):
    """Generate comprehensive test cases based on system documentation"""

    # Preprocess text for better analysis
    processed_text, _ = preprocess_text(text_content)

    print("Analyzing system documentation and generating test cases...")

    # Generate test cases with higher temperature for creativity
    test_cases = send_to_ollama(
        processed_text,
        model=model,
        system_role=SYSTEM_ROLE,
        prompt_prefix=GENERATE_TEST_CASES_PROMPT,
        temp=0.6  # Higher temperature for more comprehensive generation
    )

    # Create the final prompt that was used
    final_prompt = f"=== SYSTEM ROLE ===\n{SYSTEM_ROLE}\n\n=== TEST CASE GENERATION PROMPT ===\n{GENERATE_TEST_CASES_PROMPT}\n\n=== PROCESSED DOCUMENT TEXT ===\n{processed_text}"

    return test_cases, final_prompt


def pdf_to_text(pdf_path):
    """Convert PDF file to text using PyMuPDF (fitz) with improved extraction"""
    try:
        doc = fitz.open(pdf_path)
        text = ""

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_text = page.get_text()

            # Try to preserve some structure
            if page_text.strip():
                text += f"\n=== PAGE {page_num + 1} ===\n"
                text += page_text
                text += "\n"

        doc.close()
        return text
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"


def create_result_folder():
    """Create result folder if it doesn't exist"""
    result_folder = Path("thai_result")
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


def process_single_pdf(pdf_path, result_folder, generate_test_cases=True, model="llama3.2"):
    """Process a single PDF file to generate test cases from system documentation"""
    print(f"Processing: {pdf_path}")

    # Convert PDF to text
    text_content = pdf_to_text(pdf_path)

    if text_content.startswith("Error"):
        print(f"Failed to extract text: {text_content}")
        return None

    pdf_name = Path(pdf_path).stem

    # Generate test cases from system documentation
    if generate_test_cases:
        print(f"Generating test cases using model: {model}")
        test_cases, final_prompt = generate_test_cases_from_documentation(
            text_content, model)

        # Save generated test cases
        model_name = re.sub(r'[^\w\.-]', '_', model)
        test_cases_file = f"{pdf_name}_{model_name}_test_cases.txt"
        test_cases_path = save_text_to_file(
            test_cases, test_cases_file, result_folder)
        print(f"Test cases saved to: {test_cases_path}")

        # Save final prompt used
        final_prompt_file = f"{pdf_name}_{model_name}_final_prompt.txt"
        final_prompt_path = save_text_to_file(
            final_prompt, final_prompt_file, result_folder)
        print(f"Final prompt saved to: {final_prompt_path}")

        return {
            "pdf_path": pdf_path,
            "test_cases_path": test_cases_path,
            "final_prompt_path": final_prompt_path,
            "text_content": text_content,
            "test_cases": test_cases,
            "final_prompt": final_prompt
        }

    return {
        "pdf_path": pdf_path,
        "text_content": text_content
    }


def process_all_pdfs(pdf_folder="static/pdfs", generate_test_cases=True, model="llama3.2"):
    """Process all PDF files in the specified folder to generate test cases"""
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
            pdf_file, result_folder, generate_test_cases, model)
        if result:
            results.append(result)
        print("-" * 50)

    return results


def main():
    for model in MODELS:
        print(f"\nGenerating test cases with model: {model}")
        print("=" * 50)
        results = process_all_pdfs(
            pdf_folder="static/pdfs",
            generate_test_cases=True,
            model=model
        )
        print(
            f"\nProcessing complete! {len(results)} files processed successfully.")


if __name__ == "__main__":
    main()
