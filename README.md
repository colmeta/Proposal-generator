# Professional Funding Proposal Generator

A sophisticated AI-powered system for generating professional, human-written quality proposals and documents for major funders including Fortune 500 companies, Bill & Melinda Gates Foundation, World Bank, and World Health Organization.

## Features

- **Document Analysis**: Analyzes existing documents and identifies gaps
- **Intelligent Questioning**: Asks targeted questions when users only have ideas
- **Multi-Document Generation**: Creates proposals, pitch decks, concept notes, executive summaries
- **Funder-Specific Templates**: Tailored for major international funders
- **Human-Like Writing**: Natural, professional tone that doesn't feel AI-generated
- **Gap Identification**: Automatically identifies missing elements in documents
- **Change Tracking**: Shows what will be changed/added to existing documents

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Web Interface (Recommended)
```bash
streamlit run app.py
```
Opens a user-friendly web interface in your browser with:
- Interactive forms for answering questions
- Document upload and analysis
- Real-time gap identification
- One-click document generation

### Command Line Interface
```bash
python main.py
```
Provides an interactive command-line experience.

### Quick Start Scripts
- **Windows**: Double-click `run.bat` or run it from command prompt
- **Linux/Mac**: Run `bash run.sh` or `chmod +x run.sh && ./run.sh`

## Configuration

Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Supported Funders

- Bill & Melinda Gates Foundation
- World Bank
- World Health Organization (WHO)
- Fortune 500 Companies

## Document Types

- **Full Proposal**: Comprehensive 10-20 page document with all sections
- **Concept Note**: Shorter 2-5 page high-level overview
- **Pitch Deck**: Presentation format for meetings (10-15 slides)
- **Executive Summary**: Brief 1-2 page overview document

## How It Works

1. **Select Your Funder**: Choose from Gates Foundation, World Bank, WHO, or Fortune 500
2. **Choose Document Type**: Pick the format that best fits your needs
3. **Provide Information**: 
   - Answer intelligent questions if starting from scratch
   - OR upload existing documents for analysis and enhancement
4. **Get Results**: Receive a professional, human-written document tailored to your funder

## Key Features Explained

### Intelligent Question Generation
The system asks funder-specific questions based on:
- Your target funder's priorities
- Required document sections
- Best practices for winning proposals

### Gap Analysis
When analyzing existing documents, the system identifies:
- Missing critical sections
- Insufficient detail in key areas
- Funder-specific requirements not met
- Opportunities for improvement

### Human-Like Writing
Documents are generated with:
- Natural, engaging language (not robotic)
- Professional yet accessible tone
- Data-driven arguments
- Compelling storytelling
- Funder-specific style requirements

## Requirements

- Python 3.8 or higher
- OpenAI API key (get one at https://platform.openai.com/api-keys)
- Internet connection for API calls

## Documentation

See [USAGE.md](USAGE.md) for detailed usage instructions and examples.

