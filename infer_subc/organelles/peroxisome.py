import numpy as np
from typing import Dict
from pathlib import Path
import time

from aicssegmentation.core.seg_dot import dot_2d_slice_by_slice_wrapper

from infer_subc.constants import PEROX_CH
from infer_subc.core.file_io import export_inferred_organelle, import_inferred_organelle

from infer_subc.core.img import (
    dot_filter_3,
    scale_and_smooth,
    select_channel_from_raw,
    fill_and_filter_linear_size,
    label_uint16,
)


##########################
#  infer_perox
##########################
def infer_perox( 
        in_img: np.ndarray,
        peroxi_ch: int,
        median_sz: int,
        gauss_sig: float,
        dot_scale_1: float,
        dot_cut_1: float,
        dot_scale_2: float,
        dot_cut_2: float,
        dot_scale_3: float,
        dot_cut_3: float,
        dot_method: str,
        hole_min_width: int,
        hole_max_width: int,
        small_object_width: int,
        fill_filter_method: str
        ) -> np.ndarray:
    """
    Procedure to infer peroxisome from linearly unmixed input.

   Parameters
    ------------
    in_img: 
        a 3d image containing all the channels
    median_sz: 
        width of median filter for signal
    gauss_sig: 
        sigma for gaussian smoothing of  signal
    dot_scale: 
        scales (log_sigma) for dot filter (1,2, and 3)
    dot_cut: 
        threshold for dot filter thresholds (1,2,and 3)
    small_obj_w: 
        minimu object size cutoff for nuclei post-processing
 
    Returns
    -------------
    peroxi_object
        mask defined extent of peroxisome object
    """

    ###################
    # EXTRACT
    ###################    
    peroxi = select_channel_from_raw(in_img, peroxi_ch)

    ###################
    # PRE_PROCESSING
    ###################    
    peroxi =  scale_and_smooth(peroxi,
                               median_size = median_sz,
                               gauss_sigma = gauss_sig)

   ###################
    # CORE_PROCESSING
    ###################
    bw = dot_filter_3(peroxi, dot_scale_1, dot_cut_1, dot_scale_2, dot_cut_2, dot_scale_3, dot_cut_3, dot_method)

    ###################
    # POST_PROCESSING
    ###################
    struct_obj = fill_and_filter_linear_size(bw, 
                                             hole_min=hole_min_width, 
                                             hole_max=hole_max_width, 
                                             min_size=small_object_width,
                                             method=fill_filter_method)

    ###################
    # LABELING
    ###################
    struct_obj1 = label_uint16(struct_obj)

    return struct_obj1

# def infer_perox(
#     in_img: np.ndarray,
#     median_sz: int,
#     gauss_sig: float,
#     dot_scale: float,
#     dot_cut: float,
#     small_obj_w: int,
# ) -> np.ndarray:
#     """
#     Procedure to infer peroxisome from linearly unmixed input.

#     Parameters
#      ------------
#      in_img:
#          a 3d image containing all the channels
#     median_sz:
#         width of median filter for signal
#      gauss_sig:
#          sigma for gaussian smoothing of  signal
#      dot_scale:
#          scales (log_sigma) for dot filter (1,2, and 3)
#      dot_cut:
#          threshold for dot filter thresholds (1,2,and 3)
#      small_obj_w:
#          minimu object size cutoff for nuclei post-processing

#      Returns
#      -------------
#      peroxi_object
#          mask defined extent of peroxisome object
#     """
#     peroxi_ch = PEROX_CH
#     ###################
#     # EXTRACT
#     ###################
#     peroxi = select_channel_from_raw(in_img, peroxi_ch)

#     ###################
#     # PRE_PROCESSING
#     ###################
#     peroxi = scale_and_smooth(peroxi, median_sz=median_sz, gauss_sig=gauss_sig)  # skips for median_sz < 2

#     ###################
#     # CORE_PROCESSING
#     ###################
#     s3_param = [[dot_scale, dot_cut]]
#     bw = dot_2d_slice_by_slice_wrapper(peroxi, s3_param)

