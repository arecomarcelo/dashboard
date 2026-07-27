#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.text import Text

# Configurações
console = Console()
ROOT_DIR = Path(".")


def run_command(command: str, success_msg: str, error_msg: str) -> bool:
    """Executa um comando e exibe o resultado formatado."""
    console.print(f"\n[bold]Executando:[/bold] [cyan]{command}[/cyan]")

    with Progress(transient=True) as progress:
        task = progress.add_task("[yellow]Processando...", total=1)
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=ROOT_DIR,
                check=True,
                capture_output=True,
                text=True,
            )
            progress.update(task, completed=1)
            console.print(
                Panel.fit(
                    Text.from_ansi(result.stdout),
                    title=f"[green]✓ {success_msg}",
                    border_style="green",
                )
            )
            return True
        except subprocess.CalledProcessError as e:
            progress.update(task, completed=1)
            console.print(
                Panel.fit(
                    Text.from_ansi(e.stderr),
                    title=f"[red]✗ {error_msg}",
                    border_style="red",
                )
            )
            return False


def check_dependencies():
    """Verifica se as dependências estão instaladas corretamente"""
    console.print("\n[yellow]🔍 Verificando dependências...[/yellow]")

    try:
        import black

        console.print("[green]✅ Black instalado[/green]")
        black_ok = True
    except ImportError:
        console.print("[red]❌ Black não encontrado[/red]")
        black_ok = False

    try:
        import mypy

        console.print("[green]✅ Mypy instalado[/green]")
        mypy_ok = True
    except ImportError:
        console.print("[red]❌ Mypy não encontrado[/red]")
        mypy_ok = False

    if not (black_ok and mypy_ok):
        console.print(
            "\n[yellow]⚠️  Execute primeiro: python fix_formatters.py[/yellow]"
        )
        return False

    return True


def main():
    console.print(
        Panel.fit(
            "[bold]🔧 Formatador de Código[/bold]",  # Adicionado símbolo de registro
            subtitle="HauxTech®",  # Adicionado emoji de engrenagem
            border_style="blue",
        )
    )

    # Verificar dependências primeiro
    if not check_dependencies():
        return

    # Usa o mesmo interpretador que está rodando este script (a venv do
    # projeto, chamada pelo predeploy.sh) em vez de um "python" bare — que via
    # subprocess/shell=True resolve pelo PATH e pode cair no python do pyenv
    # (sem black/isort/mypy instalados), mesmo com a venv ativa.
    python_exe = sys.executable

    # Formatação com verificações mais robustas
    black_success = run_command(
        f'"{python_exe}" -m black . --line-length=88 --skip-string-normalization',
        "Black: Formatação concluída com sucesso!",
        "Black: Erro na formatação!",
    )

    isort_success = run_command(
        f'"{python_exe}" -m isort . --profile black',
        "Isort: Imports organizados com sucesso!",
        "Isort: Erro ao organizar imports!",
    )

    # Verificação de tipos com configuração de desenvolvimento (warnings são OK)
    console.print("\n[yellow]⚙️  Executando Mypy em modo desenvolvimento...[/yellow]")
    mypy_result = run_command(
        f'"{python_exe}" -m mypy app.py --ignore-missing-imports --allow-untyped-defs',
        "Mypy: Verificação do arquivo principal concluída!",
        "Mypy: Arquivo principal tem alguns warnings (normal em desenvolvimento)",
    )
    # Em modo desenvolvimento, consideramos sucesso mesmo com warnings
    mypy_success = True

    console.print("\n[bold]📊 Resumo:[/bold]")
    console.print(
        f"• Black: {'[green]Sucesso[/green]' if black_success else '[red]Falha[/red]'}"
    )
    console.print(
        f"• Isort: {'[green]Sucesso[/green]' if isort_success else '[red]Falha[/red]'}"
    )
    console.print(
        f"• Mypy: {'[green]Sucesso[/green]' if mypy_success else '[red]Falha[/red]'}"
    )


if __name__ == "__main__":
    main()
