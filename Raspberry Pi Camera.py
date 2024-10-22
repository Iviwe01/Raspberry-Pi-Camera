import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter.ttk import Progressbar
from picamera2 import Picamera2
import threading
from PIL import Image, ImageTk, ImageEnhance, ImageOps, ImageFilter
import firebase_admin
from firebase_admin import credentials, storage
import os
import logging

class CameraApp:
    def __init__(self, master):
        # Initialize the main window
        self.master = master
        master.title("Raspberry Pi Camera")
        master.geometry("800x1000")
        master.configure(bg="#e0f7fa")

        # Setup logging for debugging and error tracking
        logging.basicConfig(filename='camera_app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

        # Create and pack the GUI elements using grid layout
        self.label = tk.Label(master, text="Raspberry Pi Camera Control", bg="#e0f7fa", font=("Helvetica", 20, "bold"))
        self.label.grid(row=0, column=0, columnspan=2, pady=20)

        # Button to start/stop the camera preview
        self.start_preview_button = tk.Button(master, text="Start Preview", command=self.toggle_preview, bg="#00796b", fg="white", font=("Helvetica", 16, "bold"))
        self.start_preview_button.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

        # Button to capture an image
        self.capture_button = tk.Button(master, text="Capture Image", command=self.capture_image, bg="#00796b", fg="white", font=("Helvetica", 16, "bold"))
        self.capture_button.grid(row=1, column=1, sticky="ew", padx=10, pady=10)

        # Button to apply filters to the captured image
        self.filter_button = tk.Button(master, text="Apply Filter", command=self.apply_filter, bg="#ffb300", fg="white", font=("Helvetica", 16, "bold"))
        self.filter_button.grid(row=2, column=0, sticky="ew", padx=10, pady=10)

        # Button to open settings
        self.settings_button = tk.Button(master, text="Settings", command=self.open_settings, bg="#ffb300", fg="white", font=("Helvetica", 16, "bold"))
        self.settings_button.grid(row=2, column=1, sticky="ew", padx=10, pady=10)

        # Button to quit the application
        self.quit_button = tk.Button(master, text="Quit", command=self.confirm_quit, bg="#d32f2f", fg="white", font=("Helvetica", 16, "bold"))
        self.quit_button.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        # Label to display status messages
        self.status_label = tk.Label(master, text="", bg="#e0f7fa", font=("Helvetica", 14))
        self.status_label.grid(row=4, column=0, columnspan=2, pady=10)

        # Label to display the captured image
        self.image_label = tk.Label(master, bg="#e0f7fa")
        self.image_label.grid(row=5, column=0, columnspan=2, pady=10)

        # Progress bar for uploading images
        self.progress_bar = Progressbar(master, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.progress_bar.grid(row=6, column=0, columnspan=2, pady=10)

        # Initialize Firebase for image storage
        self.initialize_firebase()

        # Initialize the camera
        self.camera = Picamera2()
        self.camera.configure(self.camera.create_preview_configuration(main={"size": (640, 480)}))
        self.camera.start()

        # Create a canvas for the camera preview
        self.preview_canvas = tk.Canvas(master, width=640, height=480, bg="black")
        self.preview_canvas.grid(row=7, column=0, columnspan=2, pady=10)

        self.image_id = None
        self.previewing = False
        self.last_captured_image = None
        self.loading_indicator = None

    def initialize_firebase(self):
        """Initialize Firebase storage."""
        try:
            service_account_key_path = './serviceAccountKey.json'
            cred = credentials.Certificate(service_account_key_path)
            firebase_admin.initialize_app(cred, {
                'storageBucket': 'camera-what-what-940f1.appspot.com'
            })
            self.bucket = storage.bucket()
            logging.info("Firebase initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize Firebase: {str(e)}")
            messagebox.showerror("Firebase Error", f"Failed to initialize Firebase: {str(e)}")

    def toggle_preview(self):
        """Toggle the camera preview on and off."""
        if self.previewing:
            self.previewing = False
            self.start_preview_button.config(text="Start Preview")
            self.preview_canvas.delete("all")
        else:
            self.previewing = True
            self.start_preview_button.config(text="Stop Preview")
            self.update_preview()

    def update_preview(self):
        """Update the camera preview with the latest image."""
        if self.previewing:
            raw_image = self.camera.capture_array()
            img = Image.fromarray(raw_image)
            img = img.convert("RGB")
            img.thumbnail((640, 480))

            img_tk = ImageTk.PhotoImage(img)
            if self.image_id:
                self.preview_canvas.delete(self.image_id)
            self.image_id = self.preview_canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
            self.preview_canvas.image = img_tk

            self.preview_canvas.after(100, self.update_preview)

    def capture_image(self):
        """Capture an image and save it to the specified location."""
        self.show_loading_indicator("Capturing image...")
        self.status_label.config(text="Capturing image...")
        self.master.update()

        # Visual feedback (flash effect)
        self.master.config(bg="white")
        self.master.after(100, lambda: self.master.config(bg="#e0f7fa"))

        filename = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg")])
        if filename:
            try:
                raw_image = self.camera.capture_array()
                img = Image.fromarray(raw_image)
                img = img.convert("RGB")
                img.save(filename)
                self.last_captured_image = filename

                self.status_label.config(text=f"Image saved as {os.path.basename(filename)}")
                logging.info(f"Image saved as {os.path.basename(filename)}")

                # Upload in a separate thread to avoid freezing the UI
                threading.Thread(target=self.upload_to_firebase, args=(filename,)).start()
                self.display_image(filename)

            except Exception as e:
                logging.error(f"Failed to capture image: {str(e)}")
                self.status_label.config(text=f"Error capturing image: {str(e)}")
                messagebox.showerror("Capture Error", f"Failed to capture image: {str(e)}")
        self.hide_loading_indicator()

    def apply_filter(self):
        """Apply a selected filter to the last captured image with preview."""
        if not self.last_captured_image:
            messagebox.showerror("No Image", "Please capture an image first.")
            return

        img = Image.open(self.last_captured_image)
        filter_choice = simpledialog.askstring("Choose Filter", "Enter filter: grayscale, sepia, invert, blur, sharpen, edge")

        preview_img = img.copy()
        if filter_choice == "grayscale":
            preview_img = preview_img.convert("L").convert("RGB")
        elif filter_choice == "sepia":
            sepia_filter = ImageEnhance.Color(preview_img)
            preview_img = sepia_filter.enhance(0.3)
        elif filter_choice == "invert":
            preview_img = ImageOps.invert(preview_img)
        elif filter_choice == "blur":
            preview_img = preview_img.filter(ImageFilter.BLUR)
        elif filter_choice == "sharpen":
            preview_img = preview_img.filter(ImageFilter.SHARPEN)
        elif filter_choice == "edge":
            preview_img = preview_img.filter(ImageFilter.FIND_EDGES)
        else:
            messagebox.showerror("Invalid Filter", "Invalid filter selected.")
            return

        self.display_image_preview(preview_img)

        if messagebox.askyesno("Apply Filter", f"Do you want to apply the {filter_choice} filter?"):
            filename = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg")])
            if filename:
                preview_img.save(filename)
                self.display_image(filename)
                self.last_captured_image = filename
                self.status_label.config(text=f"Image saved with {filter_choice} filter.")
                logging.info(f"Image saved with {filter_choice} filter.")

    def upload_to_firebase(self, file_path):
        """Upload the captured image to Firebase."""
        self.show_loading_indicator("Uploading to Firebase...")
        try:
            self.progress_bar.start()
            blob = self.bucket.blob(f'images/{os.path.basename(file_path)}')
            blob.upload_from_filename(file_path)
            blob.make_public()

            self.progress_bar.stop()
            self.progress_bar['value'] = 100
            self.status_label.config(text=f"Image uploaded to Firebase as {os.path.basename(file_path)}")
            logging.info(f"Image uploaded to Firebase as {os.path.basename(file_path)}")

        except Exception as e:
            self.progress_bar.stop()
            logging.error(f"Error uploading to Firebase: {str(e)}")
            self.status_label.config(text=f"Error uploading to Firebase: {str(e)}")
            messagebox.showerror("Upload Error", f"Failed to upload image: {str(e)}")
        finally:
            self.progress_bar['value'] = 0
            self.hide_loading_indicator()

    def display_image(self, file_path):
        """Display the captured image in the GUI."""
        try:
            img = Image.open(file_path)
            img.thumbnail((250, 250))
            img = ImageTk.PhotoImage(img)
            self.image_label.config(image=img)
            self.image_label.image = img
        except Exception as e:
            logging.error(f"Error displaying image: {str(e)}")
            self.status_label.config(text=f"Error displaying image: {str(e)}")

    def display_image_preview(self, img):
        """Display the preview of the filtered image in the GUI."""
        img.thumbnail((250, 250))
        img = ImageTk.PhotoImage(img)
        self.image_label.config(image=img)
        self.image_label.image = img

    def open_settings(self):
        """Open the settings window for brightness and contrast adjustments."""
        settings_window = tk.Toplevel(self.master)
        settings_window.title("Settings")
        settings_window.geometry("300x200")

        brightness_label = tk.Label(settings_window, text="Brightness (0-100):")
        brightness_label.pack(pady=10)
        self.brightness_entry = tk.Entry(settings_window)
        self.brightness_entry.pack(pady=5)

        contrast_label = tk.Label(settings_window, text="Contrast (0-100):")
        contrast_label.pack(pady=10)
        self.contrast_entry = tk.Entry(settings_window)
        self.contrast_entry.pack(pady=5)

        save_button = tk.Button(settings_window, text="Save Settings", command=self.save_settings)
        save_button.pack(pady=20)

    def save_settings(self):
        """Save the brightness and contrast settings (placeholder for future implementation)."""
        brightness = self.brightness_entry.get()
        contrast = self.contrast_entry.get()
        messagebox.showinfo("Settings Saved", f"Brightness: {brightness}\nContrast: {contrast}")

    def show_loading_indicator(self, message):
        """Show a loading indicator with a message."""
        self.loading_indicator = tk.Toplevel(self.master)
        self.loading_indicator.title("Loading")
        self.loading_indicator.geometry("200x100")
        self.loading_indicator.transient(self.master)
        self.loading_indicator.grab_set()
        
        label = tk.Label(self.loading_indicator, text=message, font=("Helvetica", 14))
        label.pack(pady=20)

    def hide_loading_indicator(self):
        """Hide the loading indicator."""
        if self.loading_indicator:
            self.loading_indicator.destroy()

    def confirm_quit(self):
        """Confirm exit and close the application."""
        if messagebox.askokcancel("Quit", "Do you really want to quit?"):
            self.camera.close()  # Ensure the camera is closed before quitting
            self.master.destroy()

def main():
    """Main function to run the application."""
    root = tk.Tk()
    app = CameraApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()