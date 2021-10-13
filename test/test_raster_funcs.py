import dask
import numpy as np
import scipy
import unittest
import rioxarray as rxr
import xarray as xr
from scipy import ndimage

from raster_tools import Raster, band_concat
from raster_tools._types import (
    DTYPE_INPUT_TO_DTYPE,
    U8,
    U16,
    U32,
    U64,
    I8,
    I16,
    I32,
    I64,
    F16,
    F32,
    F64,
    F128,
    BOOL,
)


def rs_eq_array(rs, ar):
    return (rs._rs.values == ar).all()


class TestBandConcat(unittest.TestCase):
    def test_band_concat(self):
        rs1 = Raster("test/data/elevation_small.tif")
        rs2 = Raster("test/data/elevation2_small.tif")
        rsnp1 = rs1._rs.values
        rsnp2 = rs2._rs.values
        truth = np.concatenate((rsnp1, rsnp2))
        test = band_concat([rs1, rs2])
        self.assertEqual(test.shape, truth.shape)
        self.assertTrue(rs_eq_array(test, truth))
        truth = np.concatenate((rsnp1, rsnp1, rsnp2, truth))
        test = band_concat([rs1, rs1, rs2, test])
        self.assertEqual(test.shape, truth.shape)
        self.assertTrue(rs_eq_array(test, truth))

    def test_band_concat_band_dim_values(self):
        rs1 = Raster("test/data/elevation_small.tif")
        rs2 = Raster("test/data/elevation2_small.tif")
        test = band_concat([rs1, rs2])
        # Make sure that band is now an increaseing list starting at 1 and
        # incrementing by 1
        self.assertTrue(all(test._rs.band == [1, 2]))
        test = band_concat([rs1, test, rs2])
        self.assertTrue(all(test._rs.band == [1, 2, 3, 4]))

    def test_band_concat_path_inputs(self):
        rs1 = Raster("test/data/elevation_small.tif")
        rs2 = Raster("test/data/elevation2_small.tif")
        rsnp1 = rs1._rs.values
        rsnp2 = rs2._rs.values
        truth = np.concatenate((rsnp1, rsnp2, rsnp1, rsnp2))
        test = band_concat(
            [
                rs1,
                rs2,
                "test/data/elevation_small.tif",
                "test/data/elevation2_small.tif",
            ]
        )
        self.assertEqual(test.shape, truth.shape)
        self.assertTrue(rs_eq_array(test, truth))

    def test_band_concat_errors(self):
        rs1 = Raster("test/data/elevation_small.tif")
        rs2 = Raster("test/data/elevation2_small.tif")
        rs3 = Raster("test/data/elevation.tif")
        with self.assertRaises(ValueError):
            band_concat([])
        with self.assertRaises(ValueError):
            band_concat([rs1, rs2, rs3])
        with self.assertRaises(ValueError):
            band_concat([rs3, rs2])