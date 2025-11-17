# Funder Research Guide

This guide explains how the system researches funders and extracts guidelines to improve proposal quality.

## Overview

The Proposal Generator includes an automated funder research system that:
- Scrapes funder websites for guidelines
- Extracts key requirements and criteria
- Analyzes successful proposals
- Provides recommendations based on funder preferences

## How It Works

### 1. Funder Website Analysis

When you provide a funder URL, the system:
- Accesses the funder's website
- Identifies relevant pages (guidelines, requirements, FAQs)
- Extracts key information:
  - Eligibility criteria
  - Funding amounts
  - Deadlines
  - Required sections
  - Format requirements
  - Evaluation criteria

### 2. Guidelines Extraction

The system extracts:
- **Format Requirements**: Page limits, font, spacing
- **Content Requirements**: Required sections, word limits
- **Evaluation Criteria**: How proposals are scored
- **Budget Guidelines**: Limits, allowed expenses
- **Submission Process**: How to submit, required documents

### 3. Proposal Alignment

Based on extracted guidelines, the system:
- Suggests content improvements
- Highlights missing requirements
- Recommends structure changes
- Identifies alignment opportunities

## Using Funder Research

### Providing Funder Information

#### Funder Name
- Enter the full, official name
- Example: "National Science Foundation"
- Avoid abbreviations unless standard

#### Funder Website
- Provide the main website URL
- Example: `https://www.nsf.gov`
- Ensure the URL is accessible

### Automatic Research

The system automatically:
1. Scrapes the funder website
2. Extracts relevant information
3. Stores guidelines in the knowledge base
4. Uses information during proposal generation

### Manual Research

You can also:
- Review extracted guidelines
- Add additional requirements
- Update outdated information
- Provide context and notes

## Research Features

### Web Scraping
- **Technology**: BeautifulSoup, Selenium
- **Capabilities**:
  - HTML parsing
  - JavaScript rendering
  - PDF extraction
  - Form handling

### Knowledge Base
- **Storage**: Vector database (ChromaDB)
- **Search**: Semantic search
- **Updates**: Automatic and manual

### Analysis
- **NLP**: Natural language processing
- **Extraction**: Key information extraction
- **Summarization**: Guideline summaries

## Guidelines Extraction

### Common Guidelines Extracted

#### Format Requirements
- Page limits
- Font and spacing
- Margins
- File format
- Naming conventions

#### Content Requirements
- Required sections
- Word/character limits
- Required information
- Optional sections

#### Evaluation Criteria
- Scoring rubrics
- Weighted criteria
- Review process
- Success factors

#### Budget Guidelines
- Maximum amounts
- Allowed expenses
- Required justifications
- Indirect cost rates

## Best Practices

### Providing Funder Information
1. **Be Accurate**: Use official names and URLs
2. **Be Complete**: Include all relevant information
3. **Be Current**: Verify information is up-to-date
4. **Be Specific**: Include program names if applicable

### Using Research Results
1. **Review Guidelines**: Check extracted information
2. **Verify Accuracy**: Confirm with official sources
3. **Apply Recommendations**: Use suggestions appropriately
4. **Update as Needed**: Keep information current

### Improving Research
1. **Provide Feedback**: Report inaccuracies
2. **Add Context**: Include additional information
3. **Update Guidelines**: Keep information current
4. **Share Knowledge**: Contribute to knowledge base

## Research Limitations

### What the System Can Do
- Extract publicly available information
- Analyze structured guidelines
- Identify common patterns
- Provide general recommendations

### What the System Cannot Do
- Access password-protected content
- Interpret ambiguous requirements
- Guarantee accuracy
- Replace human review

## Troubleshooting

### Common Issues

#### Website Not Accessible
- **Cause**: URL incorrect or site down
- **Solution**: Verify URL, check site status
- **Alternative**: Provide guidelines manually

#### Guidelines Not Extracted
- **Cause**: Unusual format or structure
- **Solution**: Review website structure
- **Alternative**: Manual entry

#### Inaccurate Information
- **Cause**: Website changes or errors
- **Solution**: Verify with official source
- **Action**: Report for correction

### Getting Help
- Check extracted guidelines for accuracy
- Review funder website directly
- Contact support for assistance
- Provide feedback for improvements

## Advanced Features

### Custom Research
- Define custom extraction rules
- Specify pages to analyze
- Set extraction priorities
- Configure update frequency

### Research History
- View past research results
- Compare guideline versions
- Track changes over time
- Export research data

### Integration
- Connect with funder databases
- Import from external sources
- Export to other systems
- API access for automation

## Tips for Success

1. **Provide Complete Information**: Include all relevant details
2. **Verify Results**: Always check extracted information
3. **Stay Updated**: Guidelines change frequently
4. **Use Multiple Sources**: Don't rely solely on automated research
5. **Contribute**: Help improve the knowledge base

## Next Steps

- Learn about [Proposal Creation](proposal_creation.md)
- Explore [Document Management](document_management.md)
- Review [Settings Configuration](settings_configuration.md)


