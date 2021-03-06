# What is Packman?

Packman is a basic package manager which aims to provide a unified way
to manage modifications for games which do not provide adequate
management themselves. Such games include Kerbal Space Program, RimWorld
and Emergency 5.

Depending on the configuration for each particular mod, it pulls
packages from sources such as GitHub or SpaceDock and then runs a
sequence of steps to install them.

# What isn't Packman?

Packman is not a dependency management system. Although it would be nice
to automatically install dependencies and ensure cross-compatibility, as
mods do not have standardised manifests à la package.json, this would
require a parallel database of mod dependencies be created and
continuously maintained.

This would be a lot of work, introduce consistency issues where said
database does not agree with the reality, creates the expectation that
installing 100 mods should *just work* and just generally wouldn\'t be
worth it as mod dependency trees tend to be very small anyway.

# Quick start

**Note:** At some point, it will be simpler than this - probably a
compiled binary with an installer - but **it is not yet intended for
general use**.

Install Python 3.9.1:

:   <https://www.python.org/downloads/release/python-391/>

Install Poetry:

:   `pip install poetry`

On Windows, install Make:

:   <http://gnuwin32.sourceforge.net/packages/make.htm>

Start Packman:

:   `make cli` or `make gui`

Run a command:

:   `poetry run python -m packman_cli.cli --help`

# File safety

Packman aims to minimise the possibility that files end up in an invalid
state:

-   If an installation fails to complete, all changes will be rolled
    back.
-   If files are changed externally after installation, these files are
    considered \'orphans\' and will not be deleted upon uninstallation.
-   State is stored on the file-system and can be recovered in case of
    forcible termination.

There is however still work to be done in this area:

-   There is no command to deal with orphan files.

# Settings

Currently, Packman settings are configured using environment variables;
see `packman/config.py`.

At some point, this will change to be a configuration file in a more
user-friendly format.

# Configuring new mods

Currently, mod configurations exist in the form of YAML files in the
configs folder.

The schema for mod configurations can be found at
`docs/schemas/package_definition.json`.

# Planned features and changes

Planned features and changes are maintained in the code itself.

Search the code for TODO and FIXME, or install an extension for your IDE
to manage this.

# Contributing

All contributions are welcomed with open arms.

See the docs to get started (TODO).
