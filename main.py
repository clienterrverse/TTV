import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

# Ensure the src directory is in the sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from TextToVideo import TextToVideo  # Ensure this import path is correct


class TextToVideoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Text to Video Converter")
        self.root.geometry("500x400")
        self.create_widgets()

    def create_widgets(self):
        # Input text label
        input_text_label = tk.Label(self.root, text="Enter text or select an input file:")
        input_text_label.pack(pady=(20, 5))

        # Input text area
        self.input_text = tk.Text(self.root, height=10, width=60)
        self.input_text.pack(padx=20, pady=5)

        # Select input file button
        self.select_file_button = tk.Button(self.root, text="Select Input File", command=self.choose_input_file)
        self.select_file_button.pack(pady=10)

        # Output file name label and entry
        self.output_file_label = tk.Label(self.root, text="Output File Name (without extension):")
        self.output_file_label.pack()

        self.output_file_entry = tk.Entry(self.root, width=50)
        self.output_file_entry.pack(pady=5)

        # Convert button
        self.convert_button = tk.Button(self.root, text="Convert", command=self.convert)
        self.convert_button.pack(pady=20)

    def choose_input_file(self):
        filetypes = [("Text files", "*.txt"), ("All files", "*.*")]
        input_file = filedialog.askopenfilename(filetypes=filetypes)
        if input_file:
            try:
                with open(input_file, "r") as f:
                    text = f.read()
                self.input_text.delete("1.0", tk.END)
                self.input_text.insert(tk.END, text)
            except Exception as e:
                messagebox.showerror("Error", f"Could not read file: {e}")

    def convert(self):
        text = self.input_text.get("1.0", tk.END).strip()
        output_file = self.output_file_entry.get().strip()

        if not text:
            messagebox.showerror("Error", "Input text is empty.")
            return

        if not output_file:
            messagebox.showerror("Error", "Output file name is empty.")
            return

        try:
            ttv = TextToVideo(text, output_file + ".mp4")
            ttv.process_video_elements()
            ttv.save_video()
            messagebox.showinfo("Success", f"Video saved as '{output_file}.mp4'.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")


def main():
    root = tk.Tk()
    app = TextToVideoGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
