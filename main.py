"""
Main application for Professional Funding Proposal Generator
"""
import os
import sys
from typing import Optional, Dict
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.markdown import Markdown

from config import FUNDER_REQUIREMENTS, DOCUMENT_TYPES
from document_analyzer import DocumentAnalyzer
from question_generator import QuestionGenerator
from document_generator import DocumentGenerator

console = Console()


def print_header():
    """Print application header"""
    header = """
    ╔══════════════════════════════════════════════════════════════╗
    ║   Professional Funding Proposal Generator                    ║
    ║   Win Grants from Fortune 500, Gates Foundation,             ║
    ║   World Bank, WHO & More                                     ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    console.print(header, style="bold cyan")


def select_funder() -> str:
    """Let user select funder type"""
    console.print("\n[bold]Select Your Target Funder:[/bold]\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Option", style="cyan", width=10)
    table.add_column("Funder", style="white")
    table.add_column("Focus Areas", style="dim")
    
    funders = list(FUNDER_REQUIREMENTS.keys())
    for i, funder_key in enumerate(funders, 1):
        funder = FUNDER_REQUIREMENTS[funder_key]
        focus = ", ".join(funder["focus_areas"][:2])
        table.add_row(str(i), funder["name"], focus)
    
    console.print(table)
    
    while True:
        choice = Prompt.ask("\nEnter your choice", choices=[str(i) for i in range(1, len(funders) + 1)])
        return funders[int(choice) - 1]


def select_document_type() -> str:
    """Let user select document type"""
    console.print("\n[bold]Select Document Type:[/bold]\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Option", style="cyan", width=10)
    table.add_column("Document Type", style="white")
    table.add_column("Use Case", style="dim")
    
    doc_types = list(DOCUMENT_TYPES.keys())
    use_cases = {
        "proposal": "Full funding proposal",
        "concept_note": "Initial concept/idea submission",
        "pitch_deck": "Presentation to stakeholders",
        "executive_summary": "Brief overview document"
    }
    
    for i, doc_key in enumerate(doc_types, 1):
        doc = DOCUMENT_TYPES[doc_key]
        use_case = use_cases.get(doc_key, "General use")
        table.add_row(str(i), doc["name"], use_case)
    
    console.print(table)
    
    while True:
        choice = Prompt.ask("\nEnter your choice", choices=[str(i) for i in range(1, len(doc_types) + 1)])
        return doc_types[int(choice) - 1]


def get_user_input_mode() -> str:
    """Determine if user has existing documents or just ideas"""
    console.print("\n[bold]What do you have?[/bold]\n")
    console.print("1. I have existing documents that need improvement")
    console.print("2. I only have ideas - need help creating documents from scratch")
    
    choice = Prompt.ask("\nEnter your choice", choices=["1", "2"])
    return "existing" if choice == "1" else "ideas"


def collect_questions_responses(questions: list) -> Dict[str, str]:
    """Collect user responses to questions"""
    responses = {}
    
    console.print("\n[bold green]Let's gather information about your project[/bold green]\n")
    console.print("You can answer these questions in any order. Press Enter to skip any question.\n")
    
    for q in questions:
        console.print(Panel(
            f"[bold]{q['category']}[/bold]\n\n{q['question']}\n\n[dim]💡 {q['why']}[/dim]",
            title="Question",
            border_style="blue"
        ))
        
        response = Prompt.ask("\nYour answer", default="")
        if response:
            responses[q['category']] = response
        
        console.print()
    
    return responses


def analyze_existing_document(doc_path: str, funder_type: str, doc_type: str) -> tuple:
    """Analyze an existing document"""
    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            doc_text = f.read()
        
        analyzer = DocumentAnalyzer(funder_type, doc_type)
        gaps = analyzer.analyze_text(doc_text)
        report = analyzer.generate_gap_report(gaps)
        
        console.print("\n[bold]Document Analysis Results:[/bold]\n")
        console.print(Panel(report, title="Gap Analysis", border_style="yellow"))
        
        return doc_text, gaps
    
    except FileNotFoundError:
        console.print(f"[red]Error: File '{doc_path}' not found.[/red]")
        return None, []
    except Exception as e:
        console.print(f"[red]Error reading file: {str(e)}[/red]")
        return None, []


def main():
    """Main application flow"""
    print_header()
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        console.print("\n[red]⚠ Warning: OPENAI_API_KEY not found in environment.[/red]")
        console.print("Please create a .env file with your OpenAI API key.\n")
        if not Confirm.ask("Continue anyway?"):
            sys.exit(1)
    
    # Select funder and document type
    funder_type = select_funder()
    doc_type = select_document_type()
    
    funder_name = FUNDER_REQUIREMENTS[funder_type]["name"]
    doc_name = DOCUMENT_TYPES[doc_type]["name"]
    
    console.print(f"\n[green]✓[/green] Selected: [bold]{doc_name}[/bold] for [bold]{funder_name}[/bold]\n")
    
    # Determine input mode
    input_mode = get_user_input_mode()
    
    existing_doc = None
    user_responses = {}
    
    if input_mode == "existing":
        # Analyze existing document
        doc_path = Prompt.ask("\nEnter path to your existing document")
        existing_doc, gaps = analyze_existing_document(doc_path, funder_type, doc_type)
        
        if existing_doc:
            console.print("\n[bold]I'll enhance your existing document based on the analysis.[/bold]")
            # Still ask some key questions to fill gaps
            if gaps:
                question_gen = QuestionGenerator(funder_type, doc_type)
                critical_questions = [q for q in question_gen.generate_questions() 
                                    if any(gap.section in q['category'] for gap in gaps if gap.severity == "critical")]
                
                if critical_questions:
                    console.print("\n[bold yellow]I need some additional information to fill critical gaps:[/bold yellow]\n")
                    user_responses = collect_questions_responses(critical_questions[:5])  # Limit to top 5
    
    else:
        # Generate questions for idea-only users
        question_gen = QuestionGenerator(funder_type, doc_type)
        questions = question_gen.generate_questions()
        
        console.print("\n[bold]To create a winning proposal, I need to understand your project.[/bold]\n")
        user_responses = collect_questions_responses(questions)
    
    # Generate document
    if not user_responses and not existing_doc:
        console.print("\n[red]No information provided. Cannot generate document.[/red]")
        return
    
    console.print("\n[bold green]Generating your professional document...[/bold green]\n")
    console.print("[dim]This may take a minute. Please wait...[/dim]\n")
    
    generator = DocumentGenerator(funder_type, doc_type)
    generated_doc = generator.generate_document(user_responses, existing_doc)
    
    # Display results
    console.print("\n[bold green]✓ Document Generated Successfully![/bold green]\n")
    
    if existing_doc:
        change_summary = generator.generate_change_summary(existing_doc, generated_doc)
        console.print(Panel(change_summary, title="What Changed", border_style="green"))
    
    console.print("\n[bold]Generated Document:[/bold]\n")
    console.print(Panel(generated_doc, title=doc_name, border_style="cyan", expand=False))
    
    # Save option
    if Confirm.ask("\n[bold]Save document to file?[/bold]"):
        filename = Prompt.ask("Enter filename", default=f"{doc_type}_{funder_type}.txt")
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(generated_doc)
            console.print(f"\n[green]✓[/green] Document saved to [bold]{filename}[/bold]")
        except Exception as e:
            console.print(f"\n[red]Error saving file: {str(e)}[/red]")
    
    console.print("\n[bold]Thank you for using Professional Funding Proposal Generator![/bold]\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Operation cancelled by user.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]An error occurred: {str(e)}[/red]")
        sys.exit(1)

