import unittest
import logging
import os
import pandas as pd

import setup_GCToo_logger as setup_logger
import GCToo
import slice_gct
import parse_gctoo as pg

logger = logging.getLogger(setup_logger.LOGGER_NAME)
setup_logger.setup(verbose=True)

DATA_DF = pd.DataFrame([[1, 2, 3], [5, 7, 11], [13, 17, 19], [23, 29, 31]],
                       index=["a", "b", "c", "d"], columns=["e", "f", "g"])
ROW_METADATA_DF = pd.DataFrame([["rm1", "rm2"], ["rm3", "rm4"], ["rm5", "rm6"], ["rm7", "rm8"]],
                               index=["a","b","c","d"], columns=["rhd1", "rh2"])
COL_METADATA_DF = pd.DataFrame([["cm1", "cm2"], ["cm3", "cm4"], ["cm5", "cm6"]],
                               index=["e", "f", "g"], columns=["chd1", "chd2"])
IN_GCT = GCToo.GCToo(DATA_DF, ROW_METADATA_DF, COL_METADATA_DF)

FUNCTIONAL_TESTS_DIR = "functional_tests"


class TestDsSlice(unittest.TestCase):

    def test_read_arg(self):
        arg_path = os.path.join(FUNCTIONAL_TESTS_DIR, "test_slice_rid.grp")
        rids = slice_gct._read_arg([arg_path])
        self.assertItemsEqual(rids, ["a", "Bb", "c"])

    def test_read_arg_bad(self):
        with self.assertRaises(AssertionError) as e:
            slice_gct._read_arg("a b c")
        self.assertIn("arg_out must be a list", str(e.exception))

        with self.assertRaises(AssertionError) as e:
            slice_gct._read_arg([1, 2, 3])
        self.assertIn("arg_out must be a list of strings", str(e.exception))

    def test_slice_bools(self):
        out_gct = slice_gct.slice_gctoo(IN_GCT, row_bool=[True, False, True, False], col_bool=[False, False, True])

        # Outputs should be dataframes even if there is only 1 index or column
        pd.util.testing.assert_frame_equal(out_gct.data_df, pd.DataFrame(IN_GCT.data_df.iloc[[0, 2], 2]))
        pd.util.testing.assert_frame_equal(out_gct.row_metadata_df, IN_GCT.row_metadata_df.iloc[[0, 2], :])
        pd.util.testing.assert_frame_equal(out_gct.col_metadata_df, pd.DataFrame(IN_GCT.col_metadata_df.iloc[2, :]).T)

    def test_slice_and_exclude_rids(self):
        out_gct = slice_gct.slice_gctoo(IN_GCT, rid=["a", "c", "d"], exclude_rid=["d"])

        # Outputs should be dataframes even if there is only 1 index or column
        pd.util.testing.assert_frame_equal(out_gct.data_df, IN_GCT.data_df.iloc[[0, 2], :])
        pd.util.testing.assert_frame_equal(out_gct.row_metadata_df, IN_GCT.row_metadata_df.iloc[[0, 2], :])
        pd.util.testing.assert_frame_equal(out_gct.col_metadata_df, IN_GCT.col_metadata_df)

    def test_slice_cid_and_col_bool(self):
        # cid and col_bool should not both be provided
        with self.assertRaises(AssertionError) as e:
            out_gct = slice_gct.slice_gctoo(IN_GCT, cid=["e", "f", "g"], col_bool=[True, True, False])
        self.assertIn("cid and col_bool", str(e.exception))

    def test_main(self):
        in_gct_path = os.path.join(FUNCTIONAL_TESTS_DIR, "test_slice_in.gct")
        rid_grp_path = os.path.join(FUNCTIONAL_TESTS_DIR, "test_slice_rid.grp")
        out_name = os.path.join(FUNCTIONAL_TESTS_DIR, "test_slice_out.gct")
        expected_out_path = os.path.join(FUNCTIONAL_TESTS_DIR, "test_slice_expected.gct")

        args_string = "-i {} --rid {} -ec {} -o {}".format(
            in_gct_path, rid_grp_path, "f", out_name)
        args = slice_gct.build_parser().parse_args(args_string.split())

        # Run main method
        slice_gct.main(args)

        # Compare output to expected
        out_gct = pg.parse(out_name)
        expected_gct = pg.parse(expected_out_path)

        pd.util.testing.assert_frame_equal(out_gct.data_df, expected_gct.data_df)
        pd.util.testing.assert_frame_equal(out_gct.row_metadata_df, expected_gct.row_metadata_df)
        pd.util.testing.assert_frame_equal(out_gct.col_metadata_df, expected_gct.col_metadata_df)

        # Clean up
        os.remove(out_name)

if __name__ == '__main__':
    unittest.main()
