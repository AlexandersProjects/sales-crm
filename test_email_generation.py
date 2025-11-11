#!/usr/bin/env python3
"""
Email generation test script
Tests the OpenAI integration for email generation
"""
import sys
import os
import json

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
import openai

console = Console()

# Get OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def test_email_generation():
    """Test email generation with OpenAI"""
    console.print("\n[bold cyan]🤖 Email Generation Tester[/bold cyan]\n")

    if not OPENAI_API_KEY:
        console.print("[bold red]✗ Error:[/bold red] OPENAI_API_KEY not set in environment\n")
        console.print("[yellow]To set it:[/yellow]")
        console.print("  1. Edit .env file")
        console.print("  2. Add: OPENAI_API_KEY=your-key-here")
        console.print("  3. Restart Docker containers\n")
        sys.exit(1)

    openai.api_key = OPENAI_API_KEY
    console.print("[green]✓[/green] OpenAI API key found\n")

    # Test data
    test_cases = [
        {
            "lead_name": "John Doe",
            "company": "Acme Corp",
            "tone": "professional"
        },
        {
            "lead_name": "Jane Smith",
            "company": "TechStart Inc",
            "tone": "friendly"
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        console.print(f"[bold]Test Case {i}:[/bold]")
        console.print(f"  Lead: {test_case['lead_name']}")
        console.print(f"  Company: {test_case['company']}")
        console.print(f"  Tone: {test_case['tone']}\n")

        try:
            # Generate prompt
            prompt = f"""Generate a {test_case['tone']} email for {test_case['lead_name']} at {test_case['company']} introducing our CRM solution. Return JSON with 'subject' and 'body' fields."""

            console.print("[cyan]Calling OpenAI API...[/cyan]")

            # Call OpenAI
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional sales email writer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )

            content = response.choices[0].message.content

            # Try to parse as JSON
            try:
                email_data = json.loads(content)
                subject = email_data.get('subject', 'N/A')
                body = email_data.get('body', content)
            except json.JSONDecodeError:
                # If not JSON, use raw content
                subject = f"Connecting with {test_case['lead_name']}"
                body = content

            # Display result
            console.print(Panel(
                f"[bold]Subject:[/bold] {subject}\n\n[bold]Body:[/bold]\n{body}",
                title=f"✓ Generated Email #{i}",
                border_style="green"
            ))
            console.print()

        except openai.APIError as e:
            console.print(f"[bold red]✗ OpenAI API Error:[/bold red] {str(e)}\n")
        except Exception as e:
            console.print(f"[bold red]✗ Error:[/bold red] {str(e)}\n")

    console.print("[bold green]✓ Email generation test complete![/bold green]\n")

if __name__ == "__main__":
    test_email_generation()

