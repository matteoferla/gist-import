__all__ = ['get_imports_in_codeblock', 'get_import_lines', 'import_imports']

import re
import types
import importlib
from typing import Dict, Any, NoReturn, Iterator, List


def get_imports_in_codeblock(codeblock: str) -> Dict[str, Any]:
    """
    Given a codeblock (str) return a dictionary of key=names and value=obj
    of the objects imported in the codeblock

    :param codeblock:
    :return:
    """
    import_lines: List[str] = get_import_lines(codeblock)
    return {k: v for import_line in import_lines for k, v in import_imports(import_line).items()}

# ------------------------------------------------------------

def get_import_lines(codeblock: str) -> List[str]:
    """
    Extract the import lines (str) in the codeblock
    called by ``get_imports_in_codeblock``
    can deal with multiline imports via brackets or backslash
    
    :param codeblock: 
    :return: 
    """
    import_lines = []
    try:
        lines = iter(codeblock.split('\n'))
        while True:
            line = _get_next_line(lines)
            if 'import' in line:
                import_lines.append(line.strip())
    except StopIteration:
        return import_lines
    # else is impossible (endless file)


def _get_next_line(lines: Iterator) -> str:
    """
    Internal function called by get_import_lines
    
    :param lines: 
    :return: 
    """
    line = next(lines)
    if not line:
        return ''
    if line[-1] == '\\':  # newline is escaped
        line = line[:-1]
        line += _get_next_line(lines)
    line = re.sub('#.*', '', line)  # uncomment first
    if line.count('(') > line.count(')'):  # unclosed
        line += _get_next_line(lines)
    return line


# ------------------------------------------------------------

def import_imports(import_line: str) -> Dict[str, Any]:
    """
    Given an import line ``from foo import bar``
    returns {'bar': bar}
    Can deal with star-imports.

    :param import_line:
    :return:
    """
    if 'from ' in import_line:
        imports = import_from_import(re.sub(r' as .*', '', import_line))
    else:
        imports = import_direct_import(re.sub(r' as .*', '', import_line))
    if ' as ' in import_line:
        import_rex = re.search(r'as (.*)')
        assert_rex(import_rex, import_line)
        new_names = re.findall(r'(\w+)', import_rex.group(1))
        assert len(new_names) == len(imports), f'Length mismatch for {import_line}'
        return {new: imports[old] for new, old in zip(new_names, imports.keys())}
    return imports


def assert_rex(import_rex: re.Match, import_line: str) -> NoReturn:
    if not import_rex:
        raise ValueError(f'Failed to parse {import_line}')


def import_from_import(import_line: str) -> Dict[str, Any]:
    """
    ``from foo import bar`` or ``from foo import *``
    """
    import_rex = re.match(r'from\s+(\S*?)\s+import\s+(.*)', import_line)
    assert_rex(import_rex, import_line)
    module_name: str = import_rex.group(1)
    imported_names: str = import_rex.group(2)
    module = importlib.import_module(module_name)
    if imported_names != '*':
        # regular from-import
        imported_names: list = re.findall('(\w+)', imported_names)
        return {name: obj for name, obj in module.__dict__.items() if name in imported_names}
    elif hasattr(module, '__all__'):
        # star import from __all__ module
        return {name: getattr(module, name) for name in module.__all__}
    else:
        # star import from module without __all__
        return module.__dict__


def import_direct_import(import_line) -> Dict[str, types.ModuleType]:
    """
    ``import foo``
    """
    import_rex = re.match(r'import\s+(.*)', import_line)
    assert_rex(import_rex, import_line)
    module_name: str = import_rex.group(1)
    return {module_name: importlib.import_module(module_name)}
