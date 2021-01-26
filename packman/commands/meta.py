from argparse import ArgumentParser
from typing import List, Optional

from loguru import logger

from .command import Command

# TODO interactive orphan resolution:
# - Delete all
# - Delete orphan
# - Keep orphan (remove from manifest)
# - Restore from backup (if applicable)


class PackageListCommand(Command):
    help = "Lists available packages"

    def execute(self) -> None:
        self.output.write_table(
            [
                [name, config.name, config.description]
                for name, config in self.packman.packages()
            ]
        )


class VersionListCommand(Command):
    help = "Lists available versions for a package"

    def configure_parser(self, parser: ArgumentParser) -> None:
        parser.add_argument("package", help="The package to list versions for")

    def execute(self, package: str) -> None:
        for version in self.packman.versions(package):
            self.output.write(version)


class InstalledPackageListCommand(Command):
    help = "Lists installed packages"

    def execute(self) -> None:
        manifest = self.packman.manifest
        packages = {key: value for key, value in self.packman.packages()}
        self.output.write_table(
            rows=[
                [name, info.version, packages[name].name, packages[name].description]
                for name, info in manifest.packages.items()
            ]
        )


class UpdateCommand(Command):
    help = "Updates the configuration from the configured remote source"

    def execute(self) -> None:

        output = self.output

        step_name = "updating..."

        def on_progress(p: float) -> None:
            output.write_step_progress(step_name, p)

        try:
            if self.packman.update(on_progress=on_progress):
                output.write_step_complete(step_name)
            else:
                output.write_step_error(step_name, "nothing to update")
        except Exception as exc:
            logger.exception(exc)
            output.write_step_error(step_name, str(exc))
        except KeyboardInterrupt as exc:
            self.output.write_step_error(step_name, "cancelled")
            raise exc from None


class ValidateCommand(Command):
    help = "Validates the files of one or more packages"

    def configure_parser(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "packages",
            help="Names of the package or packages to validate; if none specified, all packages will be validated",
            nargs="*",
        )

    def execute(self, packages: Optional[List[str]] = None) -> None:
        if not packages:
            manifest = self.packman.manifest
            if not manifest.packages:
                self.output.write("0 invalid files")
                return
            packages = list(manifest.packages.keys())
        invalid_files: List[str] = []
        for name in packages:
            invalid_files += list(self.packman.validate(name=name))
        invalid_count = len(invalid_files)
        if invalid_count == 1:
            self.output.write("1 invalid file")
        else:
            self.output.write(f"{invalid_count} invalid files")
        for file in invalid_files:
            self.output.write(file)


class CleanCommand(Command):
    help = "Cleans up orphaned files"

    def execute(self) -> None:
        raise NotImplementedError("TODO")
