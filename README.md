# Translate dir CLI
This is CLI tool that aims to automatize the process of translation of large
documents written using Markup languages such as:
- LaTeX
- Markdown
- Jupyter
- Myst
- Typst

This CLI tool is an implementation of [this library](https://github.com/DobbiKov/translate-dir-lib).

## Features
- [x] Project creation
- [x] Source language and the source folder to translate setting
- [x] Target language addition
- [x] Project files syncing (between languages)
- [x] Translation database
- [x] File translation
- [x] Translation correction

## Getting started
For developers: follow [here](#getting-started-for-developers)

### Installation
1. Ensure you have [uv](https://docs.astral.sh/uv/#__tabbed_1_1) tool installed. 
2. Clone this repo: `git clone https://github.com/DobbiKov/translate-dir-cli`
3. Enter to the directory: `cd translate-dir-cli`
4. Install dependencies: `uv sync`
5. Install the CLI globally on your machine: `uv tool install .`
6. Use it using `translate-dir` (example: `translate-dir --help`)

### First steps
This section is to start using this tool as quickly as possible, the profound
explanation can be found [here](./docs/tool-profound-explanation.md). It is
very recommended to read the profound explanation in order to understand how 
the tool operates with files and how the overall structure of the project look
like.

#### Setup the translation project
1. Create a dedicated directory where you will store your project **OR** move to the parent directory of the root of your project.
2. Create the dedicated translation project:
```
translate-dir init
```
In order to set the project's name, use `--name` flag, example:
```
translate-dir init --name my_proj
```
3. Set the source directory (that will be translated) if such exists, if it doesn't, create one or move one:
```
translate-dir project set-source <dir_name> <language>
```

Example:
```
translate-dir project set-source analysis_notes french
```

4. Add target language(s) that you want to translate your project into:
```
translate-dir project add-lang <language>
```

Example:
```
translate-dir project add-lang english
```

#### Syncing and Translation 
5. Mark the files in the source directory that you want to translate:
```
translate-dir project mark-translatable <path_to_file>
```

Example:
```
translate-dir project mark-translatable analysis_notes/main.tex
```

To see all the translatable files use: `translate-dir project list-translatable`

6. Synchronize the source directory and target language directories (untranslatable files only)
```
translate-dir project sync
```

Why and how does it work? Visit [profound explanation](./docs/tool-profound-explanation.md)

7. Translate one particular file:
```
GOOGLE_API_KEY=<your_google_api_key> translate-dir project translate file <file_path> <target_language>
```

Example:
```
GOOGLE_API_KEY=my_super_google_key translate-dir project translate file analysis_notes/main.tex english
```

8. Translate all the files into particular language:
```
GOOGLE_API_KEY=<your_google_api_key> translate-dir project translate all <target_language>
```

Example:
```
GOOGLE_API_KEY=my_super_google_key translate-dir project translate all english 
```

#### Correction

9. In case you corrected the translation done by this tool, in order to save those translations use:
    1. To correct one particular file
    ```
    translate-dir project correct <file_path>
    ```

    2. To correct all the target language directory
    ```
    translate-dir project correct <language>
    ```

## Getting started for developers
1. Ensure you have [uv](https://docs.astral.sh/uv/#__tabbed_1_1) tool installed. 
2. Clone the library firstly, the lib's installation guide can be found [here](https://github.com/DobbiKov/translate-dir-lib?tab=readme-ov-file#installation)
3. Get the path to the lib's directory on your local machine (for instance: `realpath <your_dir>` on macOs)
4. Clone this repo: `git clone https://github.com/DobbiKov/translate-dir-cli`
5. Enter to the directory: `cd translate-dir-cli`
6. Remove current library dependency: `uv remove translate-dir-lib`
7. Add the local one: `uv add --editable <path_to_local_lib_dir>`
8. Install the dependencies: `uv sync`
9. Install the CLI globally in editable mode: `uv pip install -e .`

## Documentation
The documentation for the library can be found [here](./docs/main.md)

## Contributing
The suggestions and pull requests are welcome. Visit the issues pages as well
as the project's [main page](https://github.com/DobbiKov/sci-trans-git) and the
[shared document](https://codimd.math.cnrs.fr/sUW9PQ1tTLWcR98UjLHLpw) in order
to know the current direction and plans of the project.
