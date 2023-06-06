"""
A module to convert Markdown to Jupyter Notebook.
"""

import os
import argparse
import nbformat as nbf

def markdown_to_notebook(md_file_path, ipynb_file_path):
    """
    Convert the content of a Markdown file into a Jupyter notebook.

    Args:
    md_file_path (str): Path to the Markdown file to be converted.
    ipynb_file_path (str): Path to the output Jupyter notebook file.
    """
    with open(md_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    notebook = nbf.v4.new_notebook()

    notebook['cells'] = [nbf.v4.new_markdown_cell(content)]

    with open(ipynb_file_path, 'w', encoding='utf-8') as file:
        nbf.write(notebook, file)

def get_args():
    """
    Parse command line arguments.

    Returns:
    argparse.Namespace: The parsed command line arguments.
    """
    parser = argparse.ArgumentParser(description='Convert Markdown to Jupyter Notebook.')
    parser.add_argument('-i', '--input', help='Input Markdown file', required=True)
    parser.add_argument('-o', '--output', help='Output Jupyter Notebook file')
    args = parser.parse_args()

    # Use the base name of the input file as the default output file name
    if not args.output:
        base_name = os.path.splitext(os.path.basename(args.input))[0]
        args.output = f"{base_name}.ipynb"

    return args

def main():
    """
    The main function of the script. Gets command line arguments
    and converts the input Markdown file to a Jupyter notebook.
    """
    args = get_args()
    markdown_to_notebook(args.input, args.output)

if __name__ == "__main__":
    main()
