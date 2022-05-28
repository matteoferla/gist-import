import unittest
from gist_import import GistImporter

class MyTestCase(unittest.TestCase):
    def test_GistImporter(self):
        gi = GistImporter('24d9a319d05773ae219dd678a3aa11be')
        self.assertIsInstance(gi['Safeguard'], type)

    def test_kwargs(self):
        gi = GistImporter.from_code_block('foo.append(bar)', foo=[], bar=1)
        self.assertEqual(gi['foo'], [1])

if __name__ == '__main__':
    unittest.main()
