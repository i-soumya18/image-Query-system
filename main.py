import shutil
import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk, Image
from pathlib import Path
import os
import google.generativeai as genai
from api import value
import logging
import traceback
# Initialize logging configuration
log_format = '%(asctime)s - %(levelname)s - %(message)s'
log_file = 'app_log.log'

logging.basicConfig(filename=log_file, level=logging.INFO, format=log_format)


# Configure your API key here
genai.configure(api_key=value)

# Global list to store image file paths
image_file_paths = []

# Create 'image_upload' folder if it doesn't exist
upload_folder = 'image_upload'
if not os.path.exists(upload_folder):
    os.makedirs(upload_folder)

# Function to handle the image selection

# Function to handle the image selection
def select_images():
    try:
        global image_file_paths
        # Prompt the user to select multiple image files
        files = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=(
                ("Image files", "*.jpg;*.jpeg;*.png;*.gif;*.bmp;*.tiff"),
                ("All files", "*.*")
            )
        )
        if files:
            image_file_paths = list(files)
            save_images_to_folder(image_file_paths)

            # Log image upload activity with image names
            uploaded_images = [os.path.basename(img_path) for img_path in image_file_paths]
            logging.info(f"Uploaded {len(uploaded_images)} image(s): {', '.join(uploaded_images)}")

            display_images()  # Show image previews after selection
    except Exception as e:
        logging.error(f"Error occurred in select_images: {str(e)}")
        logging.error(traceback.format_exc())


# Function to save uploaded images to the 'image_upload' folder
def save_images_to_folder(image_paths):
    try:
        global image_file_paths
        for img_path in image_file_paths:
            img_name = os.path.basename(img_path)
            shutil.copyfile(img_path, os.path.join(upload_folder, img_name))
    except Exception as e:
        logging.error(f"Error occurred in save_images_to_folder: {str(e)}")
        logging.error(traceback.format_exc())

# Function to display the selected images as previews
def display_images():
    try:
        global image_file_paths

        # Clear any existing image previews
        for widget in image_frame.winfo_children():
            widget.destroy()

        # Display the selected images as previews in separate boxes
        for idx, img_path in enumerate(image_file_paths):
            img = Image.open(img_path)
            img = img.resize((100, 100))

            # Convert image to ImageTk format for display in Tkinter
            img = ImageTk.PhotoImage(img)

            img_label = tk.Label(image_frame, image=img)
            img_label.image = img
            img_label.grid(row=idx // 4, column=idx % 4, padx=5, pady=5)  # Display 4 images per row
    except Exception as e:
        logging.error(f"Error occurred in display_images: {str(e)}")
        logging.error(traceback.format_exc())



# Function to process the selected images and generate content
def process_images_and_generate_content():
    try:
        global image_file_paths

        # Get the user query from the entry box
        query = query_entry.get()

        # Validate that at least one image is selected
        if not image_file_paths:
            tk.messagebox.showerror("Error", "Please select at least one image.")
            return

        image_parts = [
            {
                "mime_type": "image/jpeg",
                "data": Path(img_path).read_bytes()
            } for img_path in image_file_paths
        ]

        # Set up the model and generation configuration
        generation_config = {
            "temperature": 0.4,
            "top_p": 1,
            "top_k": 32,
            "max_output_tokens": 4096,
        }

        model = genai.GenerativeModel(model_name="gemini-pro-vision",
                                      generation_config=generation_config)

        # Use the model to generate content based on the provided images and query
        prompt_parts = [
            query,
            *image_parts,
        ]

        response = model.generate_content(prompt_parts)

        # Display the generated content in the text box
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, response.text)
    except Exception as e:
        logging.error(f"Error occurred in process_images_and_generate_content: {str(e)}")
        logging.error(traceback.format_exc())
# Create the main window
root = tk.Tk()
root.title("Image Query System")

# Get screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Set window size and center it
window_width = int(screen_width * 0.41)
window_height = int(screen_height * 0.8)
x_coordinate = (screen_width - window_width) // 2
y_coordinate = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

root.configure(bg='light blue')

# Add padding and weight to rows and columns to adjust elements
root.grid_rowconfigure(5, weight=1)
root.grid_columnconfigure(2, weight=1)

# Add the Upload button for multiple images
upload_button = tk.Button(root, text="Upload Images", command=select_images, bg='light green')
upload_button.grid(row=0, column=0, padx=10, pady=10, sticky='w')

# Add the image frame to display image previews
image_frame = tk.Frame(root, bg='light blue')
image_frame.grid(row=0, column=1, padx=10, pady=10, sticky='w')

# Add the query entry box
query_label = tk.Label(root, text="Enter your query:", bg='light blue')
query_label.grid(row=1, column=0, sticky='w', padx=10)
query_entry = tk.Entry(root)
query_entry.grid(row=1, column=1, padx=10, pady=5, sticky='ew')

# Add the Submit button
submit_button = tk.Button(root, text="Submit", command=process_images_and_generate_content, bg='light green')
submit_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

# Add the result text box
result_label = tk.Label(root, text="Result:", bg='light blue')
result_label.grid(row=3, column=0, sticky='w', padx=10, pady=5)
result_text = tk.Text(root, width=50, height=20)
result_text.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')

# Run the main loop
root.mainloop()