# Django String Analyzer API

A robust Django REST API for comprehensive string analysis. It calculates metrics like length, word count, and character frequency, and includes a custom natural language filter for querying analyzed strings.

---

## 🌟 Key Features

* **String Analysis:** Calculates essential metrics for any input string, including:
    * Length, Word Count, and Unique Characters.
    * **Palindrome Check** (`is_palindrome`).
    * Detailed **Character Frequency Map**.
    * Unique **SHA-256 Hash** (used as the primary key).
* **Database Storage:** Analyzed strings are stored and indexed for fast retrieval.
* **Custom Natural Language Query:** Search and filter data using plain English (e.g., `palindromic strings that contain the first vowel`).

---

## 🛠️ Local Setup

To run this project locally, you'll need Python 3.8+ and pip.

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/YourUsername/Django-String-Analyzer-API.git](https://github.com/YourUsername/Django-String-Analyzer-API.git)
    cd Django-String-Analyzer-API
    ```

2.  **Setup Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    # (Note: You may need to create this file first: pip freeze > requirements.txt)
    ```

4.  **Run Migrations and Start Server:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver
    ```
    The API will be available at `http://127.0.0.1:8000/`.

---

## 🚀 API Endpoints

The primary endpoint is `/strings/`. All API requests should be sent to the base URL: `http://127.0.0.1:8000/strings/`.

| Method | URL | Action | Example Data (Body) |
| :--- | :--- | :--- | :--- |
| **POST** | `/strings/` | **Create & Analyze** a new string. | `{"value": "Hello World"}` |
| **GET** | `/strings/` | **List** all analyzed strings (supports query filters). | |
| **GET** | `/strings/{value}` | **Retrieve** the analysis by original string value. | `/strings/madam` |
| **DELETE** | `/strings/{value}` | **Delete** the entry by original string value. | `/strings/Hello%20Django` |

### ✨ Natural Language Filter

Use the dedicated endpoint to query data using human language:

| URL | Query Example |
| :--- | :--- |
| `/strings/filter-by-natural-language` | `?query=palindromic%20strings%20longer%20than%205` |
| `/strings/filter-by-natural-language` | `?query=single%20word%20entries%20that%20contain%20the%20letter%20z` |

---

## Next Steps

1.  **Generate `requirements.txt`:** If you haven't already, run `pip freeze > requirements.txt` to make setup easy for others.
2.  **Deployment:** Consider deploying to a free platform like **Render** or **Heroku** to make your API publicly accessible!
