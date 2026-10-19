"""Entry point for the RAG command-line interface."""

import fire

from src.cli.commands import Commands


def main() -> None:
    """Expose the RAG commands through Python Fire."""
    fire.Fire(Commands)


if __name__ == "__main__":
    main()
