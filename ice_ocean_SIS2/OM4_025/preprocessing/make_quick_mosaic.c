
#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <string.h>
#include <math.h>
#include <unistd.h>
#include "mpp.h"
#include "mpp_io.h"
#include "constant.h"
#include "tool_util.h"
#include "read_mosaic.h"
#include "create_xgrid.h"
#define AREA_RATIO_THRESH (1.e-6)
#define AREA_RATIO_THRESH2 (1.e-4)

char *usage[] = {
  "",
  "  make_quick_mosaic --input_mosaic input_mosaic.nc [--mosaic_name mosaic_name]",
  "                    [--ocean_topog ocean_topog.nc] [--sea_level #]            ",
  "                    [--reproduce_siena]                                       ",
  " ",
  "make_quick_mosaic generate a complete grid a FMS coupler. When --ocean_topog  ",
  "is not specified, it takes a coupled mosaic as input_mosaic. Otherwise it     ",
  "takes a solo mosaic as input_mosaic. The atmosphere, ocean and land grid will ",
  "be the same. The land/sea mask will be decided by the land/sea mask of        ",
  "input_mosaic if ocean_topog is not specified, otherwise by the ocean_topog    ",
  "file.                                                                         ",
  "                                                                              ",
  "make_quick_mosaic takes the following flags:                                  ",
  "                                                                              ",
  "REQUIRED:                                                                     ",
  "                                                                              ",
  "--input_mosaic input_mosaic.nc: specify the input mosaic file name.           ",
  "                                                                              ",
  "OPTIONAL FLAGS                                                                ",
  "                                                                              ",
  "--mosaic_name mosaic_name   : coupler mosaic name. The output coupler mosaic  ",
  "                              file will be mosaic_name.nc. default value is   ",
  "                              'quick_mosaic'                                  ",
  "                                                                              ",
  "--ocean_topog ocean_topog.nc: ocean topography file.                          ",
  "--sea_level #               : specify the sea level ( in meters ) and its     ",
  "                              value will be used to determine land/sea mask.  ",
  "                              When topography of a grid cell is less than sea ",
  "                              level, this grid cell will be land, otherwise   ",
  "                              it will be ocean. Default value is 0.           ",
  " ",
  "--reproduce_siena              Set to reproduce siena shared codes results    ",
  "    ",
  "",
  NULL };


char grid_version[] = "0.2";
char tagname[] = "$Name: fre-nctools-bronx-10 $";

void get_file_name(char *file, char *filename)
{
  char *fptr=NULL;
  int siz;
  
  fptr = strrchr(file, '/');

    if(!fptr) {
      strcpy(filename, file);
    }
    else {
      ++fptr;
      strcpy(filename, fptr);      
    }
};



