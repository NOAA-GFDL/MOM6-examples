"""
A collection of useful functions...
"""
import numpy as np
import tarfile
from scipy.io import netcdf

def section2quadmesh(x, z, q, representation='pcm'):
  """
  Creates the appropriate quadmesh coordinates to plot a scalar q(1:nk,1:ni) at
  horizontal positions x(1:ni+1) and between interfaces at z(nk+1,ni), using
  various representations of the topography.

  Returns X(2*ni+1), Z(nk+1,2*ni+1) and Q(nk,2*ni) to be passed to pcolormesh.

  TBD: Optionally, x can be dimensioned as x(ni) in which case it will be extraplated as if it had 
  had dimensions x(ni+1).
  
  Optional argument:
  
  representation='pcm' (default) yields a step-wise visualization, appropriate for
           z-coordinate models.
  representation='plm' yields a piecewise-linear visualization more representative
           of general-coordinate (and isopycnal) models.
  representation='linear' is the aesthetically most pleasing but does not
           represent the data conservatively.

  """

  if x.ndim!=1: raise Exception('The x argument must be a vector')
  if z.ndim!=2: raise Exception('The z argument should be a 2D array')
  if q.ndim!=2: raise Exception('The z argument should be a 2D array')
  qnk, qni = q.shape
  znk, zni = z.shape
  xni = x.size
  if zni!=qni: raise Exception('The last dimension of z and q must be equal in length')
  if znk!=qnk+1: raise Exception('The first dimension of z must be 1 longer than that of q. q has %i levels'%qnk)
  if xni!=qni+1: raise Exception('The length of x must 1 longer than the last dimension of q')

  if type( z ) == np.ma.core.MaskedArray: z[z.mask] = 0
  if type( q ) == np.ma.core.MaskedArray: qmin = np.amin(q); q[q.mask] = qmin

  periodicDomain =  abs((x[-1]-x[0])-360. ) < 1e-6 # Detect if horizontal axis is a periodic domain

  if representation=='pcm':
    X = np.zeros((2*qni))
    X[::2] = x[:-1]
    X[1::2] = x[1:]
    Z = np.zeros((qnk+1,2*qni))
    Z[:,::2] = z
    Z[:,1::2] = z
    Q = np.zeros((qnk,2*qni-1))
    Q[:,::2] = q
    Q[:,1::2] = ( q[:,:-1] + q[:,1:] )/2.
  elif representation=='linear':
    X = np.zeros((2*qni+1))
    X[::2] = x
    X[1::2] = ( x[0:-1] + x[1:] )/2.
    Z = np.zeros((qnk+1,2*qni+1))
    Z[:,1::2] = z
    Z[:,2:-1:2] = ( z[:,0:-1] + z[:,1:] )/2.
    Z[:,0] = z[:,0]
    Z[:,-1] = z[:,-1]
    Q = np.zeros((qnk,2*qni))
    Q[:,::2] = q
    Q[:,1::2] = q
  elif representation=='plm':
    X = np.zeros((2*qni))
    X[::2] = x[:-1]
    X[1::2] = x[1:]
    # PLM reconstruction for Z
    dz = np.roll(z,-1,axis=1) - z # Right-sided difference
    if not periodicDomain: dz[:,-1] = 0 # Non-periodic boundary
    d2 = ( np.roll(z,-1,axis=1) - np.roll(z,1,axis=1) )/2. # Centered difference
    d2 = ( dz + np.roll(dz,1,axis=1) )/2. # Centered difference
    s = np.sign( d2 ) # Sign of centered slope
    s[dz * np.roll(dz,1,axis=1) <= 0] = 0 # Flatten extrema
    dz = np.abs(dz) # Only need magnitude from here on
    S = s * np.minimum( np.abs(d2), np.minimum( dz, np.roll(dz,1,axis=1) ) ) # PLM slope
    Z = np.zeros((qnk+1,2*qni))
    Z[:,::2] = z - S/2.
    Z[:,1::2] = z + S/2.
    Q = np.zeros((qnk,2*qni-1))
    Q[:,::2] = q
    Q[:,1::2] = ( q[:,:-1] + q[:,1:] )/2.
  else: raise Exception('Unknown representation!')

  return X, Z, Q

