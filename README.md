# Carcino Term Finder

A modern desktop application for looking up medical and cancer-related terms. This tool provides clear, authoritative definitions from trusted sources through a user-friendly and responsive interface.

<img width="2048" height="1280" alt="Screenshot 2025-07-24 at 4 36 46 PM" src="https://github.com/user-attachments/assets/bfcfb210-b6c3-43aa-b925-bb2882d3f305" />

## Features

-   **Modern User Interface**: Built with `CustomTkinter` for a clean, professional look that supports both **Light and Dark modes**.
-   **Authoritative Definitions**: Utilizes a hybrid search strategy for the best results:
    1.  **Primary Source**: First queries the **MedlinePlus API** from the U.S. National Library of Medicine (NLM) for authoritative medical definitions.
    2.  **Fallback Source**: If no definition is found, it seamlessly falls back to **Wikipedia** for broader coverage.
-   **Intelligent Autocomplete**: Suggests relevant medical terms as you type, helping you find information faster and more accurately. The suggestions are powered by a curated corpus of cancer-related terms.
-   **Responsive & Non-Blocking**: The application uses `threading` to perform network requests in the background, ensuring the UI never freezes while searching for a term.
-   **Smart Text Cleaning**: Definitions from APIs are often returned in messy HTML format. The application uses `BeautifulSoup` to parse and clean this data, presenting only readable, well-formatted text to the user.

## Technology Stack

-   **Language**: Python 3
-   **GUI Framework**: [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
-   **API Interaction**: [Requests](https://pypi.org/project/requests/)
-   **Data Sources**:
    -   [MedlinePlus Connect API](https://medlineplus.gov/connect/service.html)
    -   [Wikipedia API](https://pypi.org/project/wikipedia/)
-   **HTML Parsing**: [BeautifulSoup4](https://pypi.org/project/beautifulsoup4/)

## Setup and Installation

Follow these steps to get the application running on your local machine.

### 1. Prerequisites

Make sure you have **Python 3.7 or higher** installed on your system.

