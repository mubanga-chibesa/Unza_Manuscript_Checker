
!pip install fastapi uvicorn # Install fastapi and uvicorn in a separate cell

!pip install deepdoctection[full]  # Install deepdoctection with all necessary dependencies

import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from deepdoctection import ModelCatalog, DoctectionPipe, Page # Use ModelCatalog instead of ModelZoo

# ... rest of your code ...

# Load the model using the 'create' method
model = ModelCatalog.create("publaynet_fast")




app = FastAPI()

# Load the model using the 'create' method
model = ModelCatalog.create("publaynet_fast")

# Initialize the pipeline
pipe = DoctectionPipe(model=model)

# Define compliance rules
def check_compliance(doc):
    issues = []

    # Check for title page
    if not doc.contains("Title Page"):
        issues.append("Title Page is missing.")

    # Check for font size
    if not doc.is_font_size(12):
        issues.append("Incorrect font size. Should be 12pt.")

    # Check for margins
    if not doc.has_margins(40, 25):
        issues.append("Incorrect margins.")

    # Check for centered page numbering
    if not doc.has_centered_page_numbers():
        issues.append("Page numbering is not centered.")

    # Check Abstract length (max 500 words or 1 page)
    abstract = doc.get_section("Abstract")
    if abstract:
        word_count = abstract.get_word_count()
        if word_count > 500 or abstract.is_more_than_one_page():
            issues.append(f"Abstract is too long: {word_count} words or more than one page.")
    else:
        issues.append("Abstract is missing.")

    return issues

# API endpoint to process document uploads
@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    # Save the uploaded file
    file_location = f"temp_files/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    # Process the document
    try:
        report = process_document(file_location)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Document processing failed.")
    finally:
        os.remove(file_location)

    # Return the compliance report
    return {"compliance_report": report}

def process_document(file_path):
    pages = pipe(file_path)
    doc = Page(pages)

    # Check compliance
    compliance_report = check_compliance(doc)

    return compliance_report

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
     



# Load the model using the 'create' method
model = ModelCatalog.create("publaynet_fast")




app = FastAPI()

# Load the model using the 'create' method
model = ModelCatalog.create("publaynet_fast")

# Initialize the pipeline
pipe = DoctectionPipe(model=model)

# Define compliance rules
def check_compliance(doc):
    issues = []

    # Check for title page
    if not doc.contains("Title Page"):
        issues.append("Title Page is missing.")

    # Check for font size
    if not doc.is_font_size(12):
        issues.append("Incorrect font size. Should be 12pt.")

    # Check for margins
    if not doc.has_margins(40, 25):
        issues.append("Incorrect margins.")

    # Check for centered page numbering
    if not doc.has_centered_page_numbers():
        issues.append("Page numbering is not centered.")

    # Check Abstract length (max 500 words or 1 page)
    abstract = doc.get_section("Abstract")
    if abstract:
        word_count = abstract.get_word_count()
        if word_count > 500 or abstract.is_more_than_one_page():
            issues.append(f"Abstract is too long: {word_count} words or more than one page.")
    else:
        issues.append("Abstract is missing.")

    return issues

# API endpoint to process document uploads
@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    # Save the uploaded file
    file_location = f"temp_files/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    # Process the document
    try:
        report = process_document(file_location)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Document processing failed.")
    finally:
        os.remove(file_location)

    # Return the compliance report
    return {"compliance_report": report}

def process_document(file_path):
    pages = pipe(file_path)
    doc = Page(pages)

    # Check compliance
    compliance_report = check_compliance(doc)

    return compliance_report

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
     

!pip install fastapi uvicorn # Install fastapi and uvicorn in a separate cell

!pip install deepdoctection[full]  # Install deepdoctection with all necessary dependencies

import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from deepdoctection import ModelCatalog, DoctectionPipe, Page # Use ModelCatalog instead of ModelZoo

# ... rest of your code ...

# Load the model using the 'create' method
model = ModelCatalog.create("publaynet_fast")




app = FastAPI()

# Load the model using the 'create' method
model = ModelCatalog.create("publaynet_fast")

# Initialize the pipeline
pipe = DoctectionPipe(model=model)

# Define compliance rules
def check_compliance(doc):
    issues = []

    # Check for title page
    if not doc.contains("Title Page"):
        issues.append("Title Page is missing.")

    # Check for font size
    if not doc.is_font_size(12):
        issues.append("Incorrect font size. Should be 12pt.")

    # Check for margins
    if not doc.has_margins(40, 25):
        issues.append("Incorrect margins.")

    # Check for centered page numbering
    if not doc.has_centered_page_numbers():
        issues.append("Page numbering is not centered.")

    # Check Abstract length (max 500 words or 1 page)
    abstract = doc.get_section("Abstract")
    if abstract:
        word_count = abstract.get_word_count()
        if word_count > 500 or abstract.is_more_than_one_page():
            issues.append(f"Abstract is too long: {word_count} words or more than one page.")
    else:
        issues.append("Abstract is missing.")

    return issues

# API endpoint to process document uploads
@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    # Save the uploaded file
    file_location = f"temp_files/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    # Process the document
    try:
        report = process_document(file_location)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Document processing failed.")
    finally:
        os.remove(file_location)

    # Return the compliance report
    return {"compliance_report": report}

def process_document(file_path):
    pages = pipe(file_path)
    doc = Page(pages)

    # Check compliance
    compliance_report = check_compliance(doc)

    return compliance_report

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
     

!pip install fastapi uvicorn # Install fastapi and uvicorn in a separate cell

!pip install deepdoctection[full]  # Install deepdoctection with all necessary dependencies

import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from deepdoctection import ModelCatalog, DoctectionPipe, Page # Use ModelCatalog

# ... rest of your code ...

# Load the model using the 'create' method
model = ModelCatalog.create("publaynet_fast")




app = FastAPI()

# Load the model using the 'create' method
model = ModelCatalog.create("publaynet_fast")

# Initialize the pipeline
pipe = DoctectionPipe(model=model)

# Define compliance rules
def check_compliance(doc):
    issues = []

    # Check for title page
    if not doc.contains("Title Page"):
        issues.append("Title Page is missing.")

    # Check for font size
    if not doc.is_font_size(12):
        issues.append("Incorrect font size. Should be 12pt.")

    # Check for margins
    if not doc.has_margins(40, 25):
        issues.append("Incorrect margins.")

    # Check for centered page numbering
    if not doc.has_centered_page_numbers():
        issues.append("Page numbering is not centered.")

    # Check Abstract length (max 500 words or 1 page)
    abstract = doc.get_section("Abstract")
    if abstract:
        word_count = abstract.get_word_count()
        if word_count > 500 or abstract.is_more_than_one_page():
            issues.append(f"Abstract is too long: {word_count} words or more than one page.")
    else:
        issues.append("Abstract is missing.")

    return issues

# API endpoint to process document uploads
@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    # Save the uploaded file
    file_location = f"temp_files/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    # Process the document
    try:
        report = process_document(file_location)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Document processing failed.")
    finally:
        os.remove(file_location)

    # Return the compliance report
    return {"compliance_report": report}

def process_document(file_path):
    pages = pipe(file_path)
    doc = Page(pages)

    # Check compliance
    compliance_report = check_compliance(doc)

    return compliance_report

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
     