def get_z(rg, depth, var_name):
  """Returns 3d interface positions from netcdf group rg, based on dimension data for variable var_name"""
  if 'e' in rg.variables: # First try native approach
    if len(rg.variables['e'])==3: return rg.variables['e'][:]
    elif len(rg.variables['e'])==4: return rg.variables['e'][0]
  if var_name not in rg.variables: raise Exception('Variable "'+var_name+'" not found in netcdf file')
  if rg.variables[var_name].shape<3: raise Exception('Variable "'+var_name+'" must have 3 or more dimensions')
  vdim = rg.variables[var_name].dimensions[-3]
  if vdim not in rg.variables: raise Exception('Variable "'+vdim+'" should be a [CF] dimension variable but is missing')
  if 'edges' in rg.variables[vdim].ncattrs(): zvar = getattr(rg.variables[vdim],'edges')
  elif 'zw' in rg.variables: zvar = 'zw'
  else: raise Exception('Cannot figure out vertical coordinate from variable "'+var_name+'"')
  if not len(rg.variables[zvar].shape)==1: raise Exception('Variable "'+zvar+'" was expected to be 1d')
  zw = rg.variables[zvar][:]
  Zmod = np.zeros((zw.shape[0], depth.shape[0], depth.shape[1] ))
  for k in range(zw.shape[0]):
    Zmod[k] = -np.minimum( depth, abs(zw[k]) )
  return Zmod

def rho_Wright97(S, T, P=0):
  """
  Returns the density of seawater for the given salinity, potential temperature
  and pressure.

  Units: salinity in PSU, potential temperature in degrees Celsius and pressure in Pascals.
  """
  a0 = 7.057924e-4; a1 = 3.480336e-7; a2 = -1.112733e-7
  b0 = 5.790749e8;  b1 = 3.516535e6;  b2 = -4.002714e4
  b3 = 2.084372e2;  b4 = 5.944068e5;  b5 = -9.643486e3
  c0 = 1.704853e5;  c1 = 7.904722e2;  c2 = -7.984422
  c3 = 5.140652e-2; c4 = -2.302158e2; c5 = -3.079464
  al0 = a0 + a1*T + a2*S
  p0 = b0 + b4*S + T * (b1 + T*(b2 + b3*T) + b5*S)
  Lambda = c0 + c4*S + T * (c1 + T*(c2 + c3*T) + c5*S)
  return (P + p0) / (Lambda + al0*(P + p0))


def ice9(i, j, source, xcyclic=True, tripolar=True):
  """
  An iterative (stack based) implementation of "Ice 9".

  The flood fill starts at [j,i] and treats any positive value of "source" as
  passable. Zero and negative values block flooding.

  xcyclic = True allows cyclic behavior in the last index. (default)
  tripolar = True allows a fold across the top-most edge. (default)

  Returns an array of 0's and 1's.
  """
  wetMask = 0*source
  (nj,ni) = wetMask.shape
  stack = set()
  stack.add( (j,i) )
  while stack:
    (j,i) = stack.pop()
    if wetMask[j,i] or source[j,i] <= 0: continue
    wetMask[j,i] = 1
    if i>0: stack.add( (j,i-1) )
    elif xcyclic: stack.add( (j,ni-1) )
    if i<ni-1: stack.add( (j,i+1) )
    elif xcyclic: stack.add( (j,0) )
    if j>0: stack.add( (j-1,i) )
    if j<nj-1: stack.add( (j+1,i) )
    elif tripolar: stack.add( (j,ni-1-i) ) # Tri-polar fold
  return wetMask

def ice9Wrapper(x, y, depth, xy0):
  ji = nearestJI(x, y, xy0)
  return ice9(ji[1], ji[0], depth)

def maskFromDepth(depth, zCellTop):
  """
  Generates a "wet mask" for a z-coordinate model based on relative location of
  the ocean bottom to the upper interface of the cell.

  depth (2d) is positiveo
  zCellTop (scalar) is a negative position of the upper interface of the cell..
  """
  wet = 0*depth
  wet[depth>-zCellTop] = 1
  return wet

