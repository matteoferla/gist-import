from __future__ import annotations
import requests, warnings, re
from typing import Optional, Dict, Any, Union
from .imports import get_imports_in_codeblock  # this is not a class, but a function


class GistImporter:
    """
    A very simple class to import cleanly a gist into a project.
    Namely it retrieves the gist and executes it with any given additional named arguments
    in a local context thus not polluting the global namespace.
    If required does a special import of the gist's imports (<3.8).
    The variables in that namespace are then available as items.

    .. code-block:: python

       GistImporter('24d9a319d05773ae219dd678a3aa11be')
       Safeguard = gi['Safeguard']

    One can also run a code block if wanted:

    .. code-block:: python

        gi = GistImporter.from_code_block('foo.append(bar)', foo=[], bar=1)
        assert gi['foo'] == [1]
    """

    def __init__(self, gist_id: str, filename: Optional[str] = None, **kwargs):
        self.gist_id = gist_id
        self.gist_data = self._retrieve_gist_data()
        self.filename: str = self._parse_filename(filename)
        assert self.filename in self.gist_data['files'], f'{self.filename} not found in gist'
        self.gist_file_data: Dict[str, Any] = self.gist_data['files'][self.filename]
        self.gist_codeblock: str = self.gist_file_data['content']
        self.gist_description: str = self.gist_data['description']
        self.gist_owner: str = self.gist_data['owner']['login']
        self.pocket_globals: Dict[str, Any] = {**globals(), **locals(), **kwargs}
        self._run()

    def try_excecuting_gist(self) -> Union[None, Exception]:
        """
        Runs ``excute_gist`` in a try-catch block.

        :return: None or the error if it failed
        """
        try:
            return self.excute_gist()
        except Exception as error:
            return error

    def excute_gist(self) -> None:
        """
        Executes the gist codeblock

        :return: None. exec does not return anything, but its return is returned just in case the global was modified
        """
        return exec(self.gist_codeblock, self.pocket_globals)

    def _retrieve_gist_data(self) -> Dict[str, Any]:
        response: requests.Response = requests.get(f'https://api.github.com/gists/{self.gist_id}')
        response.raise_for_status()
        return response.json()

    def _run(self) -> None:
        output = self.try_excecuting_gist()
        if isinstance(output, NameError):
            warnings.warn('NameError: {output} occured. Trying with imports outside of the excecution context.')
            self.pocket_globals.update(get_imports_in_codeblock(self.gist_codeblock))
            output = self.try_excecuting_gist()
        if isinstance(output, Exception):
            warnings.warn(f'{output.__class__.__name__}: {output} occurred during gist execution.')

    def _parse_filename(self, filename: Optional[str] = None) -> str:
        """
        Gets the first filename from the gist if no filename is specified

        :param filename:
        :return:
        """
        if filename is None:
            return list(self.gist_data['files'].keys())[0]
        return filename

    def __getitem__(self, key):
        return self.pocket_globals[key]

    def __setitem__(self, key, value):
        self.pocket_globals[key] = value

    def __delitem__(self, key):
        del self.pocket_globals[key]

    @classmethod
    def mock(cls, **kwargs) -> GistImporter:
        """
        This make a mock GistImporter object.
        """
        self = cls.__new__(cls)
        self.gist_id = ''
        self.gist_data = {}
        self.filename = None
        self.gist_file_data = {}
        self.gist_codeblock = ''
        self.gist_description = ''
        self.gist_owner = ''
        self.pocket_globals = {**globals(), **locals(), **kwargs}
        return self


    @classmethod
    def from_code_block(cls, code_block: str, **kwargs) -> GistImporter:
        """
        This circumvents the gist by excecuting the code block provided.
        """
        self = cls.mock(**kwargs)
        self.gist_codeblock = code_block
        self._run()
        return self


    @classmethod
    def from_url(cls, url: str, **kwargs) -> GistImporter:
        """
        This excecutes the code from the url provided (not an HTML MIME type but a raw text type file)
        """
        self = cls.mock(**kwargs)
        response: requests.Response = requests.get(url)
        response.raise_for_status()
        self.gist_codeblock = response.text
        self._run()
        return self

    @classmethod
    def from_github(cls, url: str, **kwargs) -> GistImporter:
        """
        This excecutes the code from a GitHub url provided.
        But differs from the ``from_url`` method in that a URL from a GitHub page is a HTML page,
        say
        ``https://github.com/username/repo/blob/main/filename.py`` is a HTML page,
        while the "raw" version of the file is a raw text file:
        ``https://raw.githubusercontent.com/username/repo/main/filename.py``

        """
        if 'raw.githubusercontent.com' in url:
            raw_url = url
        elif 'github.com/' not in url:
            raise ValueError('The url provided is not a GitHub url.')
        else:
            raw_url = url.replace('github.com', 'raw.githubusercontent.com')\
                         .replace('blob/', '')
        return cls.from_url(raw_url, **kwargs)
