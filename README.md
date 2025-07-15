# Translate dir CLI
This is CLI tool that aims to automatize the process of translation of large
documents written using Markup languages such as:
- LaTeX
- Markdown
- Jupyter
- Myst
- Typst

This CLI tool is an implementation of [this library](https://github.com/DobbiKov/translate-dir-lib).


**Important**
> This tool is still in an early phase of development, it may have bugs and unimplemented features

## Table of Contents
- [Features](#features)
- [Citation](#citation)
- [Getting started](#getting-started)
    - [Installation](#installation)
    - [First steps](#first-steps)
        - [Setup the translation project](#setup-the-translation-project)
        - [Syncing and Translation](#syncing-and-translation)
        - [Correction](#correction)
- [Getting started for developers](#getting-started-for-developers)
- [Documentation](#documentation)
- [Contributing](#contributing)

## Features
- [x] Project creation
- [x] Source language and the source folder to translate setting
- [x] Target language addition
- [x] Project files syncing (between languages)
- [x] Translation database
- [x] File translation
- [x] Translation correction

## Citation

If you use this software in your research, please cite it as follows:
```bib
@software{korotenko-sci-trans-git,
    author = {Yehor Korotenko},
    title = {sci-trans-git},
    year = {2025},
    publisher = {GitHub},
    version = {0.2.0-alpha},
    url = {https://github.com/DobbiKov/sci-trans-git},
    doi = {10.5281/zenodo.15775111}
}
```

## Getting started
For developers: follow [here](#getting-started-for-developers)

### Installation
1. Ensure you have [uv](https://docs.astral.sh/uv/#__tabbed_1_1) tool installed. 
2. Clone this repo: 
    ```sh
    git clone https://github.com/DobbiKov/translate-dir-cli
    ```
3. Enter to the directory: 
    ```sh
    cd translate-dir-cli
    ```
4. Install dependencies: 
    ```sh
    uv sync
    ```

5. Install the CLI globally on your machine: 
    ```sh
    uv tool install .
    ```
6. Use it using `translate-dir` (example: `translate-dir --help`)

### First steps
This section is a guide to start using this tool as quickly as possible, the profound
explanation can be found [here](https://github.com/DobbiKov/translate-dir-lib/blob/master/docs/tool-profound-explanation.md). It is
very recommended to read the profound explanation in order to understand how 
the tool operates with files and how the overall structure of the project look
like.

#### Setup the translation project
1. Create a dedicated directory to serve as the root for your translation
   project, and place your existing writing project's directory inside it. In
   other words, your root directory (for the translation project) must be a
   parent directory for your writing project.

2. Create the dedicated translation project:
```
translate-dir init [--name <your_name>]
```
where `--name` is an optional parameter that sets your project's name.

Example:
```
translate-dir init --name my_proj
```

3. Set the source directory (that will be translated) if such exists, if it doesn't, create one or move one inside of your translation project's directoy:
```
translate-dir set-source <dir_name> <language>
```

Example:
```
translate-dir set-source analysis_notes french
```

4. Add target language(s) that you want to translate your project into:
```
translate-dir set-target <language> --tgt-dir [YOUR_TARGET_DIRCTORY]
```

The `--tgt-dir` is an optional flag, if the target directory is not provided,
then the APP will create a new one.

Example:
```
translate-dir set-target english 
```

or:
```
translate-dir set-target english --tgt-dir translations/en
```

#### Syncing and Translation 
5. Mark the files in the source directory that you want to translate:
```
translate-dir add <path_to_file>
```

Example:
```
translate-dir add analysis_notes/main.tex
```

To see all the translatable files use: `translate-dir list`

6. Synchronize the source directory and target language directories (untranslatable files only)
```
translate-dir sync
```

Why and how does it work? Visit the [profound explanation](https://github.com/DobbiKov/translate-dir-lib/blob/master/docs/tool-profound-explanation.md)

For the translation you need to have a `GOOGLE_API_KEY`. Follow the next instruction to obtain the key:
1. Visit [this link](https://aistudio.google.com/app/apikey)
2. 
    - If it is your first time getting an API KEY for Gemini:
        1. If it is your first time getting an API KEY for Gemini, then you'll see a Popup window. Click on `Get API Key`, then accept the Terms of Service.
        2. Click on `Create API Key`
        3. Copy the generated API key in the popup window
    - If you already had your API KEY
        1. Click on `Create API Key`
        2. Create a new project or choose an existing one
        3. Click on `Create API KEY in existing project`
        4. Copy the generated API key in the popup window

This key must be set as a environment variable. This can be done by providing
it in the start of your CLI command as it is shown below:

7. Translate one particular file:
```
GOOGLE_API_KEY=<your_google_api_key> translate-dir translate file <file_path> <target_language>
```

Example:
```
GOOGLE_API_KEY=my_super_google_key translate-dir translate file analysis_notes/main.tex english
```

8. Translate all the files into particular language:
```
GOOGLE_API_KEY=<your_google_api_key> translate-dir translate all <target_language>
```

Example:
```
GOOGLE_API_KEY=my_super_google_key translate-dir translate all english 
```
##### Vocabulary
To each translation command a `--vocabulary` flag can be passed. That flag
requires a path to a CSV file that contains a translation vocabulary. Such
file must contain a table where each column is dedicated to one particular
language, then in the row, there's a term in a language and the other fields
of the row contain the translation of that term on the language depending the
column they located in. This vocabulary then is passed to the translation
tool in order to improve the translation quality.

Example:
Let's assume you have a file in the project's root directory that is called `vocab.csv` that has such contents:
```
English,French,Ukrainian
iff,ssi,якщо і тільки якщо
eigen vector, vecteur propre, айген вектор
```

Then, in order to use it in the translation from French to English:
```
GOOGLE_API_KEY=my_super_google_key translate-dir translate all english --vocabulary vocab.csv
```

#### Correction

9. In case you corrected the translation done by this tool, in order to save those translations use:
    1. To correct one particular file
    ```
    translate-dir correct <file_path>
    ```

    2. To correct all the target language directory
    ```
    translate-dir correct <language>
    ```

## Getting started for developers
1. Ensure you have [uv](https://docs.astral.sh/uv/#__tabbed_1_1) tool installed. 
2. Clone the library firstly, the lib's installation guide can be found [here](https://github.com/DobbiKov/translate-dir-lib?tab=readme-ov-file#installation)
3. Get the path to the lib's directory on your local machine (for instance: `realpath <your_dir>` on macOs)
4. Clone this repo: 
    ```sh
    git clone https://github.com/DobbiKov/translate-dir-cli
    ```
5. Enter to the directory: 
    ```sh
    cd translate-dir-cli
    ```
6. Remove current library dependency: 
    ```sh
    uv remove translate-dir-lib
    ```
7. Add the local one: `uv add --editable <path_to_local_lib_dir>`
8. Install the dependencies: 
    ```sh
    uv sync
    ```
9. Install the CLI globally in editable mode: 
    ```sh
    uv pip install -e .
    ```

## Documentation
The documentation for the library can be found [here](./docs/main.md)

## Contributing
The suggestions and pull requests are welcome. Visit the issues pages as well
as the project's [main page](https://github.com/DobbiKov/sci-trans-git) and the
[shared document](https://codimd.math.cnrs.fr/sUW9PQ1tTLWcR98UjLHLpw) in order
to know the current direction and plans of the project.
