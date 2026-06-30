# Import the main FastAPI class to create your application instance
from fastapi import FastAPI, UploadFile, File, HTTPException
# Import StaticFiles to serve local folders (like images/PDFs) directly via a URL
from fastapi.staticfiles import StaticFiles
# Import Python's built-in OS module to handle file paths and directory creation
import os
# Import shutil (shell utilities) for efficient file copying operations
import shutil

# Initialize your FastAPI application instance
app = FastAPI()

# ==========================================
# Step-1: Ensure uploads folder exists
# ==========================================

# Define the string name of the folder where uploaded files will be stored
UPLOAD_DIR = "uploads"

# Check if the folder does NOT exist yet on the server's hard drive
if not os.path.exists(UPLOAD_DIR):
    # Create the folder automatically so the app doesn't crash later when saving files
    os.makedirs(UPLOAD_DIR)

# ==========================================
# STEP-2: Static file set-up
# ==========================================

# app.mount() maps a URL path to a physical folder on your disk.
# "/files" is the URL prefix. Anyone going to http://127.0.0.1:8000/files/image.png
# will download 'image.png' directly from your local UPLOAD_DIR folder.
# 'name="files"' is an internal identifier FastAPI uses for URL reversing.
app.mount("/files", StaticFiles(directory=UPLOAD_DIR), name="files")

# ==========================================
# Step-3: Upload file api
# ==========================================

# Define a POST route because the client is sending/uploading data to the server
@app.post("/upload")
def upload_file(file: UploadFile = File(...)):
    """
    UploadFile: A FastAPI class that handles files smartly. It stores small files in 
    memory and streams large files to disk so your server's RAM doesn't overflow.
    File(...): The ellipsis (...) means this file argument is strictly required.
    """
    # Extract the original name of the file the user uploaded (e.g., "resume.pdf")
    filename = file.filename
    
    # Check if the user hit upload without actually selecting a file
    if not filename:
        # Halt execution and return a 400 Bad Request error to the client
        raise HTTPException(status_code=400, detail="File not selected")
        
    # Combine the upload directory folder path and the filename safely for any OS
    # (e.g., Windows uses backslashes '\', Mac/Linux use forward slashes '/')
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # 'with' handles opening and automatically closing the file stream, even if errors happen.
    # "wb" means Write Binary mode, which is required for saving non-text files like images/PDFs.
    with open(file_path, "wb") as buffer:
        # file.file is the underlying Python file-like object.
        # shutil.copyfileobj streams chunks of data from the upload straight to your hard drive.
        shutil.copyfileobj(file.file, buffer)

    # Return a success JSON response after the 'with' block completes and closes the file.
    return {
        "message": "File Uploaded successfully",
        "fileName": filename,
        # Hardcoded URL pointing to the static file route we set up in Step 2
        "file_url": f"http://127.0.0.1:8000/files/{filename}"
    }
    
# ==========================================
# Step-4: Get File URL API
# ==========================================

# A GET route that uses a path parameter {filename} so users can search for specific files
@app.get("/files/{filename}")
def get_file(filename: str):
    # Construct the full local system path to check if the file actually exists on disk
    file_path = os.path.join(UPLOAD_DIR, filename)

    # If the file isn't in our uploads folder, return a standard 404 Not Found error
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # If it exists, return the live URL where the client can view/download it
    return {
        "file_url": f"http://127.0.0.1:8000/files/{filename}"
    }

# ==========================================
# Step-5: Home / Root API Route
# ==========================================

# The base landing page URL (http://127.0.0.1:8000/) to quickly test if the server is alive
@app.get("/")
def home():
    return {
        "message": "File Uploaded api Running"
    }
