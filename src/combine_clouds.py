#%%
import pdal
import numpy as np
from pathlib import Path

import argparse

#%%
def parse_arguments():
    '''parses the arguments, returns args'''
    # init parser
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--in_laz',
        type=str,
        required=True,
        help='Path to input las/z file'
    )

    parser.add_argument(
        '--out_dir',
        type=str,
        required=True,
        help='Path to directory where results will be written'
    )

    parser.add_argument(
        '--count',
        type=str,
        required=False,
        help='Max number of points to read from laz'
    )

    args = parser.parse_args()
    args.in_laz = Path(args.in_laz).resolve()
    args.out_dir = Path(args.out_dir).resolve()

    return args

#%%

ARGS = parse_arguments()
stem = ARGS.in_laz.stem
out_hag_path = ARGS.out_dir / f'{stem}_hag.tif'
hag_las_path = ARGS.out_dir / f'{stem}_hag.las'

ground_las_path = ARGS.out_dir / f'{stem}_ground.las'
ground_tif_path = ARGS.out_dir / f'{stem}_ground.tif'
#%%

pipe = pdal.Reader.las(filename=ARGS.in_laz).pipeline()
if ARGS.count is not None:
    pipe = pdal.Reader.las(filename=ARGS.in_laz, count=ARGS.count).pipeline()

pipe |= pdal.Filter.smrf(where='ReturnNumber == NumberOfReturns')
pipe |= pdal.Filter.hag_nn(count=3)
pipe |= pdal.Writer.las(
    forward='all',
    extra_dims='all',
    filename=hag_las_path,
    minor_version=4,)
pipe |= pdal.Writer.gdal(
    dimension='HeightAboveGround',
    resolution=0.1,
    filename=out_hag_path
)
pipe |= pdal.Filter.expression(expression='Classification == 2')
pipe |= pdal.Writer.las(forward='all', filename=ground_las_path)
pipe |= pdal.Writer.gdal(resolution=0.1, filename=ground_tif_path)
n = pipe.execute()
print(n)

# %%
