#!/usr/bin/env python3
"""
Database verification script for Sales CRM
Checks if the database is properly set up and contains data
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/sales_crm")

def check_database():
    """Check database connection and data"""
    console.print("\n[bold cyan]🔍 Sales CRM Database Checker[/bold cyan]\n")

    try:
        # Create engine
        engine = create_engine(DATABASE_URL)

        with engine.connect() as conn:
            # Check connection
            console.print("[green]✓[/green] Database connection successful!\n")

            # Check tenants
            console.print("[bold]Checking Tenants:[/bold]")
            result = conn.execute(text("SELECT * FROM tenants ORDER BY id"))
            tenants = result.fetchall()

            if tenants:
                table = Table(title="Tenants", show_header=True, header_style="bold magenta")
                table.add_column("ID", style="cyan")
                table.add_column("Name", style="green")
                table.add_column("Created At", style="yellow")

                for tenant in tenants:
                    table.add_row(str(tenant[0]), tenant[1], str(tenant[2]))

                console.print(table)
                console.print(f"\n[green]✓[/green] Found {len(tenants)} tenant(s)\n")
            else:
                console.print("[yellow]⚠[/yellow]  No tenants found\n")

            # Check leads
            console.print("[bold]Checking Leads:[/bold]")
            result = conn.execute(text("""
                SELECT l.id, l.name, l.email, l.company, l.status, t.name as tenant_name
                FROM leads l
                JOIN tenants t ON l.tenant_id = t.id
                ORDER BY l.created_at DESC
                LIMIT 10
            """))
            leads = result.fetchall()

            if leads:
                table = Table(title="Recent Leads (max 10)", show_header=True, header_style="bold magenta")
                table.add_column("ID", style="cyan")
                table.add_column("Name", style="green")
                table.add_column("Email", style="blue")
                table.add_column("Company", style="yellow")
                table.add_column("Status", style="magenta")
                table.add_column("Tenant", style="cyan")

                for lead in leads:
                    table.add_row(
                        str(lead[0]),
                        lead[1],
                        lead[2] or "N/A",
                        lead[3] or "N/A",
                        lead[4],
                        lead[5]
                    )

                console.print(table)

                # Count by status
                result = conn.execute(text("SELECT status, COUNT(*) FROM leads GROUP BY status"))
                status_counts = result.fetchall()

                console.print("\n[bold]Lead Status Distribution:[/bold]")
                for status, count in status_counts:
                    console.print(f"  • {status}: [cyan]{count}[/cyan]")

                console.print(f"\n[green]✓[/green] Found {len(leads)} lead(s) (showing latest 10)\n")
            else:
                console.print("[yellow]⚠[/yellow]  No leads found\n")

            # Database info
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]

            console.print(Panel(
                f"[bold]Database:[/bold] {DATABASE_URL.split('@')[1]}\n"
                f"[bold]PostgreSQL Version:[/bold] {version.split(',')[0]}",
                title="Database Info",
                border_style="green"
            ))

    except Exception as e:
        console.print(f"\n[bold red]✗ Error:[/bold red] {str(e)}\n")
        console.print("[yellow]Make sure the database container is running:[/yellow]")
        console.print("  docker-compose up postgres\n")
        sys.exit(1)

if __name__ == "__main__":
    check_database()

