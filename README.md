# InSAR
Scripts to aid in processing InSAR data with GMTSAR, as well as post-processing SBAS analysis in python  
**ers_rename_raw_data.sh:** this shell script renames ERS C-band images downloaded from https://scihub.copernicus.eu/dhus/#/home to a format GMTSAR can use  
**sbas_list.py:** makes a list of interferogram pairs based on a user-defined temporal and spatial baseline  
**snaphu_dec.csh:** modified shell script from GMTSAR code. This unwraps interferograms after multi-looking them to speed up the process.  
**unwrap_igrams.sh:** this runs snaphu_dec.csh for each interferogram pair.  
**tm.py:** makes a file called 'tm.out' which is used for SBAS modeling  
**sbas_funs.py:** functions for running SBAS based on Berardino et al., 2002; Sansosti et al., 2010. Creates a time series of deformation from a stack of interferogram pairs.  
