# **DOU Engineering Analysis Automation**

This repository contains a Python-based automation system designed to extract and analyze publications from the Brazilian Official Gazette (DOU) for identifying engineering works and services, based on the guidelines of Law 14.133/2021. The tool also generates reports and sends emails with the results for daily monitoring.

---

## **Features**
- **Data Extraction**: Scrapes DOU publications based on a specific date, targeting relevant sections and filtering for content related to engineering works and services.
- **Automated Analysis**: Uses AI (Google Gemini) to classify each publication as engineering-related or not, providing justification and summary.
- **Report Generation**: Produces HTML and PDF reports summarizing the analysis results.
- **Email Notification**: Sends automated emails with the generated report attached.
- **Proxy Support**: Includes proxy configuration for secure data fetching.

---

## **Requirements**
- **Python Version**: Python 3.9+
- **Packages**:
  - `requests`
  - `beautifulsoup4`
  - `dotenv`
  - `google.generativeai`
  - `tqdm`
  - `pandas`
  - `pdfkit`
  - `fuzzywuzzy`
  - `smtplib`
  - `email`

---

## **Setup Instructions**

### **1. Clone the Repository**
```bash
git clone https://github.com/yourusername/dou-engineering-analysis.git
cd dou-engineering-analysis
```

### **2. Install Dependencies**
Use pip to install the required packages:

```bash
pip install -r requirements.txt
```

### **3. Configure Environment Variables**
Create a `.env` file in the root directory and add the following keys:

```dotenv
GEMINI_KEY=your_google_gemini_api_key
GSHEET_CRED=your_google_sheets_credential_path
GSHEET_KEY_SHEET=your_google_sheets_key
USUARIO_PROXY=your_proxy_username
PASS_PROXY=your_proxy_password
ENDERECO_PROXY=your_proxy_address
SENDER_EMAIL=your_email_address
EMAIL_PASSWORD=your_email_password
RECEIVER_EMAIL=primary_recipient_email
```

### **Install PDF Rendering Engine**
Install `wkhtmltopdf` to enable HTML-to-PDF conversion:

```bash
sudo apt-get install wkhtmltopdf
```

## **Usage**

### Run the Main Script
Run the following command to start the analysis:

```bash
python dou.py
```

The script will:
- Extract publications for the specified date.
- Analyze the content using Google Gemini AI.
- Generate detailed HTML and PDF reports.
- Send the report via email to the specified recipients.

### Customize the Date
To analyze a specific date, modify the `date` variable in `dou.py`:
```python
date = "30/01/2025"  # Example date (DD/MM/YYYY)
```

## Project Structure
- `dou.py`: Main script orchestrating the workflow.
- `extrair_dou_comaer.py`: Handles data scraping from the DOU website.
- `gemini.py`: Interfaces with Google Gemini AI for text analysis.
- `helpers.py`: Contains utility functions for normalization, similarity calculation, email sending, and PDF generation.
- `template_saida.html`: HTML template used for report generation.

## Key Functionalities
### 1. Content Extraction
Extracts publication data (title, content, organization, etc.) from the DOU website using `BeautifulSoup` and `requests`.
### 2. AI-Based Analysis
Uses Google Gemini to determine if a publication relates to engineering works or services. For each publication, it provides:
- A verdict: "Yes" or "No".
- A justification for the classification.
- A brief summary of the publication.
### 3. Report Generation
Creates:
- HTML Reports: Styled for easy viewing.
- PDF Reports: Formatted for official use.
### 4. Email Notification
Sends the PDF report via email to specified recipients.