int main (int argc, char *argv[])
{
  int c, n, i;
  int errflg = (argc == 1);
  int    option_index = 0;
  int fid, vid, nfile_aXl, ntiles;

  int *nx, *ny;
  double **lonb, **latb, **land_area, **ocean_area, **cell_area;
  char **axl_file = NULL, **axo_file=NULL, **lxo_file=NULL;
  char **tilename = NULL;
  char **ocn_topog_file = NULL;
  char *input_mosaic = NULL;
  char *ocean_topog = NULL;
  double sea_level = 0.;
  int    reproduce_siena=0;
  char mosaic_name[STRING] = "mosaic", mosaic_file[STRING];
  char griddir[STRING], solo_mosaic[STRING], filepath[STRING];
  char solo_mosaic_full_path[STRING] = "./";
  char solo_mosaic_dir[STRING] = "./";
  char ocn_topog_dir[STRING] = "./";
  char amosaic_name[STRING] = "atmos_mosaic";
  char omosaic_name[STRING] = "ocean_mosaic";
  char lmosaic_name[STRING] = "land_mosaic";
  char history[512];
  int  use_ocean_topog = 0;  
  int  fid_solo_mosaic, tid_gridtile;
  
  static struct option long_options[] = {
    {"input_mosaic",       required_argument, NULL, 'i'},
    {"mosaic_name",        required_argument, NULL, 'm'},
    {"sea_level",          required_argument, NULL, 's'},
    {"ocean_topog",        required_argument, NULL, 'o'},
    {"reproduce_siena",      no_argument,       NULL, 'q'},
    {NULL, 0, NULL, 0}
  };

  
  /*
   * process command line
   */

  while ((c = getopt_long(argc, argv, "i:m:o:", long_options, &option_index) ) != -1)
    switch (c) {
    case 'i': 
      input_mosaic = optarg;
      break;
    case 'm':
      strcpy(mosaic_name,optarg);
      break;
    case 's':
      sea_level = atof(optarg);
      break;
    case 'o':
      ocean_topog = optarg;
      break;
    case 'q':
      reproduce_siena = 1;
      break;  
    case '?':
      errflg++;
    }
  if (errflg || !input_mosaic)  {
    char **u = usage;
    while (*u) { fprintf(stderr, "%s\n", *u); u++; }
    exit(2);
  }  

  strcpy(history,argv[0]);

  for(i=1;i<argc;i++) {
    strcat(history, " ");
    strcat(history, argv[i]);
  }

  /*When ocean_topog specified, input_mosaic is a solo mosaic and will use ocean_topog,
    when ocean_topog is not specified, input_mosaic is a coupled mosaic will use land/sea mask
    for the land grid in the input_mosaic.
  */

  if( ocean_topog ) {
    use_ocean_topog = 1;
    if( ! mpp_field_exist(input_mosaic, "gridfiles") ) {
      mpp_error("make_quick_mosaic: field gridfiles does not exist in input_mosaic");
    }
  }
  else {/* check to make sure it is coupled mosaic */
    use_ocean_topog = 0;
    if( ! mpp_field_exist(input_mosaic, "lnd_mosaic_file") ) {
      mpp_error("make_quick_mosaic: field lnd_mosaic_file does not exist in input_mosaic");
    }
  }

  if(reproduce_siena) set_reproduce_siena_true();
  
  /* First get land grid information */
  
  mpp_init(&argc, &argv);
  sprintf(mosaic_file, "%s.nc", mosaic_name);
  get_file_path(input_mosaic, griddir);
  if( use_ocean_topog ) {
    get_file_name( input_mosaic, solo_mosaic);
  }
  else {
    fid = mpp_open(input_mosaic, MPP_READ);
    vid = mpp_get_varid(fid, "lnd_mosaic_file");
    mpp_get_var_value(fid, vid, solo_mosaic);
    nfile_aXl = mpp_get_dimlen( fid, "nfile_aXl");

    /*make sure the directory that stores the mosaic_file is not current directory */
    { 
      char cur_path[STRING];
    
      if(getcwd(cur_path, STRING) != cur_path ) mpp_error("make_quick_mosaic: The size of cur_path maybe is not big enough");
      printf("The current directory is %s\n", cur_path);
      printf("The mosaic file location is %s\n", griddir);
      if(strcmp(griddir, cur_path)==0 || strcmp( griddir, ".")==0)
	mpp_error("make_quick_mosaic: The input mosaic file location should not be current directory");
    }
  
  }

  sprintf(filepath, "%s/%s", griddir, solo_mosaic);
  strcpy(solo_mosaic_full_path, filepath);
  ntiles = read_mosaic_ntiles(filepath);
  
  if(use_ocean_topog ) nfile_aXl = ntiles;
  /* copy the solo_mosaic file and grid file */
  {
    int fid2, vid2;
    char cmd[STRING], gridfile[STRING];
    size_t start[4], nread[4];
    sprintf(cmd, "cp %s %s", filepath, solo_mosaic);

    system(cmd);
    fid2 = mpp_open(filepath, MPP_READ);
    
    vid2 = mpp_get_varid(fid2, "gridfiles");
    for(i=0; i<4; i++) {
      start[i] = 0; nread[i] = 1;
    }	  
    for(n=0; n<ntiles; n++) {  
      start[0] = n; nread[1] = STRING;
      mpp_get_var_value_block(fid2, vid2, start, nread, gridfile);
      sprintf(cmd, "cp %s/%s %s", griddir, gridfile, gridfile);
      printf("%s \n", cmd);
      system(cmd);
    }
    mpp_close(fid2);
  }

  /* ntiles should be either 1 or ntiles = nfile_aXl */
  if(ntiles != nfile_aXl && ntiles != 1)
    mpp_error("make_quick_mosaic: only support ntiles = 1 or ntiles = nfile_aXl, contact developer");

  nx = (int *)malloc(ntiles*sizeof(int));
  ny = (int *)malloc(ntiles*sizeof(int));
  read_mosaic_grid_sizes(filepath, nx, ny);
  lonb = (double **)malloc(ntiles*sizeof(double *));
  latb = (double **)malloc(ntiles*sizeof(double *));
  for(n=0; n<ntiles; n++) {
     lonb[n] = (double *)malloc((nx[n]+1)*(ny[n]+1)*sizeof(double));
     latb[n] = (double *)malloc((nx[n]+1)*(ny[n]+1)*sizeof(double));     
     read_mosaic_grid_data(filepath, "x", nx[n], ny[n], lonb[n], n, 0, 0); 
     read_mosaic_grid_data(filepath, "y", nx[n], ny[n], latb[n], n, 0, 0);
     for(i=0; i<(nx[n]+1)*(ny[n]+1); i++) {
       lonb[n][i] *= (M_PI/180.0);
       latb[n][i] *= (M_PI/180.0);
     }
  }


  /* get grid cell area */
  cell_area = (double **)malloc(ntiles*sizeof(double *));
  land_area = (double **)malloc(ntiles*sizeof(double *));
  ocean_area = (double **)malloc(ntiles*sizeof(double *));
  for(n=0; n<ntiles; n++) {
    land_area[n] = (double *)malloc(nx[n]*ny[n]*sizeof(double));
    ocean_area[n] = (double *)malloc(nx[n]*ny[n]*sizeof(double));
    cell_area[n] = (double *)malloc(nx[n]*ny[n]*sizeof(double));
    get_grid_area(&nx[n], &ny[n], lonb[n], latb[n], cell_area[n]);
  }

  /* get the ocean and land area. */
  if( use_ocean_topog ) {
    int t_fid, t_vid, ntiles2, nlon, nlat;
    /* first read ocean topography */
    t_fid = mpp_open(ocean_topog, MPP_READ);
    ntiles2 = mpp_get_dimlen(t_fid, "ntiles");
    if(ntiles2 != ntiles) mpp_error("make_quick_mosaic: dimlen ntiles in mosaic file is not the same as dimlen in topog file");
    for(n=0; n<ntiles; n++) {
      char name[128];
      char depth_name[128], mask_name[128];
      int i, j;
      double *depth, *omask;
      int mask_name_exist;
      
      if(ntiles == 1)
	strcpy(name, "nx");
      else
	sprintf(name, "nx_tile%d", n+1);
      nlon = mpp_get_dimlen(t_fid, name);
      if(ntiles == 1)
	strcpy(name, "ny");
      else
	sprintf(name, "ny_tile%d", n+1);
      nlat = mpp_get_dimlen(t_fid, name);
      if( nlon != nx[n] || nlat != ny[n]) mpp_error("make_quick_mosaic: grid size mismatch between mosaic file and topog file");
      if(ntiles == 1) {
	strcpy(depth_name, "depth");
	strcpy(mask_name, "area_frac");
      }
      else {
	sprintf(depth_name, "depth_tile%d", n+1);
        sprintf(mask_name, "area_frac_tile%d", n+1);
      }      
      omask = (double *)malloc(nx[n]*ny[n]*sizeof(double));
      for(i=0; i<nx[n]*ny[n]; i++) omask[i] = 0;
      mask_name_exist = mpp_var_exist(t_fid, mask_name);

      if(mask_name_exist) {
	if(mpp_pe() == mpp_root_pe() ) printf("\nNOTE from make_quick_mosaic: the ocean land/sea mask will be "
					     "determined by field area_frac from file %s\n", ocean_topog);
	t_vid = mpp_get_varid(t_fid, mask_name);
	mpp_get_var_value(t_fid, t_vid, omask);
      }
      else {
	if(mpp_pe() == mpp_root_pe()) printf("\nNOTE from make_coupler_mosaic: the ocean land/sea mask will be "
					     "determined by field depth from file %s\n", ocean_topog);
	t_vid = mpp_get_varid(t_fid, depth_name);
	depth    = (double *)malloc(nx[n]*ny[n]*sizeof(double));
        mpp_get_var_value(t_fid, t_vid, depth);
	for(i=0; i<nx[n]*ny[n]; i++) {
	  if(depth[i] >sea_level) omask[i] = 1;
	}
	free(depth);
      }
      /* Now calculate the ocean and land grid cell area. */
      for(i=0; i<nx[n]*ny[n]; i++) {
	if(omask[i] == 1) {
	  land_area[n][i] = 0;
	  ocean_area[n][i] = cell_area[n][i];
	}
	else {
	  ocean_area[n][i] = 0;
	  land_area[n][i] = cell_area[n][i];
	}
      }
      free(omask);
    }
    mpp_close(t_fid);
  }            
  else {
  
    /* read the exchange grid information and get the land/sea mask of land model*/
    for(n=0; n<ntiles; n++) {
      for(i=0; i<nx[n]*ny[n]; i++) land_area[n][i] = 0;
    }

    vid = mpp_get_varid(fid, "aXl_file");
    for(n=0; n<nfile_aXl; n++) {
      size_t start[4], nread[4];
      int nxgrid;
      char aXl_file[STRING];
      start[0] = n;
      start[1] = 0;
      nread[0] = 1;
      nread[1] = STRING;
      mpp_get_var_value_block(fid, vid, start, nread, aXl_file);
      sprintf(filepath, "%s/%s", griddir, aXl_file);
      nxgrid = read_mosaic_xgrid_size(filepath);
      if(nxgrid>0) {
	int l;
	int *i1, *j1, *i2, *j2;
	double *area;

	i1 = (int *)malloc(nxgrid*sizeof(int));
	j1 = (int *)malloc(nxgrid*sizeof(int));
	i2 = (int *)malloc(nxgrid*sizeof(int));
	j2 = (int *)malloc(nxgrid*sizeof(int));
	area = (double *)malloc(nxgrid*sizeof(double));
	read_mosaic_xgrid_order1(filepath, i1, j1, i2, j2, area);
	if(ntiles == 1) {
	  for(l=0; l<nxgrid; l++) land_area[0][j2[l]*nx[0]+i2[l]] += (area[l]*4*M_PI*RADIUS*RADIUS);
	}
	else {
	  for(l=0; l<nxgrid; l++) land_area[n][j2[l]*nx[n]+i2[l]] += (area[l]*4*M_PI*RADIUS*RADIUS);
	}
	free(i1);
	free(j1);
	free(i2);
	free(j2);
	free(area);
      }
    }

    mpp_close(fid);
  
    /* calculate ocean area */
    for(n=0; n<ntiles; n++) {
      for(i=0; i<nx[n]*ny[n]; i++) {
	ocean_area[n][i] = cell_area[n][i];
if(i==18504) {
printf("%15.10f, %15.10f, %15.10f\n", ocean_area[n][i], land_area[n][i]+AREA_RATIO_THRESH2*ocean_area[n][i],
    land_area[n][i]-AREA_RATIO_THRESH*ocean_area[n][i]);
}
        if(ocean_area[n][i] < land_area[n][i]+AREA_RATIO_THRESH*ocean_area[n][i] &&
           ocean_area[n][i] > land_area[n][i]-AREA_RATIO_THRESH2*ocean_area[n][i])
	  ocean_area[n][i] = 0;
	else 
	  ocean_area[n][i] -= land_area[n][i];
	if(ocean_area[n][i] < 0) {
	  printf("at i = %d, ocean_area = %g, land_area = %g, cell_area=%g\n", i, ocean_area[n][i], land_area[n][i], cell_area[n][i]);
	  mpp_error("make_quick_mosaic: ocean area is negative at some points");
	}
      }
    }
  }
  /* write out land mask */
  {
    for(n=0; n<ntiles; n++) {
      int fid, id_mask, dims[2];
      char lnd_mask_file[STRING];
      double *mask;
      mask = (double *)malloc(nx[n]*ny[n]*sizeof(double));
      for(i=0; i<nx[n]*ny[n]; i++) mask[i] = land_area[n][i]/cell_area[n][i];
      
      if(ntiles > 1)
	sprintf(lnd_mask_file, "land_mask_tile%d.nc", n+1);
      else
	strcpy(lnd_mask_file, "land_mask.nc");
      fid = mpp_open(lnd_mask_file, MPP_WRITE);
      mpp_def_global_att(fid, "grid_version", grid_version);
      mpp_def_global_att(fid, "code_version", tagname);
      mpp_def_global_att(fid, "history", history);
      dims[1] = mpp_def_dim(fid, "nx", nx[n]); 
      dims[0] = mpp_def_dim(fid, "ny", ny[n]);
      id_mask = mpp_def_var(fid, "mask", MPP_DOUBLE, 2, dims,  2, "standard_name",
			    "land fraction at T-cell centers", "units", "none");
      mpp_end_def(fid);
      mpp_put_var_value(fid, id_mask, mask);
      free(mask);
      mpp_close(fid);
    }
  }
    
  /* write out ocean mask */
  {
    for(n=0; n<ntiles; n++) {
      int fid, id_mask, dims[2];
      char ocn_mask_file[STRING];
      double *mask;
      mask = (double *)malloc(nx[n]*ny[n]*sizeof(double));
      for(i=0; i<nx[n]*ny[n]; i++) mask[i] = ocean_area[n][i]/cell_area[n][i];
      
      if(ntiles > 1)
	sprintf(ocn_mask_file, "ocean_mask_tile%d.nc", n+1);
      else
	strcpy(ocn_mask_file, "ocean_mask.nc");
      fid = mpp_open(ocn_mask_file, MPP_WRITE);
      mpp_def_global_att(fid, "grid_version", grid_version);
      mpp_def_global_att(fid, "code_version", tagname);
      mpp_def_global_att(fid, "history", history);
      dims[1] = mpp_def_dim(fid, "nx", nx[n]); 
      dims[0] = mpp_def_dim(fid, "ny", ny[n]);
      id_mask = mpp_def_var(fid, "mask", MPP_DOUBLE, 2, dims,  2, "standard_name",
			    "ocean fraction at T-cell centers", "units", "none");
      mpp_end_def(fid);
      mpp_put_var_value(fid, id_mask, mask);
      free(mask);
      mpp_close(fid);
    }
  }
  
  ocn_topog_file = (char **)malloc(ntiles*sizeof(char *));
  axl_file = (char **)malloc(ntiles*sizeof(char *));
  axo_file = (char **)malloc(ntiles*sizeof(char *));
  lxo_file = (char **)malloc(ntiles*sizeof(char *));
  tilename = (char **)malloc(ntiles*sizeof(char *));
  fid_solo_mosaic = mpp_open(solo_mosaic_full_path, MPP_READ);
  tid_gridtile = mpp_get_varid(fid_solo_mosaic, "gridtiles");

  for(n=0; n<ntiles; n++) {
    size_t start[4], nread[4];
    
    axl_file[n] = (char *)malloc(STRING*sizeof(char));
    axo_file[n] = (char *)malloc(STRING*sizeof(char));
    lxo_file[n] = (char *)malloc(STRING*sizeof(char));
    tilename[n] = (char *)malloc(STRING*sizeof(char));
    ocn_topog_file[n] = (char *)malloc(STRING*sizeof(char));
    for(i=0; i<4; i++) {
      start[i] = 0; nread[i] = 1;
    }	  

    start[0] = n; start[1] = 0; nread[0] = 1; nread[1] = STRING;
    mpp_get_var_value_block(fid_solo_mosaic, tid_gridtile, start, nread, tilename[n]);
    if(use_ocean_topog) 
      get_file_name(ocean_topog, ocn_topog_file[n]);
    else
      sprintf(ocn_topog_file[n], "ocean_topog_%s.nc", tilename[n]);

    sprintf(axl_file[n], "%s_%sX%s_%s.nc", amosaic_name, tilename[n], lmosaic_name, tilename[n]);
    sprintf(axo_file[n], "%s_%sX%s_%s.nc", amosaic_name, tilename[n], omosaic_name, tilename[n]);
    sprintf(lxo_file[n], "%s_%sX%s_%s.nc", lmosaic_name, tilename[n], omosaic_name, tilename[n]);
    
  }

  mpp_close(fid_solo_mosaic);

  for(n=0; n<ntiles; n++) {
    int *i1, *j1, *i2, *j2;
    double *area, *di, *dj;
    int nxgrid, i, j;
    int fid, dim_string, dim_ncells, dim_two, dims[2];
    int id_contact, id_tile1_cell, id_tile2_cell;
    int id_xgrid_area, id_tile1_dist, id_tile2_dist;
    size_t start[4], nwrite[4];
    char contact[STRING];
    
    for(i=0; i<4; i++) {
      start[i] = 0; nwrite[i] = 1;
    } 

    /* first calculate the atmXlnd exchange grid */
    i1 = (int *)malloc(nx[n]*ny[n]*sizeof(int));
    j1 = (int *)malloc(nx[n]*ny[n]*sizeof(int));
    i2 = (int *)malloc(nx[n]*ny[n]*sizeof(int));
    j2 = (int *)malloc(nx[n]*ny[n]*sizeof(int));
    area = (double *)malloc(nx[n]*ny[n]*sizeof(double));
    di   = (double *)malloc(nx[n]*ny[n]*sizeof(double));
    dj   = (double *)malloc(nx[n]*ny[n]*sizeof(double));

    /* write out the atmosXland exchange grid file, The file name will be atmos_mosaic_tile#Xland_mosaic_tile#.nc */   
    nxgrid = 0;
    for(j=0; j<ny[n]; j++) for(i=0; i<nx[n]; i++) {
      if(land_area[n][j*nx[n]+i] >0) {
	i1[nxgrid] = i+1;
	j1[nxgrid] = j+1;
	i2[nxgrid] = i+1;
	j2[nxgrid] = j+1;
	area[nxgrid] = land_area[n][j*nx[n]+i];
	di[nxgrid] = 0;
	dj[nxgrid] = 0;
	nxgrid++;
      }
    }
 
    fid = mpp_open(axl_file[n], MPP_WRITE);
    sprintf(contact, "atmos_mosaic:%s::land_mosaic:%s", tilename[n], tilename[n]);
    mpp_def_global_att(fid, "grid_version", grid_version);
    mpp_def_global_att(fid, "code_version", tagname);
    mpp_def_global_att(fid, "history", history);
    dim_string = mpp_def_dim(fid, "string", STRING);
    dim_ncells = mpp_def_dim(fid, "ncells", nxgrid);
    dim_two    = mpp_def_dim(fid, "two", 2);
    id_contact = mpp_def_var(fid, "contact", MPP_CHAR, 1, &dim_string, 7, "standard_name", "grid_contact_spec",
			     "contact_type", "exchange", "parent1_cell",
			     "tile1_cell", "parent2_cell", "tile2_cell", "xgrid_area_field", "xgrid_area", 
			     "distant_to_parent1_centroid", "tile1_distance", "distant_to_parent2_centroid", "tile2_distance");
	    
    dims[0] = dim_ncells; dims[1] = dim_two;
    id_tile1_cell = mpp_def_var(fid, "tile1_cell", MPP_INT, 2, dims, 1, "standard_name", "parent_cell_indices_in_mosaic1");
    id_tile2_cell = mpp_def_var(fid, "tile2_cell", MPP_INT, 2, dims, 1, "standard_name", "parent_cell_indices_in_mosaic2");
    id_xgrid_area = mpp_def_var(fid, "xgrid_area", MPP_DOUBLE, 1, &dim_ncells, 2, "standard_name",
				"exchange_grid_area", "units", "m2");
    id_tile1_dist = mpp_def_var(fid, "tile1_distance", MPP_DOUBLE, 2, dims, 1, "standard_name", "distance_from_parent1_cell_centroid");
    id_tile2_dist = mpp_def_var(fid, "tile2_distance", MPP_DOUBLE, 2, dims, 1, "standard_name", "distance_from_parent2_cell_centroid");
    mpp_end_def(fid);
    nwrite[0] = strlen(contact);
    mpp_put_var_value_block(fid, id_contact, start, nwrite, contact);
    nwrite[0] = nxgrid;
    mpp_put_var_value(fid, id_xgrid_area, area);
    mpp_put_var_value_block(fid, id_tile1_cell, start, nwrite, i1);
    mpp_put_var_value_block(fid, id_tile2_cell, start, nwrite, i2);
    mpp_put_var_value_block(fid, id_tile1_dist, start, nwrite, di);
    mpp_put_var_value_block(fid, id_tile2_dist, start, nwrite, di);    
    start[1] = 1;
    mpp_put_var_value_block(fid, id_tile1_cell, start, nwrite, j1);
    mpp_put_var_value_block(fid, id_tile2_cell, start, nwrite, j2);
    mpp_put_var_value_block(fid, id_tile1_dist, start, nwrite, dj);
    mpp_put_var_value_block(fid, id_tile2_dist, start, nwrite, dj);   
    mpp_close(fid);
    
    /* write out the atmosXocean exchange grid file, The file name will be atmos_mosaic_tile#Xocean_mosaic_tile#.nc */
    nxgrid = 0;
    for(j=0; j<ny[n]; j++) for(i=0; i<nx[n]; i++) {
      if(ocean_area[n][j*nx[n]+i] >0) {
	i1[nxgrid] = i+1;
	j1[nxgrid] = j+1;
	i2[nxgrid] = i+1;
	j2[nxgrid] = j+1;
	area[nxgrid] = ocean_area[n][j*nx[n]+i];
	di[nxgrid] = 0;
	dj[nxgrid] = 0;
	nxgrid++;
      }
    }    
    fid = mpp_open(axo_file[n], MPP_WRITE);
    
    sprintf(contact, "atmos_mosaic:%s::ocean_mosaic:%s", tilename[n], tilename[n]);
    mpp_def_global_att(fid, "grid_version", grid_version);
    mpp_def_global_att(fid, "code_version", tagname);
    mpp_def_global_att(fid, "history", history);
    dim_string = mpp_def_dim(fid, "string", STRING);
    dim_ncells = mpp_def_dim(fid, "ncells", nxgrid);
    dim_two    = mpp_def_dim(fid, "two", 2);
    id_contact = mpp_def_var(fid, "contact", MPP_CHAR, 1, &dim_string, 7, "standard_name", "grid_contact_spec",
			     "contact_type", "exchange", "parent1_cell",
			     "tile1_cell", "parent2_cell", "tile2_cell", "xgrid_area_field", "xgrid_area", 
			     "distant_to_parent1_centroid", "tile1_distance", "distant_to_parent2_centroid", "tile2_distance");
	    
    dims[0] = dim_ncells; dims[1] = dim_two;
    id_tile1_cell = mpp_def_var(fid, "tile1_cell", MPP_INT, 2, dims, 1, "standard_name", "parent_cell_indices_in_mosaic1");
    id_tile2_cell = mpp_def_var(fid, "tile2_cell", MPP_INT, 2, dims, 1, "standard_name", "parent_cell_indices_in_mosaic2");
    id_xgrid_area = mpp_def_var(fid, "xgrid_area", MPP_DOUBLE, 1, &dim_ncells, 2, "standard_name",
				"exchange_grid_area", "units", "m2");
    id_tile1_dist = mpp_def_var(fid, "tile1_distance", MPP_DOUBLE, 2, dims, 1, "standard_name", "distance_from_parent1_cell_centroid");
    id_tile2_dist = mpp_def_var(fid, "tile2_distance", MPP_DOUBLE, 2, dims, 1, "standard_name", "distance_from_parent2_cell_centroid");
    mpp_end_def(fid);
    start[1] = 0;
    nwrite[0] = strlen(contact);
    mpp_put_var_value_block(fid, id_contact, start, nwrite, contact);
    nwrite[0] = nxgrid;
    mpp_put_var_value(fid, id_xgrid_area, area);
    mpp_put_var_value_block(fid, id_tile1_cell, start, nwrite, i1);
    mpp_put_var_value_block(fid, id_tile2_cell, start, nwrite, i2);
    mpp_put_var_value_block(fid, id_tile1_dist, start, nwrite, di);
    mpp_put_var_value_block(fid, id_tile2_dist, start, nwrite, di);    
    start[1] = 1;
    mpp_put_var_value_block(fid, id_tile1_cell, start, nwrite, j1);
    mpp_put_var_value_block(fid, id_tile2_cell, start, nwrite, j2);
    mpp_put_var_value_block(fid, id_tile1_dist, start, nwrite, dj);
    mpp_put_var_value_block(fid, id_tile2_dist, start, nwrite, dj);   
    mpp_close(fid);
    
    /* write out landXocean exchange grid information */
    fid = mpp_open(lxo_file[n], MPP_WRITE);
    sprintf(contact, "land_mosaic:%s::ocean_mosaic:%s", tilename[n], tilename[n]);
    mpp_def_global_att(fid, "grid_version", grid_version);
    mpp_def_global_att(fid, "code_version", tagname);
    mpp_def_global_att(fid, "history", history);
    dim_string = mpp_def_dim(fid, "string", STRING);
    dim_ncells = mpp_def_dim(fid, "ncells", nxgrid);
    dim_two    = mpp_def_dim(fid, "two", 2);
    id_contact = mpp_def_var(fid, "contact", MPP_CHAR, 1, &dim_string, 7, "standard_name", "grid_contact_spec",
			     "contact_type", "exchange", "parent1_cell",
			     "tile1_cell", "parent2_cell", "tile2_cell", "xgrid_area_field", "xgrid_area", 
			     "distant_to_parent1_centroid", "tile1_distance", "distant_to_parent2_centroid", "tile2_distance");
	    
    dims[0] = dim_ncells; dims[1] = dim_two;
    id_tile1_cell = mpp_def_var(fid, "tile1_cell", MPP_INT, 2, dims, 1, "standard_name", "parent_cell_indices_in_mosaic1");
    id_tile2_cell = mpp_def_var(fid, "tile2_cell", MPP_INT, 2, dims, 1, "standard_name", "parent_cell_indices_in_mosaic2");
    id_xgrid_area = mpp_def_var(fid, "xgrid_area", MPP_DOUBLE, 1, &dim_ncells, 2, "standard_name",
				"exchange_grid_area", "units", "m2");
    id_tile1_dist = mpp_def_var(fid, "tile1_distance", MPP_DOUBLE, 2, dims, 1, "standard_name", "distance_from_parent1_cell_centroid");
    id_tile2_dist = mpp_def_var(fid, "tile2_distance", MPP_DOUBLE, 2, dims, 1, "standard_name", "distance_from_parent2_cell_centroid");
    mpp_end_def(fid);
    start[1] = 0;
    nwrite[0] = strlen(contact);
    mpp_put_var_value_block(fid, id_contact, start, nwrite, contact);
    nwrite[0] = nxgrid;
    mpp_put_var_value(fid, id_xgrid_area, area);
    mpp_put_var_value_block(fid, id_tile1_cell, start, nwrite, i1);
    mpp_put_var_value_block(fid, id_tile2_cell, start, nwrite, i2);
    mpp_put_var_value_block(fid, id_tile1_dist, start, nwrite, di);
    mpp_put_var_value_block(fid, id_tile2_dist, start, nwrite, di);    
    start[1] = 1;
    mpp_put_var_value_block(fid, id_tile1_cell, start, nwrite, j1);
    mpp_put_var_value_block(fid, id_tile2_cell, start, nwrite, j2);
    mpp_put_var_value_block(fid, id_tile1_dist, start, nwrite, dj);
    mpp_put_var_value_block(fid, id_tile2_dist, start, nwrite, dj);   
    mpp_close(fid);
    
    free(i1);
    free(j1);
    free(i2);
    free(j2);
    free(area);
    free(di);
    free(dj);
  }

  
  /*Fianlly create the coupler mosaic file mosaic_name.nc */
  {
    int dim_string, dim_axo, dim_axl, dim_lxo, dims[2];
    int id_amosaic, id_lmosaic, id_omosaic;
    int id_amosaic_file, id_lmosaic_file, id_omosaic_file, id_otopog_file;
    int id_amosaic_dir, id_lmosaic_dir, id_omosaic_dir, id_otopog_dir;
    int id_axo_file, id_axl_file, id_lxo_file;
    size_t start[4], nwrite[4];
    
    for(i=0; i<4; i++) {
      start[i] = 0; nwrite[i] = 1;
    }	      
    printf("mosaic_file is %s\n", mosaic_file);   
    fid = mpp_open(mosaic_file, MPP_WRITE);
    mpp_def_global_att(fid, "grid_version", grid_version);
    mpp_def_global_att(fid, "code_version", tagname);
    mpp_def_global_att(fid, "history", history);
    dim_string = mpp_def_dim(fid, "string", STRING);
    dim_axo = mpp_def_dim(fid, "nfile_aXo", ntiles);
    dim_axl = mpp_def_dim(fid, "nfile_aXl", ntiles);
    dim_lxo = mpp_def_dim(fid, "nfile_lXo", ntiles);

    id_amosaic_dir  = mpp_def_var(fid, "atm_mosaic_dir", MPP_CHAR, 1, &dim_string,
                                  1, "standard_name", "directory_storing_atmosphere_mosaic");
    id_amosaic_file = mpp_def_var(fid, "atm_mosaic_file", MPP_CHAR, 1, &dim_string,
                                  1, "standard_name", "atmosphere_mosaic_file_name");
    id_amosaic      = mpp_def_var(fid, "atm_mosaic", MPP_CHAR, 1, &dim_string,
                                  1, "standard_name", "atmosphere_mosaic_name");
    id_lmosaic_dir  = mpp_def_var(fid, "lnd_mosaic_dir", MPP_CHAR, 1, &dim_string,
                                  1, "standard_name", "directory_storing_land_mosaic");
    id_lmosaic_file = mpp_def_var(fid, "lnd_mosaic_file", MPP_CHAR, 1, &dim_string,
                                  1, "standard_name", "land_mosaic_file_name");
    id_lmosaic      = mpp_def_var(fid, "lnd_mosaic", MPP_CHAR, 1, &dim_string,
                                  1, "standard_name", "land_mosaic_name");
    id_omosaic_dir  = mpp_def_var(fid, "ocn_mosaic_dir", MPP_CHAR, 1, &dim_string,
                                  1, "standard_name", "directory_storing_ocean_mosaic");
    id_omosaic_file = mpp_def_var(fid, "ocn_mosaic_file", MPP_CHAR, 1, &dim_string,
                                  1, "standard_name", "ocean_mosaic_file_name");
    id_omosaic      = mpp_def_var(fid, "ocn_mosaic", MPP_CHAR, 1, &dim_string,
                                  1, "standard_name", "ocean_mosaic_name");
    if(use_ocean_topog) {   
       id_otopog_dir   = mpp_def_var(fid, "ocn_topog_dir", MPP_CHAR, 1, &dim_string,
                                     1, "standard_name", "directory_storing_ocean_topog");
       id_otopog_file  = mpp_def_var(fid, "ocn_topog_file", MPP_CHAR, 1, &dim_string,
               		             1, "standard_name", "ocean_topog_file_name");
    }    
    dims[0] = dim_axo; dims[1] = dim_string;
    id_axo_file = mpp_def_var(fid, "aXo_file", MPP_CHAR, 2, dims, 1, "standard_name", "atmXocn_exchange_grid_file");
    dims[0] = dim_axl; dims[1] = dim_string;
    id_axl_file = mpp_def_var(fid, "aXl_file", MPP_CHAR, 2, dims, 1, "standard_name", "atmXlnd_exchange_grid_file");
    dims[0] = dim_lxo; dims[1] = dim_string;
    id_lxo_file = mpp_def_var(fid, "lXo_file", MPP_CHAR, 2, dims, 1, "standard_name", "lndXocn_exchange_grid_file");
    mpp_end_def(fid);    

    nwrite[0] = strlen(solo_mosaic_dir);
    mpp_put_var_value_block(fid, id_amosaic_dir, start, nwrite, solo_mosaic_dir);
    mpp_put_var_value_block(fid, id_lmosaic_dir, start, nwrite, solo_mosaic_dir);
    mpp_put_var_value_block(fid, id_omosaic_dir, start, nwrite, solo_mosaic_dir);				  
    nwrite[0] = strlen(solo_mosaic);
    mpp_put_var_value_block(fid, id_lmosaic_file, start, nwrite, solo_mosaic);
    mpp_put_var_value_block(fid, id_amosaic_file, start, nwrite, solo_mosaic);
    mpp_put_var_value_block(fid, id_omosaic_file, start, nwrite, solo_mosaic);
    nwrite[0] = strlen(amosaic_name);
    mpp_put_var_value_block(fid, id_amosaic, start, nwrite, amosaic_name);
    nwrite[0] = strlen(lmosaic_name);
    mpp_put_var_value_block(fid, id_lmosaic, start, nwrite, lmosaic_name);
    nwrite[0] = strlen(omosaic_name);
    mpp_put_var_value_block(fid, id_omosaic, start, nwrite, omosaic_name);

    for(n=0; n<ntiles; n++) {
      start[0] = n; nwrite[0] =1;
      start[1] = 0; nwrite[1] =1;
      if(use_ocean_topog) {
         nwrite[0] = strlen(ocn_topog_file[n]);
         mpp_put_var_value_block(fid, id_otopog_file, start, nwrite, ocn_topog_file[n]);
         nwrite[0] = strlen(ocn_topog_dir);
         mpp_put_var_value_block(fid, id_otopog_dir, start, nwrite, ocn_topog_dir);
      }
      start[0] = n; nwrite[0] =1;
      nwrite[1] = strlen(axl_file[n]);
      mpp_put_var_value_block(fid, id_axl_file, start, nwrite, axl_file[n]);
      nwrite[1] = strlen(axo_file[n]);
      mpp_put_var_value_block(fid, id_axo_file, start, nwrite, axo_file[n]);
      nwrite[1] = strlen(lxo_file[n]);
      mpp_put_var_value_block(fid, id_lxo_file, start, nwrite, lxo_file[n]);
    }
    mpp_close(fid);
  }
    
  for(n=0; n<ntiles; n++) {
    free(axl_file[n]);
    free(axo_file[n]);
    free(lxo_file[n]);
  }
  free(axl_file);
  free(axo_file);
  free(lxo_file);
  printf("\n***** Congratulation! You have successfully run make_quick_mosaic\n");
  mpp_end();

  return 0;

} /* main */  