def nearestJI(x, y, xy0):
  """
  Find (j,i) of cell with center nearest to (x0,y0).
  """
  x0,y0 = xy0
  return np.unravel_index( ((x-x0)**2 + (y-y0)**2).argmin() , x.shape)

def readNCFromTar(tar,file,var):
  TF = tarfile.open(tar,'r')
  member = [m for m in TF.getmembers() if file in m.name][0]
  nc = netcdf.netcdf_file(TF.extractfile(member),'r')
  return nc.variables[var]

def southOf(x, y, xy0, xy1):
  """
  Returns 1 for point south/east of the line that passes through xy0-xy1, 0 otherwise.
  """
  x0 = xy0[0]; y0 = xy0[1]; x1 = xy1[0]; y1 = xy1[1]
  dx = x1 - x0; dy = y1 - y0
  Y = (x-x0)*dy - (y-y0)*dx
  Y[Y>=0] = 1; Y[Y<=0] = 0
  return Y

def genBasinMasks(x,y,depth,verbose=False):
  if verbose: print('Generating global wet mask ...')
  wet = ice9Wrapper(x, y, depth, (0,-35)) # All ocean points seeded from South Atlantic
  if verbose: print('done.')

  code = 0*wet

  if verbose: print('Finding Cape of Good Hope ...')
  tmp = 1 - wet; tmp[x<-30] = 0
  tmp = ice9Wrapper(x, y, tmp, (20,-30.))
  yCGH = (tmp*y).min()
  if verbose: print('done.', yCGH)

  if verbose: print('Finding Melbourne ...')
  tmp = 1 - wet; tmp[x>-180] = 0
  tmp = ice9Wrapper(x, y, tmp, (-220,-25.))
  yMel = (tmp*y).min()
  if verbose: print('done.', yMel)

  if verbose: print('Processing Persian Gulf ...')
  tmp = wet*( 1-southOf(x, y, (55.,23.), (56.5,27.)) )
  tmp = ice9Wrapper(x, y, tmp, (53.,25.))
  code[tmp>0] = 11
  wet = wet - tmp # Removed named points

  if verbose: print('Processing Red Sea ...')
  tmp = wet*( 1-southOf(x, y, (40.,11.), (45.,13.)) )
  tmp = ice9Wrapper(x, y, tmp, (40.,18.))
  code[tmp>0] = 10
  wet = wet - tmp # Removed named points

  if verbose: print('Processing Black Sea ...')
  tmp = wet*( 1-southOf(x, y, (26.,42.), (32.,40.)) )
  tmp = ice9Wrapper(x, y, tmp, (32.,43.))
  code[tmp>0] = 7
  wet = wet - tmp # Removed named points

  if verbose: print('Processing Mediterranean ...')
  tmp = wet*( southOf(x, y, (-5.7,35.5), (-5.7,36.5)) )
  tmp = ice9Wrapper(x, y, tmp, (4.,38.))
  code[tmp>0] = 6
  wet = wet - tmp # Removed named points

  if verbose: print('Processing Baltic ...')
  tmp = wet*( southOf(x, y, (8.6,56.), (8.6,60.)) )
  tmp = ice9Wrapper(x, y, tmp, (10.,58.))
  code[tmp>0] = 9
  wet = wet - tmp # Removed named points

  if verbose: print('Processing Hudson Bay ...')
  tmp = wet*( 
             ( 1-(1-southOf(x, y, (-95.,66.), (-83.5,67.5)))
                *(1-southOf(x, y, (-83.5,67.5), (-84.,71.))) 
             )*( 1-southOf(x, y, (-70.,58.), (-70.,65.)) ) )
  tmp = ice9Wrapper(x, y, tmp, (-85.,60.))
  code[tmp>0] = 8
  wet = wet - tmp # Removed named points

  if verbose: print('Processing Arctic ...')
  tmp = wet*( 
            (1-southOf(x, y, (-171.,66.), (-166.,65.5))) * (1-southOf(x, y, (-64.,66.4), (-50.,68.5))) # Lab Sea
       +    southOf(x, y, (-50.,0.), (-50.,90.)) * (1- southOf(x, y, (0.,65.5), (360.,65.5))  ) # Denmark Strait
       +    southOf(x, y, (-18.,0.), (-18.,65.)) * (1- southOf(x, y, (0.,64.9), (360.,64.9))  ) # Iceland-Sweden
       +    southOf(x, y, (20.,0.), (20.,90.)) # Barents Sea
       +    (1-southOf(x, y, (-280.,55.), (-200.,65.)))
            )
  tmp = ice9Wrapper(x, y, tmp, (0.,85.))
  code[tmp>0] = 4
  wet = wet - tmp # Removed named points

  if verbose: print('Processing Pacific ...')
  tmp = wet*( (1-southOf(x, y, (0.,yMel), (360.,yMel)))
             -southOf(x, y, (-257,1), (-257,0))*southOf(x, y, (0,3), (1,3))
             -southOf(x, y, (-254.25,1), (-254.25,0))*southOf(x, y, (0,-5), (1,-5)) 
             -southOf(x, y, (-243.7,1), (-243.7,0))*southOf(x, y, (0,-8.4), (1,-8.4)) 
             -southOf(x, y, (-234.5,1), (-234.5,0))*southOf(x, y, (0,-8.9), (1,-8.9)) 
            )
  tmp = ice9Wrapper(x, y, tmp, (-150.,0.))
  code[tmp>0] = 3
  wet = wet - tmp # Removed named points

  if verbose: print('Processing Atlantic ...')
  tmp = wet*(1-southOf(x, y, (0.,yCGH), (360.,yCGH)))
  tmp = ice9Wrapper(x, y, tmp, (-20.,0.))
  code[tmp>0] = 2
  wet = wet - tmp # Removed named points

  if verbose: print('Processing Indian ...')
  tmp = wet*(1-southOf(x, y, (0.,yCGH), (360.,yCGH)))
  tmp = ice9Wrapper(x, y, tmp, (55.,0.))
  code[tmp>0] = 5
  wet = wet - tmp # Removed named points

  if verbose: print('Processing Southern Ocean ...')
  tmp = ice9Wrapper(x, y, wet, (0.,-55.))
  code[tmp>0] = 1
  wet = wet - tmp # Removed named points

  code[wet>0] = -9
  (j,i) = np.unravel_index( wet.argmax(), x.shape)
  if j:
    if verbose: print('There are leftover points unassigned to a basin code')
    while j:
      print(x[j,i],y[j,i],[j,i])
      wet[j,i]=0
      (j,i) = np.unravel_index( wet.argmax(), x.shape)
  else: 
    if verbose: print('All points assigned a basin code')

  if verbose:
    print("""
Basin codes:
-----------------------------------------------------------
  (1) Southern Ocean      (6) Mediterranean Sea
  (2) Atlantic Ocean      (7) Black Sea
  (3) Pacific Ocean       (8) Hudson Bay
  (4) Arctic Ocean        (9) Baltic Sea
  (5) Indian Ocean       (10) Red Sea

    """)

  return code


# Tests
if __name__ == '__main__':

  import matplotlib.pyplot as plt
  import numpy.matlib

  # Test data
  x=np.arange(5)
  z=np.array([[0,0.2,0.3,-.1],[1,1.5,.7,.4],[2,2,1.5,2],[3,2.3,1.5,2.1]])*-1
  q=np.matlib.rand(3,4)
  print('x=',x)
  print('z=',z)
  print('q=',q)

  X, Z, Q = section2quadmesh(x, z, q)
  print('X=',X)
  print('Z=',Z)
  print('Q=',Q)
  plt.subplot(3,1,1)
  plt.pcolormesh(X, Z, Q)

  X, Z, Q = section2quadmesh(x, z, q, representation='linear')
  print('X=',X)
  print('Z=',Z)
  print('Q=',Q)
  plt.subplot(3,1,2)
  plt.pcolormesh(X, Z, Q)

  X, Z, Q = section2quadmesh(x, z, q, representation='plm')
  print('X=',X)
  print('Z=',Z)
  print('Q=',Q)
  plt.subplot(3,1,3)
  plt.pcolormesh(X, Z, Q)

  plt.show()

