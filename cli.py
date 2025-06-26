import asyncio
import os
import csv
from pathlib import Path
from typing import List, Optional

import typer
from typing_extensions import Annotated # For Typer < 0.7 or for more complex annotations

from trans_lib.enums import Language, CLI_LANGUAGE_CHOICES
from trans_lib.project_manager import Project, init_project, load_project
from trans_lib import errors
from trans_lib.vocab_list import VocabList, vocab_list_from_vocab_db # Import the errors module

# Create the Typer app
app = typer.Typer(
    name="dir-translator",
    help="A tool for managing and translating directory structures.",
    no_args_is_help=True
)

# Shared callback to load project (or handle not being in one)
def get_project_from_context(ctx: typer.Context) -> Project:
    """Loads project based on current directory or explicit path."""
    try:
        # Typer passes the command-specific options.
        # We need a way to get a global --project-path or use CWD.
        # Let's assume `load_project` can take PWD.
        project_path_str = "." # Default to current directory
        
        # If a global option --project-dir is added to app, it can be accessed via ctx.params
        # if ctx.parent and ctx.parent.params.get("project_dir"):
        #    project_path_str = ctx.parent.params["project_dir"]
            
        return load_project(project_path_str)
    except errors.LoadProjectError as e:
        typer.secho(f"Error loading project: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    except Exception as e: # Catch any other unexpected error during load
        typer.secho(f"An unexpected error occurred: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


# --- Project Initialization and Loading Commands ---
@app.command()
def init(
    name: Annotated[str, typer.Option(help="Name for the new project.")] = "MyTranslationProject",
    path: Annotated[Path, typer.Option(help="Directory to initialize the project in. Defaults to current directory.")] = Path(".")
):
    """Initializes a new translation project."""
    try:
        project = init_project(name, str(path.resolve()))
        typer.secho(f"Project '{project.config.name}' initialized successfully at {project.root_path}", fg=typer.colors.GREEN)
    except errors.InitProjectError as e:
        typer.secho(f"Error initializing project: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


@app.command("set-source")
def set_source_dir(
    ctx: typer.Context, # For getting loaded project
    dir_name: Annotated[str, typer.Argument(help="Name of the source directory (relative to project root).")],
    lang: Annotated[Language, typer.Argument(help="Source language.", case_sensitive=False)] # Typer handles Enum conversion
):
    """Sets or changes the source directory and its language."""
    project = get_project_from_context(ctx)
    try:
        project.set_source_directory(dir_name, lang)
        typer.secho(f"Source directory set to '{dir_name}' with language {lang.value}", fg=typer.colors.GREEN)
    except errors.SetSourceDirError as e:
        typer.secho(f"Error setting source directory: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

@app.command("set-target")
def add_language(
    ctx: typer.Context,
    lang: Annotated[Language, typer.Argument(help="Target language to add.", case_sensitive=False)],
    tgt_dir: Annotated[Path | None, typer.Option(help="Set particular directory.", case_sensitive=False)] = None
):
    """Adds a new target language to the project."""
    project = get_project_from_context(ctx)
    try:
        new_path = project.add_target_language(lang, tgt_dir)
        typer.secho(f"Target language {lang.value} added. Directory created at {new_path}", fg=typer.colors.GREEN)
    except errors.AddLanguageError as e:
        typer.secho(f"Error adding language: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

@app.command("remove-lang")
def remove_language(
    ctx: typer.Context,
    lang: Annotated[Language, typer.Argument(help="Target language to remove.", case_sensitive=False)]
):
    """Removes a target language and its directory from the project."""
    project = get_project_from_context(ctx)
    try:
        project.remove_target_language(lang)
        typer.secho(f"Target language {lang.value} and its directory removed.", fg=typer.colors.GREEN)
    except errors.RemoveLanguageError as e:
        typer.secho(f"Error removing language: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

@app.command("sync")
def sync_files(ctx: typer.Context):
    """Synchronizes untranslatable files from the source to all target directories."""
    project = get_project_from_context(ctx)
    try:
        project.sync_untranslatable_files()
        typer.secho("Untranslatable files synchronized successfully.", fg=typer.colors.GREEN)
    except errors.SyncFilesError as e:
        typer.secho(f"Error synchronizing files: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

@app.command("add")
def mark_translatable(
    ctx: typer.Context,
    file_paths: Annotated[list[str], typer.Argument(help="Path to the file (relative to project root or absolute).")]
):
    """Marks a file in the source directory as translatable."""
    project = get_project_from_context(ctx)
    try:
        for file_path in file_paths:
            project.set_file_translatability(file_path, True)
            typer.secho(f"File '{file_path}' marked as translatable.", fg=typer.colors.GREEN)
    except errors.AddTranslatableFileError as e:
        typer.secho(f"Error marking file as translatable: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

@app.command("remove")
def mark_untranslatable(
    ctx: typer.Context,
    file_paths: Annotated[list[str], typer.Argument(help="Path to the file (relative to project root or absolute).")]
):
    """Marks a file in the source directory as untranslatable."""
    project = get_project_from_context(ctx)
    try:
        for file_path in file_paths:
            project.set_file_translatability(file_path, False)
            typer.secho(f"File '{file_path}' marked as untranslatable.", fg=typer.colors.GREEN)
    except errors.AddTranslatableFileError as e:
        typer.secho(f"Error marking file as untranslatable: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

@app.command("list")
def list_translatable_files(ctx: typer.Context):
    """Lists all files marked as translatable in the source directory."""
    project = get_project_from_context(ctx)
    try:
        files = project.get_translatable_files()
        if not files:
            typer.secho("No translatable files found.", fg=typer.colors.YELLOW)
            return
        typer.secho("Translatable files:", fg=typer.colors.BLUE)
        for f_path in files:
            # Try to make path relative to project root for cleaner display
            try:
                display_path = f_path.relative_to(project.root_path)
            except ValueError:
                display_path = f_path # If not under root_path (should not happen)
            typer.echo(f"  {display_path}")
    except errors.GetTranslatableFilesError as e:
        typer.secho(f"Error listing translatable files: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

@app.command("info")
def info_on_project(ctx: typer.Context):
    """
    Provides an info about the project
    """
    project = get_project_from_context(ctx)
    print("Project Information:");
    print("\tProject Name: {}".format(project.config.get_name()) )
    print("\tRoot Path: {}".format(project.root_path))

    src_dir = project.config.get_src_dir()
    if src_dir is None:
        print("\tSource directory: Is not set")
    else:
        src_dir_name = src_dir.get_path().name
        src_dir_lang = src_dir.get_lang()
        print("\tSource language: {}".format(src_dir_lang))
        print("\tSource directory: {}".format(src_dir_name))

    target_langs = project._get_target_languages()
    if len( target_langs ) == 0:
        print("\tTarget langauges: There is no target languages")
    else:
        print("Target languages:")
        for lang in target_langs:
            tgt_dir = project.config.get_target_dir_path_by_lang(lang)
            tgt_dir_name = None if tgt_dir is None else tgt_dir.name
            print("\tLanguage: {:<10} | Directory: {}".format(lang, tgt_dir_name))


# --- Translation Commands ---
translate_app = typer.Typer(name="translate", help="Translate files", no_args_is_help=True)
app.add_typer(translate_app) # Sub-command of project

def _read_vocab_from_file(path: Path) -> list[dict]:
    with open(path, "r") as f:
        reader = csv.DictReader(f)
        return list(reader)

async def _translate_file_command(project: Project, file_path_str: str, lang: Language, vocab: Path | None):
    try:
        vocabulary = None
        if vocab != None:
            vocabulary = vocab_list_from_vocab_db(_read_vocab_from_file(vocab), project.get_source_langugage(), lang)

        await project.translate_single_file(file_path_str, lang, vocabulary) # WARNING: remove None
        typer.secho(f"File '{file_path_str}' translated to {lang.value} successfully.", fg=typer.colors.GREEN)
    except errors.TranslateFileError as e:
        typer.secho(f"Error translating file '{file_path_str}': {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"An unexpected error occurred during translation: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

@translate_app.command("file")
def translate_file_cli(
    ctx: typer.Context,
    file_path: Annotated[str, typer.Argument(help="Path to the translatable file.")],
    lang: Annotated[Language, typer.Argument(help="Target language for translation.", case_sensitive=False)],
    vocabulary: Annotated[Path | None, typer.Option(help="A path to the csv file with the vocabulary.", case_sensitive=False)] = None
):
    """Translates a single specified translatable file."""
    project = get_project_from_context(ctx)
    asyncio.run(_translate_file_command(project, file_path, lang, vocabulary))


async def _translate_all_command(project: Project, lang: Language, vocab: Path | None):
    try:
        vocabulary = None
        if vocab != None:
            vocabulary = vocab_list_from_vocab_db(_read_vocab_from_file(vocab), project.get_source_langugage(), lang)

        await project.translate_all_for_language(lang, vocabulary) # WARNING: remove None
        typer.secho(f"All translatable files processed for language {lang.value}.", fg=typer.colors.GREEN)
    except errors.TranslateFileError as e: # Should be caught by individual file errors mostly
        typer.secho(f"Error during 'translate all' for {lang.value}: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"An unexpected error occurred during 'translate all': {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

@translate_app.command("all")
def translate_all_cli(
    ctx: typer.Context,
    lang: Annotated[Language, typer.Argument(help="Target language for translation.", case_sensitive=False)],
    vocabulary: Annotated[Path | None, typer.Option(help="A path to the csv file with the vocabulary.", case_sensitive=False)] = None
):
    """Translates all translatable files to the specified language."""
    project = get_project_from_context(ctx)
    asyncio.run(_translate_all_command(project, lang, vocabulary))


# ============ correct app =============
correct_app = typer.Typer(name="correct", help="Correct translation", no_args_is_help=True)
app.add_typer(correct_app) # Sub-command of project

@correct_app.command("file")
def correct_file_cli(
    ctx: typer.Context,
    file_path: Annotated[str, typer.Argument(help="Path to the file to correct translation in.")],
):
    """Corrects the translation of a single specified file."""
    project = get_project_from_context(ctx)
    try:
        project.correct_translation_single_file(file_path)
        typer.secho(f"Verifying the contents to translate in the {file_path} file.", fg=typer.colors.GREEN)
    except errors.CorrectTranslationError as e: # Should be caught by individual file errors mostly
        typer.secho(f"Error during 'correct file' for {file_path}: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"An unexpected error occurred during 'correct file': {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

@correct_app.command("all")
def correct_all_cli(
    ctx: typer.Context,
    lang: Annotated[Language, typer.Argument(help="Target language for correction.", case_sensitive=False)]
):
    """Corrects the translation of all the files of the specified language."""
    project = get_project_from_context(ctx)
    try:
        project.correct_translation_for_lang(lang)
        typer.secho(f"All files processed for correcting language {lang.value}.", fg=typer.colors.GREEN)
    except errors.CorrectTranslationError as e: # Should be caught by individual file errors mostly
        typer.secho(f"Error during 'correct all' for {lang.value}: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"An unexpected error occurred during 'correct all': {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

### DEBUG!
@app.command("diff")
def info_on_project(ctx: typer.Context):
    """
    Provides an info about the project
    """
    project = get_project_from_context(ctx)
    txt = "Soit $E$ un espace vectoriel normé"
    txt = r'''
\begin{preuve}
    $E = \mathcal{C}([a, b], \R)$ et $\|f\|_1 = \int_{{a}}^{{b}} {|f(x)|} \: d{x}$ norme sur $\mathcal{C}([a, b], \R)$. Je fixe $m \in \mathcal{C}([a, b], \R)$ et $A: f \to mf$. $Af(x) = m(x)f(x)$. 
    \begin{itemize}
        \item $A \in L(E)$ évident
        \item $A \in B(E)$?
    \end{itemize}
    Trouver $c \ge 0$ telle que 
    \[
    \|Af\|_{1} \le c \|f\|_1 \quad \forall f \in E
    \] 
    \begin{align*}
        \|Af\|_1 = \int_{{a}}^{{b}} {|m(x)f(x)|} \: d{x}
    \end{align*}
    \begin{align*}
        |m(x)f(x)| \le |m(x)| |f(x)| \le \|m\|_{\infty} |f(x)|
    \end{align*}
    \[
        \|m\|_{\infty} = \sup_{x \in [a, b]}|m(x)|
    \] 
    \begin{align*}
        \int_{{a}}^{{b}} {|m(x)f(x)|} \: d{x} \le \|m\|_{\infty}\int_{{a}}^{{b}} {|f(x)|} \: d{x} = \|m\|_{\infty}\|f\|_1
    \end{align*}
    \[
    c = \|m\|_{\infty}
    \] 
    On a: $A \in B(E)$ et $\|A\| \le \|m\|_{\infty}$. Montrons que $\|A\| = \|m\|_{\infty}$
    \[
        \|A\| = \sup_{\|f\|_1 \le 1} \|Af\|_{1} \overset{?}{=} \|m\|_{\infty} = \sup I \text{ avec } I = \{ \|Af\|_{1} : \|f\|_{1} \le 1 \}
    \] 
    Notons $\alpha = \sup I$
     \begin{enumerate}
        \item $\alpha$ majorant de  $I$
        \item  $\exists (a_n) \, a_n \in I$ avec $a_n \xrightarrow[n \to \infty]{} \alpha$
    \end{enumerate}
    Dans notre cas:
    \begin{itemize}
        \item But: trouver une suite $f_n \in E$ $\|f_n\|_1 \le 1$ et $\|Af_n\|_{1} \to \|m\|_{\infty}$
    \end{itemize}
    $a_n = \|Af_n\|_{1}$ $\|m\|_{\infty} = \sup$ de la fonction $|m|$ sur  $[a, b]$.
     \begin{itemize}
         \item $|m|$ continue:  $\exists x_0 \in [a, b]$ tel que $\|m\|_{\infty} = |m|(x_0)$
    \end{itemize}
    \[
    |m|(x) = |m(x)|
    \] 
\begin{figure}[H]
    \centering
    \incfig{preuve-prop-line-cont-borne}
    \caption{$f_n$}
    \label{fig:preuve-prop-line-cont-borne}
\end{figure}
\[
|m(x)f_n(x)| = |Af(x)| \text{ proche de } |m(x_0)| |f_n(x)|
\] 
$\|f_n\|_{1} = 1$ si $c_n \le 2n$
\[
f_n(x) = \begin{cases}
    0 \text{ si } a \le x \le x_0 - \frac{1}{2n}\\
    2n(1 - n|x - x_0|) \text{ si } |x - x_0| \le \frac{1}{2n}\\
    0 \text{ si } x_0 + \frac{1}{2n} \le x \le b
\end{cases}
\] 
\begin{figure}[H]
    \centering
    \incfig{preuve-lin-cont-bornee-2}
    \caption{$f_n$}
    \label{fig:preuve-lin-cont-bornee-2}
\end{figure}
\[
|m(x)f_n(x) - m(x_0)f_n(x)| \le |m(x) - m(x_0)| |f_n(x)| \le \varepsilon_n|f_n(x)|
\] 
Là où $f_n(x) \neq 0$ $|x - x_0| \le \frac{1}{n}$ donc 
\[
|m(x) - m(x_0)| \le \varepsilon_n \quad \varepsilon_n \xrightarrow[n \to \infty]{} 0
\] 
alors $m$ continue en  $x_0$.
 \begin{align*}
    \|Af_n\|_{1} = \int_{{a}}^{{b}} {|m(x)f_n(x)|} \: d{x} \le \int_{{a}}^{{b}} {|m(x) - m(x_0)| |f_n(x)|} \: d{x} + \int_{{a}}^{{b}} {|m(x_0)| |f_n(x)|} \: d{x} 
\end{align*}
\begin{itemize}
    \item $1^{er}$ terme: $\le \varepsilon_n\|f_n\|_{1} = \varepsilon_n$
    \item $2^{eme}$ terme: $:= \|m\|_{\infty}\|f_n\|_{1} = \|m\|_{\infty}$
\end{itemize}
Alors:
\begin{align*}
    &\|f_n\|_{1} = 1\\
    &\|Af_n\|_{1} \to \|m\|_{\infty}\\
    &\text{donc } \|A\| = \|m\|_{\infty}
\end{align*}
\end{preuve}
    '''
    lang = Language.FRENCH
    txt, score = project.diff(txt, lang)
    print(f"Score: {score}")
    print(f"Txt:\n{txt}")


# --- Main execution for CLI ---
# This callback is for global options like --project-dir if you add them
# For now, it's not strictly needed as get_project_from_context handles loading
# @app.callback()
# def main_global_options(
#    project_dir: Annotated[Optional[Path], typer.Option(help="Path to the project directory (if not current).")] = None
# ):
#    """
#    Directory Translation Tool
#    """
#    # Store project_dir in ctx.obj if needed by subcommands,
#    # or handle it directly in get_project_from_context.
#    pass


if __name__ == "__main__": 
    app()
