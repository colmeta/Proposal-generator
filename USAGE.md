# Usage Guide

## Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file with your OpenAI API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Running the Application

#### Option A: Web Interface (Recommended)
```bash
streamlit run app.py
```
This will open a user-friendly web interface in your browser.

#### Option B: Command Line Interface
```bash
python main.py
```
This provides an interactive command-line experience.

## Features

### 1. Document Generation from Ideas
- Select your target funder (Gates Foundation, World Bank, WHO, Fortune 500)
- Choose document type (Proposal, Concept Note, Pitch Deck, Executive Summary)
- Answer intelligent questions about your project
- Get a professional, human-written document

### 2. Document Analysis & Enhancement
- Upload your existing document
- Get a detailed gap analysis
- Identify missing critical elements
- Generate an enhanced version that fills gaps

### 3. Intelligent Questioning
- View all questions before starting
- Understand why each question matters
- Get funder-specific questions tailored to your target

## Workflow Examples

### Example 1: Creating a New Proposal for Gates Foundation

1. Run `streamlit run app.py`
2. In sidebar, select "Bill & Melinda Gates Foundation"
3. Select "Full Proposal"
4. Enter your OpenAI API key
5. Go to "New Document" tab
6. Answer all questions about your project
7. Click "Generate Document"
8. Review and download your proposal

### Example 2: Enhancing an Existing Document

1. Run `streamlit run app.py`
2. Select your funder and document type
3. Go to "Analyze Existing" tab
4. Upload your existing document (.txt format)
5. Click "Analyze Document" to see gaps
6. Provide additional information for critical gaps
7. Click "Generate Enhanced Document"
8. Review changes and download

## Tips for Best Results

1. **Be Specific**: Provide detailed, specific answers to questions
2. **Include Data**: Mention numbers, statistics, and evidence where possible
3. **Think Long-term**: Consider sustainability and scalability
4. **Be Honest**: Accurate information leads to better proposals
5. **Review Generated Content**: Always review and customize the generated document

## Document Types Explained

### Full Proposal
- Comprehensive document with all sections
- Best for formal funding applications
- Typically 10-20 pages

### Concept Note
- Shorter, high-level overview
- Good for initial submissions
- Typically 2-5 pages

### Pitch Deck
- Presentation format
- Good for meetings and presentations
- Typically 10-15 slides

### Executive Summary
- Brief overview document
- Good for quick reviews
- Typically 1-2 pages

## Funder-Specific Guidance

### Bill & Melinda Gates Foundation
- Emphasize evidence-based solutions
- Include gender equity considerations
- Focus on scalability and replication
- Provide clear impact metrics

### World Bank
- Include economic analysis
- Show government engagement
- Address environmental impacts
- Demonstrate social inclusion

### World Health Organization
- Focus on public health outcomes
- Show health system integration
- Include capacity building plans
- Provide epidemiological context

### Fortune 500 Companies
- Align with business objectives
- Show brand value
- Demonstrate ROI
- Highlight partnership opportunities

## Troubleshooting

### API Key Issues
- Make sure your OpenAI API key is valid
- Check that you have sufficient credits
- Ensure the key is entered correctly in .env file

### Document Generation Errors
- Provide more detailed answers to questions
- Check your internet connection
- Try generating again if it fails

### File Upload Issues
- Currently only .txt files are supported
- Convert .docx or .pdf to .txt first
- Ensure file encoding is UTF-8

## Support

For issues or questions, please check:
1. Your OpenAI API key is valid
2. All dependencies are installed
3. You're using Python 3.8 or higher