#     ###################
#     # POST_PROCESSING
#     ###################
#     # struct_obj = size_filter_linear_size(bw, min_size=small_obj_w, connectivity=1)
#     struct_obj = fill_and_filter_linear_size(bw, hole_min=0, hole_max=0, min_size=small_obj_w)

#     return label_uint16(struct_obj)


### CONVENIENCE / TESTING PROCEDURES


##########################
#  fixed_infer_perox
##########################
def fixed_infer_perox(in_img: np.ndarray) -> np.ndarray:
    """
    Procedure to infer peroxisome from linearly unmixed input with fixed parameters.

   Parameters
    ------------
    in_img: np.ndarray
        a 3d image containing all the channels
        
    Returns
    -------------
    peroxi_object
        mask defined extent of peroxisome object
    """
    peroxi_ch = 4
    median_sz = 0
    gauss_sig = 1.34
    dot_scale_1 = 1
    dot_cut_1 = 0.06
    dot_scale_2 = 0
    dot_cut_2 = 0
    dot_scale_3 = 0
    dot_cut_3 = 0
    dot_method = "3D"
    hole_min_width = 0
    hole_max_width = 0
    small_object_width = 2
    fill_filter_method = "3D"

    return infer_perox(
        in_img,
        peroxi_ch,
        median_sz,
        gauss_sig,
        dot_scale_1,
        dot_cut_1,
        dot_scale_2,
        dot_cut_2, 
        dot_scale_3,
        dot_cut_3,
        dot_method,
        hole_min_width,
        hole_max_width,
        small_object_width,
        fill_filter_method)

# def fixed_infer_perox(in_img: np.ndarray) -> np.ndarray:
#     """
#       Procedure to infer peroxisome from linearly unmixed input with fixed parameters.

#     Parameters
#      ------------
#      in_img: np.ndarray
#          a 3d image containing all the channels

#      Returns
#      -------------
#      peroxi_object
#          mask defined extent of peroxisome object
#     """
#     median_sz = 0
#     gauss_sig = 3.0
#     dot_scale = 1.0
#     dot_cut = 0.01
#     small_obj_w = 2

#     return infer_perox(
#         in_img,
#         median_sz,
#         gauss_sig,
#         dot_scale,
#         dot_cut,
#         small_obj_w,
#     )


def infer_and_export_perox(in_img: np.ndarray, meta_dict: Dict, out_data_path: Path) -> np.ndarray:
    """
    infer peroxisome and write inferred peroxisome to ome.tif file

    Parameters
    ------------
    in_img:
        a 3d  np.ndarray image of the inferred organelle (labels or boolean)
    meta_dict:
        dictionary of meta-data (ome)
    out_data_path:
        Path object where tiffs are written to

    Returns
    -------------
    exported file name

    """
    peroxisome = fixed_infer_perox(in_img)
    out_file_n = export_inferred_organelle(peroxisome, "perox", meta_dict, out_data_path)
    print(f"inferred peroxisome. wrote {out_file_n}")
    return peroxisome


def get_perox(in_img: np.ndarray, meta_dict: Dict, out_data_path: Path) -> np.ndarray:
    """
    load peroxisome if it exists, otherwise calculate and write to ome.tif file

    Parameters
    ------------
    in_img:
        a 3d  np.ndarray image of the inferred organelle (labels or boolean)
    meta_dict:
        dictionary of meta-data (ome)
    out_data_path:
        Path object where tiffs are written to

    Returns
    -------------
    exported file name

    """
    try:
        start = time.time()
        print("starting segmentation...")
        peroxisome = import_inferred_organelle("perox", meta_dict, out_data_path)
        end = time.time()
        print(f"loaded peroxisome in ({(end - start):0.2f}) sec")
    except:
        start = time.time()
        print("starting segmentation...")
        peroxisome = infer_and_export_perox(in_img, meta_dict, out_data_path)
        end = time.time()
        print(f"inferred (and exported) peroxisome in ({(end - start):0.2f}) sec")

    return peroxisome
