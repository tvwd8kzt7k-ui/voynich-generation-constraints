"""Adapter integrity and error-path tests; no network or generated data required."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from external_validation.timm import run as audit


def synthetic_text(body=None):
    header = "\n".join(("#Line count: 1200", "#text.lines_per_page=29",
                        "#VMS tokens count: 7678 (70 %)",
                        "#None VMS token count: 3156 (30 %)"))
    return header + "\n" + (body if body is not None else "qokedy\n" * 1200)


class AdapterTests(unittest.TestCase):
    def test_valid_body_keeps_line_order_without_manuscript_metadata(self):
        lines, rows, by_line, n = audit.parse_timm(synthetic_text())
        self.assertEqual((len(lines), len(rows), len(by_line), n), (1200, 1200, 1200, 1200))
        self.assertEqual((rows[29]['page'], rows[29]['line']), (1, 0))
        self.assertTrue({'bifolio', 'context', 'hand'}.isdisjoint(rows[0]))

    def test_malformed_body_is_not_silently_filtered(self):
        for body in ('qokedy\n' * 1199, 'qokedy\n' * 1199 + '\n',
                     'qokedy\n' * 1199 + '#hidden\n', 'qokedy\n' * 1199 + 'qokedy!\n'):
            with self.subTest(last_line=body[-20:]), self.assertRaises(ValueError):
                audit.generated_lines(synthetic_text(body))

    def test_missing_or_duplicate_header_rejected(self):
        for text in (synthetic_text().replace('#text.lines_per_page=29\n', ''),
                     '#Line count: 1200\n' + synthetic_text()):
            with self.assertRaises(ValueError):
                audit.generated_lines(text)

    def test_dictionary_membership_and_decoder_validity_are_distinct(self):
        lines = ['qokedy g chedy x']
        result = audit.dictionary_audit(synthetic_text(), lines, {'qokedy', 'g'})
        self.assertEqual(list(result['cross_classification'].values()), [1, 1, 1, 1])

    def test_complete_pages_use_raw_line_count(self):
        # Two complete pages remain complete even if their last lines contain
        # no valid words; a third, partial page is excluded.
        rows = [{'page': 0}, {'page': 1}, {'page': 2}]
        self.assertEqual(audit.complete_page_rows(rows, 59), [[rows[0]], [rows[1]]])
        self.assertEqual(audit.complete_page_rows(rows[:2], 58), [[rows[0]], [rows[1]]])

    def test_sampling_is_deterministic_unique_and_bounded(self):
        pop = list(range(30))
        x = audit.sample_without_replacement(pop, 20, 20260928)
        self.assertEqual(x, audit.sample_without_replacement(pop, 20, 20260928))
        self.assertEqual(len(set(x)), 20)
        self.assertEqual(pop, list(range(30)))
        with self.assertRaises(ValueError):
            audit.sample_without_replacement(pop, 31, 20260928)

    def test_canonical_modal_tie_order_is_preserved(self):
        rows = [{'exact': ('e',)}, {'exact': ('E',)}]
        self.assertEqual(audit.modal_stats(rows, 0)['mode'], 'E')

    def test_box0_tie_sensitivity_does_not_replace_primary_rule(self):
        rows = []
        for erun, end, n in [('E', 'l', 24), ('E', 'r', 18), ('e', 'l', 18), ('e', 'r', 24)]:
            exact = [''] * 12
            exact[6], exact[10] = erun, end
            exact = tuple(exact)
            rows.extend({'exact': exact, 'family': audit.family_of(exact)} for _ in range(n))
        result = audit.lowdim(rows)
        self.assertEqual(result['weighted_box_coverage']['box0'], 24 / 84)
        self.assertEqual(result['lowercase_first_tie_box0_sensitivity'], 18 / 84)

    def test_comparison_rejects_missing_nonfinite_and_wrong_shapes(self):
        for actual in ({}, {'x': float('nan')}, {'x': float('inf')}, {'x': 2.0}, {'x': '1.0'}):
            self.assertTrue(audit.compare_subset(actual, {'x': 1.0}))
        self.assertTrue(audit.compare_subset({'x': []}, {'x': {'y': 1}}))
        self.assertTrue(audit.compare_subset({'x': {}}, {'x': [1]}))
        self.assertFalse(audit.compare_subset({'x': 1.0, 'extra': 2}, {'x': 1.0}))


class InputIntegrityTests(unittest.TestCase):
    def test_cached_wrong_blob_fails_without_refetch(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'input.txt'
            p.write_bytes(b'wrong')
            with patch.object(audit.urllib.request, 'urlopen') as fetch:
                with self.assertRaisesRegex(RuntimeError, 'Git blob SHA-1 mismatch'):
                    audit.fetch_verified('https://example.invalid/', p, audit.TIMM_BLOB_SHA1)
                fetch.assert_not_called()
            self.assertEqual(p.read_bytes(), b'wrong')

    def test_missing_input_without_fetch_fails(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(audit.urllib.request, 'urlopen') as fetch:
            with self.assertRaisesRegex(RuntimeError, 'missing input'):
                audit.fetch_verified('https://example.invalid/', Path(tmp) / 'missing', 'bad', False)
            fetch.assert_not_called()

    def test_failed_download_identity_is_never_cached(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(audit.urllib.request, 'urlopen') as fetch:
            p = Path(tmp) / 'input.txt'
            fetch.return_value.__enter__.return_value.read.return_value = b'wrong'
            with self.assertRaisesRegex(RuntimeError, 'Git blob SHA-1 mismatch'):
                audit.fetch_verified('https://example.invalid/', p, audit.TIMM_BLOB_SHA1)
            self.assertFalse(p.exists())

    def test_cli_missing_input_has_nonzero_exit_and_json_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'result.json'
            proc = subprocess.run([sys.executable, str(audit.HERE / 'run.py'),
                                   '--timm-input', str(Path(tmp) / 'missing'),
                                   '--output', str(output)], capture_output=True, text=True)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn('missing input', proc.stderr)
            self.assertNotIn('CHECK OK', proc.stdout)
            self.assertEqual(json.loads(output.read_text())['verification']['status'], 'failed')


if __name__ == '__main__':
    unittest.main()
