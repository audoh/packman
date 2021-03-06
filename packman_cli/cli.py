import shlex
import sys
from argparse import ArgumentError, ArgumentParser
from typing import Dict, List, Optional

from packman import InstallStep, PackageSource, Packman, sources, steps
from packman.commands import (CleanCommand, Command, ExportCommand,
                              ImportCommand, InstallCommand,
                              InstalledPackageListCommand, PackageListCommand,
                              RecoverCommand, UninstallCommand, UpdateCommand,
                              ValidateCommand, VersionListCommand)
from packman.config import read_config
from packman.utils.output import SupportsWrite

cfg = read_config()
cfg.configure_logger()
packman = Packman.from_config(cfg)
DEFAULT_COMMANDS = {
    "install": InstallCommand(packman),
    "uninstall": UninstallCommand(packman),
    "recover": RecoverCommand(packman),
    "list": InstalledPackageListCommand(packman),
    "update": UpdateCommand(packman),
    "packages": PackageListCommand(packman),
    "versions": VersionListCommand(packman),
    "validate": ValidateCommand(packman),
    "export": ExportCommand(packman),
    "import": ImportCommand(packman),
    "clean": CleanCommand(packman),
}


class PackmanCLI:
    def __init__(
        self,
        commands: Dict[str, Command] = DEFAULT_COMMANDS,
        no_interactive_mode: bool = False,
        file: Optional[SupportsWrite] = None,
    ) -> None:
        desc = "Rudimentary file package management intended for modifications for games such as KSP and RimWorld"
        parser = ArgumentParser(description=desc)
        command_parsers = parser.add_subparsers(
            metavar="<command>", help="Valid commands:", dest="command", required=False
        )
        for name, command in commands.items():
            command_parser = command_parsers.add_parser(name, help=command.help)
            command.configure_parser(command_parser)

        self.commands = commands
        self.parser = parser
        self.command_parsers = command_parsers
        self.interactive_mode_enabled = not no_interactive_mode
        self.command_parsers.required = not self.interactive_mode_enabled
        self.interactive_mode = False
        self.file = file

        PackmanCLI.update_usage(self.parser)

    @staticmethod
    def update_usage(parser: ArgumentParser) -> None:
        parser.usage = parser.format_help()[7:]

    def print(self, value: str) -> None:
        print(value, file=self.file)

    def start_interactive_mode(self) -> None:
        if self.interactive_mode:
            return
        self.interactive_mode = True

        # Create new parser
        parser = ArgumentParser(
            description=self.parser.description, add_help=False, exit_on_error=False
        )
        command_parsers = parser.add_subparsers(
            metavar="<command>", help="Valid commands:", dest="command", required=True
        )
        for name, command in self.commands.items():
            command_parser = command_parsers.add_parser(name, help=command.help)
            command.configure_parser(command_parser)

        command_parsers.add_parser("exit", help="Quits this interactive session")
        command_parsers.add_parser("help", help="Shows this help message")
        PackmanCLI.update_usage(parser)

        self.print("Packman interactive session started.")
        self.print(
            "Type \u0022exit\u0022 to quit or \u0022help\u0022 for more information."
        )

        while True:
            raw = input("> ")
            argv = shlex.split(raw)
            if argv:
                arg0 = argv[0].lower()
                if arg0.startswith(
                    ("exit", "quit", "stop", "abort", "goaway", "cancel")
                ) or arg0 in (
                    "q",
                    "e",
                ):
                    self.stop_interactive_mode()
                    break
            try:
                args = parser.parse_args(argv)
                args_dict = vars(args)
                command_name = args_dict.pop("command")
                assert command_name is not None, "command_name cannot be None"
                if command_name == "help":
                    parser.print_help()
                else:
                    command = self.commands[command_name]
                    command.execute_safe(**args_dict)
            except ArgumentError as exc:
                self.print(f"error: {exc.message}")
            except Exception as exc:
                self.print(f"error: {exc}")
            except SystemExit as exc:
                # Ignore argparser's own attempts to exit
                if exc.code not in (0, 2):
                    raise

    def stop_interactive_mode(self) -> None:
        if not self.interactive_mode:
            return
        self.interactive_mode = False

    def parse(self, argv: List[str]) -> None:
        parser = self.parser
        args = parser.parse_args(argv)
        args_dict = vars(args)
        command_name: Optional[str] = args_dict.pop("command")
        if command_name is None:
            if self.interactive_mode_enabled:
                self.start_interactive_mode()
            else:
                raise Exception("no command provided")
        else:
            command = DEFAULT_COMMANDS[command_name]
            command.execute_safe(**args_dict)


if __name__ == "__main__":
    # TODO add autocomplete

    # Set up yaml handlers
    sources.register_all(PackageSource)
    steps.register_all(InstallStep)

    # Set up parser
    cli = PackmanCLI(commands=DEFAULT_COMMANDS)
    cli.parse(argv=sys.argv[1:])
