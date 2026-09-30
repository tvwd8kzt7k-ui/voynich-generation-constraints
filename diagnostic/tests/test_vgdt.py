import importlib.util
import pathlib
import unittest
import sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("vgdt",ROOT/"vgdt.py")
vgdt=importlib.util.module_from_spec(spec); sys.modules["vgdt"]=vgdt; spec.loader.exec_module(vgdt)

class CoreTests(unittest.TestCase):
    def test_known_words_decode(self):
        for w in ["qokedy","chedy","daiin","sheedy","otaiin"]:
            self.assertIsNotNone(vgdt.decode_word(w),w)

    def test_family_cue_is_deterministic(self):
        a=vgdt.decode_word("qokedy")
        b=vgdt.decode_word("qokedy")
        self.assertEqual(a["family"],b["family"])
        self.assertEqual(a["cue"],b["cue"])
        self.assertLessEqual(len(a["cue"]),2)

    def test_block_adapter_keeps_single_line_for_spectrum_not_nulls(self):
        c=vgdt.parse_blocks("qokedy\n\nqokedy\nchedy\n")
        self.assertEqual(len(c.all_units),2)
        self.assertEqual(len(c.analysis_units),1)
        self.assertEqual(c.valid_tokens,3)

    def test_line_null_preserves_line_cue_family_multiset(self):
        c=vgdt.parse_blocks("qokedy qokedy chedy\nqokedy chedy qokedy\n")
        u=vgdt.encode_units(c)[0]
        p=vgdt.permute_families(u,vgdt.Mulberry32(123),"line")
        for gm in u["line_groups"]:
            for inds in gm.values():
                self.assertEqual(sorted(u["F"][i] for i in inds), sorted(p[i] for i in inds))

    def test_profile_has_no_similarity_score(self):
        c=vgdt.parse_blocks("qokedy qokedy\nqokedy chedy\n")
        p=vgdt.profile(c,4)
        self.assertNotIn("similarity",p)
        self.assertIn("line_plus_cue_null",p)

    def test_expected_subset_comparison(self):
        actual={"a":1,"b":{"x":0.25,"extra":99},"extra":"ok"}
        self.assertEqual(vgdt._compare_expected(actual,{"a":1,"b":{"x":0.25}}),[])
        self.assertTrue(vgdt._compare_expected(actual,{"a":2}))

    def test_expected_float_tolerance(self):
        self.assertEqual(vgdt._compare_expected({"x":1.0+1e-13},{"x":1.0}),[])
        self.assertTrue(vgdt._compare_expected({"x":1.001},{"x":1.0}))

    def test_timm_trailing_newline_does_not_create_extra_line(self):
        text="# header\nqokedy\n"*0
        # Initial comment lines are headers; exactly 30 body lines make 2 units,
        # with one line in the final partial unit.
        text="# demo\n" + "qokedy\n"*30
        c=vgdt.parse_timm(text)
        self.assertEqual(c.metadata["lines"],30)
        self.assertEqual(c.metadata["outer_units"],2)
        self.assertEqual(c.metadata["partial_final_unit_lines"],1)

    def test_reference_fixture_protocol_matches_tool(self):
        import json
        fixture=json.loads((ROOT/"REFERENCE_EXPECTATIONS.json").read_text())
        self.assertEqual(fixture["protocol"],vgdt.PROTOCOL_ID)

if __name__=="__main__": unittest.main()
