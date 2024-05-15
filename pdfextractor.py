import os
import camelot  # Efficient table extraction
import PyPDF2  # Basic text extraction (fallback)
import re  # Regular expressions

def read_pdfs_from_folder(folder_path, regex_pattern, output_folder):
  """
  Reads data from PDFs in a folder, extracts patterns, creates separate PDFs,
  and generates a CSV file.

  Args:
      folder_path (str): Path to the folder containing PDF files.
      regex_pattern (str): Regular expression pattern to match.
      output_folder (str): Path to the folder for storing extracted PDFs and text files.

  Returns:
      list: A list of dictionaries, where each dictionary represents the processed data from a PDF file.
  """

  extracted_data = []
  for filename in os.listdir(folder_path):
    if filename.endswith(".pdf"):
      filepath = os.path.join(folder_path, filename)
      data = []
      text_data = []

      try:
        # Attempt using Camelot for table extraction
        tables = camelot.read_pdf(filepath)
        for table in tables:
          data.append(table.df.to_dict(orient='records'))
      except Exception as e:
        print(f"Error processing {filename} with Camelot: {e}")

      # Text extraction (fallback to PyPDF2 if Camelot fails)
      try:
        with open(filepath, 'rb') as pdf_file:
          pdf_reader = PyPDF2.PdfReader(pdf_file)
          for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            text_data.append(text)
      except Exception as e:
        print(f"Error processing {filename} with PyPDF2: {e}")

      # Regex pattern matching and separate PDF creation
      matches = re.findall(regex_pattern, "\n".join(text_data), re.MULTILINE)  # Combine page text
      for match_index, match in enumerate(matches):
        output_filename = f"{filename[:-4]}_{match_index + 1}.pdf"  # Unique filename
        output_filepath = os.path.join(output_folder, output_filename)
        with open(output_filepath, 'wb') as output_pdf:
          writer = PyPDF2.PdfWriter()
          writer.addPage(PyPDF2.PdfReader(filepath).pages[0])  # Copy first page
          writer.write(output_pdf)

      extracted_data.append({"filename": filename, "data": data, "matches": matches})

  # Generate CSV file (replace with your desired CSV structure)
  csv_data = []
  for item in extracted_data:
    for match in item["matches"]:
      csv_data.append({"filename": item["filename"], "match": match})

  # Write CSV data to file (replace with your preferred CSV library)
  with open(os.path.join(output_folder, "extracted_data.csv"), 'w', newline='') as csvfile:
    import csv  # Assuming you have the csv library installed
    writer = csv.DictWriter(csvfile, fieldnames=["filename", "match"])
    writer.writeheader()
    writer.writerows(csv_data)

  return extracted_data

# Example usage
folder_path = "egpath"  # Replace with your actual folder path
regex_pattern = r"your_regex_pattern_here"  # Replace with your desired regex pattern
output_folder = "path/to/output/folder"  # Replace with your desired output folder path

os.makedirs(output_folder, exist_ok=True)  # Create output folder if it doesn't exist

extracted_data = read_pdfs_from_folder(folder_path, regex_pattern, output_folder)

# Process the extracted data (optional)
print("Processed data:")
for item in extracted_data:
  print(f"Filename: {item['filename']}")
  print(f"Matches: {item['matches']}")
  print("---")
