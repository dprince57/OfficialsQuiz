import pdfplumber
import re


def extract_questions_and_answers(text):
    """
    Extracts questions and their answers from a given text.

    :param text: The raw text extracted from a PDF page.
    :return: A list of tuples, where each tuple contains a question (str)
             and a list of answers (dict with 'text' and 'is_correct' keys).
    """
    lines = text.split("\n")
    questions = []
    current_question = None
    current_answers = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        # Detect a new question starting with "Q#"
        question_match = re.match(r"(Q\d+)\s(.*)", line)
        if question_match:
            # Save the previous question and its answers
            if current_question and current_answers:
                questions.append((current_question.strip(), current_answers))
                current_answers = []

            # Start a new question
            current_question = question_match.group(2).strip()

        # Detect standalone "o" indicating the start of an answer
        elif line == "o" and i + 1 < len(lines):
            # The next line is the answer text
            answer_text = lines[i + 1].strip()
            is_correct = "__" in answer_text  # Detect correct answers by underline
            cleaned_text = answer_text.replace("__", "").strip()  # Clean underline markers
            current_answers.append({"text": cleaned_text, "is_correct": is_correct})
            i += 1  # Skip the next line since it's part of the answer

        # Append additional lines to the current question
        elif current_question and not re.match(r"(Q\d+)\s", line):
            current_question += f" {line.strip()}"

        i += 1

    # Add the last question and answers
    if current_question and current_answers:
        questions.append((current_question.strip(), current_answers))

    return questions


file_path = "q1.pdf"  # Replace with the path to your actual PDF

with pdfplumber.open(file_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        parsed_data = extract_questions_and_answers(text)
        for question, answers in parsed_data:  # Correct unpacking of tuple
            print("Question:", question)
            for ans in answers:
                print("  - Answer:", ans["text"], "(Correct)" if ans["is_correct"] else "(Incorrect)")
