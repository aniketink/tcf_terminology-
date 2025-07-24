import customtkinter
import wikipedia
import requests
import xml.etree.ElementTree as ET
import threading
from bs4 import BeautifulSoup # NEW IMPORT for HTML parsing

# --- BACKEND DEFINITION-FETCHING LOGIC ---

def get_medlineplus_definition(term):
    """
    Fetches a definition from the MedlinePlus Connect API, an authoritative source
    from the U.S. National Library of Medicine (NLM), and cleans its HTML output.

    Args:
        term (str): The term to look up.

    Returns:
        str: The definition from MedlinePlus (plain text), or None if not found.
    """
    base_url = "https://wsearch.nlm.nih.gov/ws/query"
    params = {
        'db': 'healthTopics',
        'term': term,
        'rettype': 'brief'
    }
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status() # Check for HTTP errors

        # Parse the XML response
        root = ET.fromstring(response.content)
        
        # Find the 'snippet' element, which contains the definition, often as HTML
        snippet_element = root.find('.//content[@name="FullSummary"]')

        if snippet_element is not None and snippet_element.text:
            raw_html_content = snippet_element.text.strip()
            
            # --- START OF NEW HTML CLEANING LOGIC ---
            soup = BeautifulSoup(raw_html_content, 'html.parser')
            
            # Replace <li> tags with a bullet point and newline for readability
            for li in soup.find_all('li'):
                li.insert(0, '\n• ')
            
            # Extract plain text, using a space as separator between elements
            # and stripping leading/trailing whitespace.
            clean_text = soup.get_text(separator=' ', strip=True)
            # --- END OF NEW HTML CLEANING LOGIC ---

            return f"Source: MedlinePlus (U.S. National Library of Medicine)\n\n{clean_text}"
        else:
            # This means the API call was successful, but the term wasn't in the dictionary
            return None

    except requests.exceptions.RequestException:
        # Network or HTTP error
        return "MedlinePlus service is currently unavailable. Please check your internet connection."
    except ET.ParseError:
        return "Failed to parse the response from MedlinePlus."
    except Exception as e:
        return f"An unexpected error occurred with the MedlinePlus service: {e}"

# We still need the Wikipedia function as a fallback (no changes needed here)
def get_wikipedia_definition(term):
    """Fetches a summary for a term from Wikipedia."""
    try:
        summary = wikipedia.summary(term, sentences=4, auto_suggest=False)
        return f"Source: Wikipedia\n\n{summary}"
    except wikipedia.exceptions.PageError:
        return f"Sorry, the term '{term}' could not be found in MedlinePlus or Wikipedia."
    except wikipedia.exceptions.DisambiguationError as e:
        # Show a few options for disambiguation errors
        return (f"The term '{term}' is ambiguous on Wikipedia. "
                f"Please be more specific. Some options might be: {', '.join(e.options[:4])}...")
    except Exception as e:
        return f"An error occurred while fetching from Wikipedia: {e}"

# --- GUI APPLICATION CLASS (NO MAJOR CHANGES NEEDED HERE, just ensure it calls the updated backend) ---

class MedicalDictApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Setup ---
        self.title("The Carcino Foundation")
        self.geometry("700x550")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        customtkinter.set_appearance_mode("System")  # Can be "System", "Dark", "Light"

        # --- Widget Creation ---
        self.main_label = customtkinter.CTkLabel(self, text="Carcino Term Finder", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.main_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        self.entry_frame = customtkinter.CTkFrame(self)
        self.entry_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.entry_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = customtkinter.CTkEntry(self.entry_frame, placeholder_text="Enter a term")
        self.search_entry.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")
        # Allow pressing Enter to search
        self.search_entry.bind("<Return>", self.search_event)

        self.search_button = customtkinter.CTkButton(self.entry_frame, text="Search", command=self.search_event)
        self.search_button.grid(row=0, column=1, padx=(5, 10), pady=10)

        self.result_textbox = customtkinter.CTkTextbox(self, wrap="word", font=("Arial", 14), state="disabled")
        self.result_textbox.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="nsew")

        self.disclaimer_label = customtkinter.CTkLabel(self, text="Disclaimer: nah nothing here", font=customtkinter.CTkFont(size=10))
        self.disclaimer_label.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="ew")
        
    def search_event(self, event=None):
        """Starts the search process in a new thread to keep the GUI responsive."""
        term = self.search_entry.get()
        if not term:
            # Provide feedback if no term is entered
            self.result_textbox.configure(state="normal")
            self.result_textbox.delete("1.0", "end")
            self.result_textbox.insert("1.0", "Please enter a term to search.")
            self.result_textbox.configure(state="disabled")
            return

        # Disable button and entry to prevent multiple searches
        self.search_button.configure(state="disabled", text="Searching...")
        self.search_entry.configure(state="disabled")

        # Clear previous results and show "Searching..." message
        self.result_textbox.configure(state="normal")
        self.result_textbox.delete("1.0", "end")
        self.result_textbox.insert("1.0", f"Searching for '{term}'...")
        self.result_textbox.configure(state="disabled")
        
        # Run the actual search in a separate thread to avoid freezing the GUI
        threading.Thread(target=self.perform_search, args=(term,)).start()

    def perform_search(self, term):
        """The actual search logic that runs in the background."""
        # 1. Try the best source first: MedlinePlus
        definition = get_medlineplus_definition(term)

        # 2. If MedlinePlus doesn't have it (returns None), fall back to Wikipedia
        if definition is None:
            definition = get_wikipedia_definition(term)
        
        # 3. Update the GUI with the result using .after() to ensure it's on the main thread
        self.after(0, self.update_gui_with_result, definition)

    def update_gui_with_result(self, definition):
        """Updates the GUI elements on the main thread."""
        self.result_textbox.configure(state="normal") # Enable writing
        self.result_textbox.delete("1.0", "end")
        self.result_textbox.insert("1.0", definition)
        self.result_textbox.configure(state="disabled") # Disable writing

        # Re-enable the search button and entry
        self.search_button.configure(state="normal", text="Search")
        self.search_entry.configure(state="normal")


if __name__ == "__main__":
    app = MedicalDictApp()
    app.mainloop()
