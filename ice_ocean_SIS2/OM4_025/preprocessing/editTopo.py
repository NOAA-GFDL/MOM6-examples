#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


def error(msg, code=9):
    print('Error: ' + msg)
    exit(code)


try:
    import argparse
except:
    error('This version of python is not new enough. python 2.7 or newer is required.')
try:
    from netCDF4 import Dataset
except:
    error('Unable to import netCDF4 module. Check your PYTHONPATH.\n'
          + 'Perhaps try:\n   module load python_netcdf4')
try:
    import numpy as np
except:
    error('Unable to import numpy module. Check your PYTHONPATH.\n'
          + 'Perhaps try:\n   module load python_numpy')
try:
    import matplotlib.pyplot as plt
except:
    error('Unable to import matplotlib.pyplot module. Check your PYTHONPATH.\n'
          + 'Perhaps try:\n   module load python_matplotlib')
from matplotlib.widgets import Button, RadioButtons, TextBox, CheckButtons
from matplotlib.colors import LinearSegmentedColormap
import shutil as sh
from os.path import dirname, basename, join, splitext
import time
import sys
import os
import pwd


def main():

    # Command line arguments
    parser = argparse.ArgumentParser(description='''Point-wise editing of topography.
            Ignore all the controls in the toolbar at the top of the window.
            Zoom in and out with the scroll wheel.
            Pan the view with the North, South, East and West buttons.
            Use +, -, Flip buttons to modify the colormap.
            Set the prescribed depth with the textbox at the bottom.
            Left click on a cell to apply the prescribed depth value.
            Right click on a cell to reset to the original value.
            Double left click to assign the highest of the 4 nearest points with depth<0.
            Close the window to write the edits to the output file.
        ''',
                        epilog='Written by Alistair Adcroft (2013) and Andrew Kiss (2020)')
    parser.add_argument('filename', type=str,
                        help='Netcdf input file to read.')
    parser.add_argument('variable', type=str,
                        nargs='?', default='depth',
                        help='Name of variable to edit. Defaults to "depth".')
    parser.add_argument('--output', type=str, metavar='outfile',
                        nargs=1, default=None,
                        help='Write an output file. If no output file is specified, creates the file with the "edit_" prepended to the name  of the input file.')
    parser.add_argument('--ref', type=str, metavar='reffile',
                        nargs=1, default=[None],
                        help='Netcdf reference input file to use for copying points from. Must have the same dimensions and variable name as filename.')
    parser.add_argument('--apply', type=str, metavar='editfile',
                        nargs=1, default=[None],
                        help='Apply edits from specified .nc file or whitespace-delimited .txt file (in which first row specifies version number (must be 1), data rows contain i, j, old, new (i, j count from 0; old is ignored), and anything following # is ignored).')
    parser.add_argument('--nogui',
                        action='store_true', default=False,
                        help="Don't open GUI. Best used with --apply, in which case editfile is applied to filename and saved as outfile, then progam exits.")

    optCmdLineArgs = parser.parse_args()

    createGUI(optCmdLineArgs.filename, optCmdLineArgs.variable,
              optCmdLineArgs.output[0], optCmdLineArgs.ref[0],
              optCmdLineArgs.apply[0], optCmdLineArgs.nogui)


def createGUI(fileName, variable, outFile, refFile, applyFile, nogui):

    # Open netcdf files
    try:
        rg = Dataset(fileName, 'r')
    except:
        error('There was a problem opening input netcdf file "'+fileName+'".')

    rgVar = rg.variables[variable]  # handle to the variable
    dims = rgVar.dimensions  # tuple of dimensions
    depth = rgVar[:]  # Read the data
    #depth = depth[0:600,0:600]
    (nj, ni) = depth.shape
    print('Range of input depths: min=', np.amin(depth), 'max=', np.amax(depth))

    ref = None
    if refFile:
        try:
            ref = Dataset(refFile, 'r').variables[variable][:]
        except:
            error('There was a problem opening reference netcdf file "'+refFile+'".')

    try:
        sg = Dataset('supergrid.nc', 'r')
        lon = sg.variables['x'][:]
        lon = lon[0:2*nj+1:2, 0:2*ni+1:2]
        lat = sg.variables['y'][:]
        lat = lat[0:2*nj+1:2, 0:2*ni+1:2]
    except:
        lon, lat = np.meshgrid(np.arange(ni+1), np.arange(nj+1))
    fullData = Topography(lon, lat, depth, ref)

    class Container:
        def __init__(self):
            self.view = None
            self.edits = None
            self.data = None
            self.quadMesh = None
            self.cbar = None
            self.ax = None
            self.syms = None
            self.useref = False
            self.textbox = None
            cdict = {'red': ((0.0, 0.0, 0.0), (0.5, 0.7, 0.0), (1.0, 0.9, 0.0)),
                     'green': ((0.0, 0.0, 0.0), (0.5, 0.7, 0.2), (1.0, 1.0, 0.0)),
                     'blue': ((0.0, 0.0, 0.2), (0.5, 1.0, 0.0), (1.0, 0.9, 0.0))}
            cdict_r = {'red': ((0.0, 0.0, 0.0), (0.497, 0.7, 0.0), (1.0, 0.9, 0.0)),
                     'green': ((0.0, 0.0, 0.0), (0.497, 0.7, 0.2), (1.0, 1.0, 0.0)),
                     'blue': ((0.0, 0.0, 0.2), (0.497, 1.0, 0.0), (1.0, 0.9, 0.0))}
            self.cmap1 = LinearSegmentedColormap('my_colormap', cdict, 256)
            self.cmap2 = LinearSegmentedColormap('my_colormap', cdict_r, 256).reversed()
            self.cmap3 = plt.get_cmap('seismic')
            self.cmap = self.cmap1
            self.prevcmap = self.cmap
            self.clim = 6000
            self.plotdiff = False
            self.fieldname = None
    All = Container()
    All.view = View(ni, nj)
    All.edits = Edits()

    # Read edit data, if it exists
    if 'iEdit' in rg.variables:
        jEdit = rg.variables['iEdit'][:]
        iEdit = rg.variables['jEdit'][:]
        zEdit = rg.variables['zEdit'][:]  # Original value of edited data
        for l, i in enumerate(iEdit):
            All.edits.setVal(fullData.height[iEdit[l], jEdit[l]])
            fullData.height[iEdit[l], jEdit[l]] = zEdit[l]  # Restore data
            All.edits.add(iEdit[l], jEdit[l])
    if applyFile:
        try:  # first try opening as a NetCDF
            apply = Dataset(applyFile, 'r')
            if 'iEdit' in apply.variables:
                jEdit = apply.variables['iEdit'][:]
                iEdit = apply.variables['jEdit'][:]
                zNew = apply.variables[variable]
                for l, i in enumerate(iEdit):
                    All.edits.add(iEdit[l], jEdit[l], zNew[iEdit[l], jEdit[l]])
            apply.close()
        except:
            try:  # if that fails, try opening as a text file
                with open(applyFile, 'rt') as edFile:
                    line = edFile.readline()
                    version = line.strip().split()[-1]
                    if version == '1':
                        while line:
                            line = edFile.readline()
                            linedata = line.strip().split('#')[0].strip()
                            if linedata:
                                jEdit, iEdit, _, zNew = linedata.split()  # swaps meaning of i & j
                                iEdit = int(iEdit)
                                jEdit = int(jEdit)
                                zNew = float(zNew)
                                All.edits.add(iEdit, jEdit, zNew)
                    else:
                        error('Unsupported version '+version+' in "'+applyFile+'".')
            except:
                error('There was a problem applying edits from "'+applyFile+'".')

    All.data = fullData.cloneWindow(
        (All.view.i0, All.view.j0), (All.view.iw, All.view.jw))
    All.fieldname = All.data.fieldnames[0]
    if All.edits.ijz:
        All.data.applyEdits(fullData, All.edits.ijz)

    # A mask based solely on value of depth
    # notLand = np.where( depth<0, 1, 0)
    # wet = ice9it(600,270,depth)

    # plt.rcParams['toolbar'] = 'None'  # don't use - also disables statusbar

    def replot(All):
        if All.cbar is not None:
            All.cbar.remove()
        h = plt.pcolormesh(All.data.longitude, All.data.latitude,
                           All.data.plotfield, cmap=All.cmap,
                           vmin=-All.clim, vmax=All.clim)
        hc = plt.colorbar()
        return(h, hc)

    All.quadMesh, All.cbar = replot(All)
    All.syms = All.edits.plot(fullData)
    dir(All.syms)
    All.ax = plt.gca()
    All.ax.set_xlim(All.data.xlim)
    All.ax.set_ylim(All.data.ylim)

    if fullData.haveref:
        def setsource(label):
            All.fieldname = label
            All.data.plotfield = All.data.fields[All.fieldname]
            All.plotdiff = All.fieldname == All.data.fieldnames[2]
            if All.plotdiff and All.cmap != All.cmap3:
                All.prevcmap = All.cmap
                All.cmap = All.cmap3
            else:
                All.cmap = All.prevcmap
            All.quadMesh.set_cmap(All.cmap)
            All.cbar.mappable.set_cmap(All.cmap)
            All.quadMesh.set_array(All.data.plotfield.ravel())
            plt.draw()
        sourcebuttons = RadioButtons(plt.axes([.88, .4, 0.12, 0.15]),
                                     All.data.fieldnames)
        sourcebuttons.on_clicked(setsource)

    def setDepth(str):
        try:
            All.edits.setVal(float(str))
        except:
            pass
    tbax = plt.axes([0.12, 0.01, 0.3, 0.05])
    textbox = TextBox(tbax, 'set depth', '0')
    textbox.on_submit(setDepth)
    textbox.on_text_change(setDepth)
    def nothing(x,y):
        return ''
    tbax.format_coord = nothing  # stop status bar displaying coords in textbox
    All.textbox = textbox
    if fullData.haveref:
        All.useref = True
        userefcheck = CheckButtons(plt.axes([0.42, 0.01, 0.11, 0.05]),
                                   ['use ref'], [All.useref])
        def setuseref(_):
            All.useref = userefcheck.get_status()[0]
            if not All.useref:
                All.edits.setVal(0.0)
                All.textbox.set_val(repr(All.edits.newDepth))
        userefcheck.on_clicked(setuseref)
    else:
        All.useref = False

    lowerButtons = Buttons(left=.9)

    def undoLast(event):
        All.edits.pop()
        All.data = fullData.cloneWindow(
            (All.view.i0, All.view.j0), (All.view.iw, All.view.jw),
            fieldname=All.fieldname)
        All.data.applyEdits(fullData, All.edits.ijz)
        All.quadMesh.set_array(All.data.plotfield.ravel())
        All.edits.updatePlot(fullData, All.syms)
        plt.draw()
    lowerButtons.add('Undo', undoLast)

    upperButtons = Buttons(bottom=1-.0615)

    def colorScale(event):
        Levs = [50, 100, 200, 500, 1000, 2000, 3000, 4000, 5000, 6000]
        i = Levs.index(All.clim)
        if event == ' + ':
            i = min(i+1, len(Levs)-1)
        elif event == ' - ':
            i = max(i-1, 0)
        elif event == 'Flip' and not All.plotdiff:
            if All.cmap == All.cmap1:
                All.cmap = All.cmap2
            else:
                All.cmap = All.cmap1
        All.clim = Levs[i]
        All.quadMesh.set_clim(vmin=-All.clim, vmax=All.clim)
        All.quadMesh.set_cmap(All.cmap)
        All.cbar.mappable.set_clim(vmin=-All.clim, vmax=All.clim)
        All.cbar.mappable.set_cmap(All.cmap)
        plt.draw()

    def moveVisData(di, dj):
        All.view.move(di, dj)
        All.data = fullData.cloneWindow(
            (All.view.i0, All.view.j0), (All.view.iw, All.view.jw),
            fieldname=All.fieldname)
        All.data.applyEdits(fullData, All.edits.ijz)
        plt.sca(All.ax)
        plt.cla()
        All.quadMesh, All.cbar = replot(All)
        All.ax.set_xlim(All.data.xlim)
        All.ax.set_ylim(All.data.ylim)
        All.syms = All.edits.plot(fullData)
        plt.draw()

    def moveWindowLeft(event): moveVisData(-1, 0)
    upperButtons.add('West', moveWindowLeft)

    def moveWindowRight(event): moveVisData(1, 0)
    upperButtons.add('East', moveWindowRight)

    def moveWindowDown(event): moveVisData(0, -1)
    upperButtons.add('South', moveWindowDown)

    def moveWindowUp(event): moveVisData(0, 1)
    upperButtons.add('North', moveWindowUp)
    climButtons = Buttons(bottom=1-.0615, left=0.75)

    def incrCScale(event): colorScale(' + ')
    climButtons.add(' + ', incrCScale)

    def decrCScale(event): colorScale(' - ')
    climButtons.add(' - ', decrCScale)

    def revcmap(event): colorScale('Flip')
    climButtons.add('Flip', revcmap)
    plt.sca(All.ax)

    def onClick(event):  # Mouse button click
        if event.inaxes == All.ax and event.button == 1 and event.xdata:
            # left click: edit point
            (i, j) = findPointInMesh(fullData.longitude, fullData.latitude,
                                     event.xdata, event.ydata)
            if i is not None:
                (I, J) = findPointInMesh(All.data.longitude, All.data.latitude,
                                         event.xdata, event.ydata)
                if event.dblclick:
                    nVal = -99999
                    if All.data.height[I+1, J] < 0:
                        nVal = max(nVal, All.data.height[I+1, J])
                    if All.data.height[I-1, J] < 0:
                        nVal = max(nVal, All.data.height[I-1, J])
                    if All.data.height[I, J+1] < 0:
                        nVal = max(nVal, All.data.height[I, J+1])
                    if All.data.height[I, J-1] < 0:
                        nVal = max(nVal, All.data.height[I, J-1])
                    if nVal == -99999:
                        return
                    All.edits.add(i, j, nVal)
                    All.data.height[I, J] = nVal
                else:
                    All.edits.add(i, j)
                    All.data.height[I, J] = All.edits.get()
                if All.data.haveref:
                    All.data.diff[I, J] = All.data.height[I, J] - All.data.ref[I, J]
                All.quadMesh.set_array(All.data.plotfield.ravel())
                All.edits.updatePlot(fullData, All.syms)
                plt.draw()
        elif event.inaxes == All.ax and event.button == 3 and event.xdata:
            # right click: undo edit
            (i, j) = findPointInMesh(fullData.longitude, fullData.latitude,
                                     event.xdata, event.ydata)
            if i is not None:
                All.edits.delete(i, j)
                All.data = fullData.cloneWindow(
                    (All.view.i0, All.view.j0), (All.view.iw, All.view.jw),
                    fieldname=All.fieldname)
                All.data.applyEdits(fullData, All.edits.ijz)
                All.quadMesh.set_array(All.data.plotfield.ravel())
                All.edits.updatePlot(fullData, All.syms)
                plt.draw()
        elif event.inaxes == All.ax and event.button == 2 and event.xdata:
            zoom(event)  # Re-center
    plt.gcf().canvas.mpl_connect('button_press_event', onClick)

    def zoom(event):  # Scroll wheel up/down
        if event.button == 'up':
            scale_factor = 1/1.5  # deal with zoom in
        elif event.button == 'down':
            scale_factor = 1.5  # deal with zoom out
        else:
            scale_factor = 1.0
        new_xlim, new_ylim = newLims(
            All.ax.get_xlim(), All.ax.get_ylim(),
            (event.xdata, event.ydata),
            All.data.xlim, All.data.ylim,
            All.view.ni, All.view.nj,
            scale_factor)
        if new_xlim is None:
            return  # No change in limits
        All.view.seti(new_xlim)
        All.view.setj(new_ylim)
        All.data = fullData.cloneWindow(
            (All.view.i0, All.view.j0), (All.view.iw, All.view.jw),
            fieldname=All.fieldname)
        All.data.applyEdits(fullData, All.edits.ijz)
        plt.sca(All.ax)
        plt.cla()
        All.quadMesh, All.cbar = replot(All)
        # All.ax.set_xlim(All.data.xlim)
        # All.ax.set_ylim(All.data.ylim)
        All.syms = All.edits.plot(fullData)
        All.ax.set_xlim(new_xlim)
        All.ax.set_ylim(new_ylim)
        # All.cbar.mappable.set_clim(vmin=-All.clim, vmax=All.clim)
        # All.cbar.mappable.set_cmap(All.cmap)
        plt.draw()  # force re-draw
    plt.gcf().canvas.mpl_connect('scroll_event', zoom)

    def statusMesg(x, y):
        j, i = findPointInMesh(fullData.longitude, fullData.latitude, x, y)
        if All.useref:
            All.textbox.set_val(repr(fullData.ref[j, i]))  # callback calls All.edits.setVal
        if i is not None:
            height = fullData.height[j, i]
            newval = All.edits.getEdit(j, i)
            if newval is not None:
                return 'depth(%i,%i) = %g (was %g)      depth - set depth = %g' % \
                        (i, j, newval, height, newval - All.edits.newDepth)
            else:
                return 'depth(%i,%i) = %g      depth - set depth = %g' % \
                        (i, j, height, height - All.edits.newDepth)
        else:
            return 'new depth = %g' % \
                    (All.edits.newDepth)
    All.ax.format_coord = statusMesg

    if not nogui:
        print("""
Ignore all the controls in the toolbar at the top of the window.
Zoom in and out with the scroll wheel.
Pan the view with the North, South, East and West buttons.
Use +, -, Flip buttons to modify the colormap.
Set the prescribed depth with the textbox at the bottom.
Left click on a cell to apply the prescribed depth value.
Right click on a cell to reset to the original value.
Double left click to assign the highest of the 4 nearest points with depth<0.
Close the window to write the edits to the output file.
""")
        plt.show()

# The following is executed after GUI window is closed
    # All.edits.list()
    if not outFile:
        outFile = join(dirname(fileName), 'edit_'+basename(fileName))
    editsFile = splitext(outFile)[0]+'.txt'
    if not outFile == ' ':
        print('Made %i edits.' % (len(All.edits.ijz)))
        print('Writing edited topography to "'+outFile+'".')
        # Create new netcdf file
        if not fileName == outFile:
            sh.copyfile(fileName, outFile)
        try:
            rg = Dataset(outFile, 'r+')
        except:
            error('There was a problem opening "'+outFile+'".')
        rgVar = rg.variables[variable]  # handle to the variable
        dims = rgVar.dimensions  # tuple of dimensions
        rgVar[:] = fullData.height[:, :]  # Write the data
        if All.edits.ijz:
            # print('Applying %i edits' % (len(All.edits.ijz)))
            if 'nEdits' in rg.dimensions:
                numEdits = rg.dimensions['nEdits']
            else:
                numEdits = rg.createDimension(
                    'nEdits', 0)  # len(All.edits.ijz))
            if 'iEdit' in rg.variables:
                iEd = rg.variables['iEdit']
            else:
                iEd = rg.createVariable('iEdit', 'i4', ('nEdits',))
                iEd.long_name = 'i-index of edited data'
            if 'jEdit' in rg.variables:
                jEd = rg.variables['jEdit']
            else:
                jEd = rg.createVariable('jEdit', 'i4', ('nEdits',))
                jEd.long_name = 'j-index of edited data'
            if 'zEdit' in rg.variables:
                zEd = rg.variables['zEdit']
            else:
                zEd = rg.createVariable('zEdit', 'f4', ('nEdits',))
                zEd.long_name = 'Original value of edited data'
                zEd.units = rgVar.units
            hist_str = 'made %i changes (i, j, old, new): ' % len(All.edits.ijz)
            for l, (i, j, z) in enumerate(All.edits.ijz):
                if l > 0:
                    hist_str += ', '
                iEd[l] = j
                jEd[l] = i
                zEd[l] = rgVar[i, j]
                rgVar[i, j] = z
                hist_str += repr((j, i, zEd[l].item(), rgVar[i, j].item()))
            print(hist_str.replace(': ', ':\n').replace('), ', ')\n'))
            hist_str = time.ctime(time.time()) + ' ' \
                + ' '.join(sys.argv) \
                + ' ' + hist_str
            if 'history' not in rg.ncattrs():
                rg.history = hist_str
            else:
                rg.history = rg.history + ' | ' + hist_str
        # write editsFile even if no edits, so editsFile will match outFile
        print('Writing list of edits to text file "'+editsFile+'" (this can be used with --apply).')
        try:
            with open(editsFile, 'wt') as edfile:
                edfile.write('editTopo.py edits file version 1\n')
                edfile.write('#\n# This file can be used as an argument for editTopo.py --apply\n#\n')
                edfile.write('# created: ' + time.ctime(time.time()) + '\n')
                edfile.write('# by: ' + pwd.getpwuid(os.getuid()).pw_name + '\n')
                edfile.write('# via: ' + ' '.join(sys.argv) + '\n#\n')
                if All.edits.ijz:
                    ii, jj, _ = zip(*All.edits.ijz)
                    news = [rgVar[i, j].item() for (i, j, _) in All.edits.ijz]
                    olds = [fullData.height[i, j].item() for (i, j, _) in All.edits.ijz]
                    iiwidth = max([len(repr(x)) for x in ii], default=0) + 2
                    jjwidth = max([len(repr(x)) for x in jj], default=0) + 2
                    oldwidth = max([len(repr(x)) for x in olds], default=0) + 2
                    edfile.write('# ' + \
                                 'i'.rjust(jjwidth-2) +  # swaps meaning of i & j
                                 'j'.rjust(iiwidth) +    # ditto
                                 '  ' +
                                 'old'.ljust(oldwidth) +
                                 'new' + '\n')
                    for (i, j, old, new) in zip(ii, jj, olds, news):
                        edfile.write(repr(j).rjust(jjwidth) +  # swaps meaning of i & j
                                     repr(i).rjust(iiwidth) +  # ditto
                                     '  ' +
                                     repr(old).ljust(oldwidth) +
                                     repr(new) + '\n')
                else:
                    edfile.write('#    i    j    old    new\n')
        except:
            error('There was a problem creating "'+editsFile+'".')
        rg.close()


def ice9it(i, j, depth):
    # Iterative implementation of "ice 9"
    wetMask = 0*depth
    (ni, nj) = wetMask.shape
    stack = set()
    stack.add((i, j))
    while stack:
        (i, j) = stack.pop()
        if wetMask[i, j] or depth[i, j] >= 0:
            continue
        wetMask[i, j] = 1
        if i > 0:
            stack.add((i-1, j))
        else:
            stack.add((ni-1, j))
        if i < ni-1:
            stack.add((i+1, j))
        else:
            stack.add((0, j))
        if j > 0:
            stack.add((i, j-1))
        if j < nj-1:
            stack.add((i, j+1))
    return wetMask


def findPointInMesh(meshX, meshY, pointX, pointY):
    def sign(x):
        if x > 0:
            return 1.0
        elif x < 0:
            return -1.0
        else:
            return 0.

    def crossProd(u0, v0, u1, v1):
        return sign(u0*v1 - u1*v0)

    def isPointInConvexPolygon(pX, pY, p):
        u0 = pX[0]-pX[-1]
        v0 = pY[0]-pY[-1]
        u1 = pX[-1] - p[0]
        v1 = pY[-1] - p[1]
        firstSign = crossProd(u0, v0, u1, v1)
        for n in range(len(pX)-1):
            u0 = pX[n+1]-pX[n]
            v0 = pY[n+1]-pY[n]
            u1 = pX[n] - p[0]
            v1 = pY[n] - p[1]
            if crossProd(u0, v0, u1, v1)*firstSign < 0:
                return False
        return True

    def recurIJ(mX, mY, p, ij00, ij22):
        # Unpack indices
        i0 = ij00[0]
        i2 = ij22[0]
        j0 = ij00[1]
        j2 = ij22[1]
        # Test bounding box first (bounding box is larger than polygon)
        xmin = min(np.amin(mX[i0, j0:j2]), np.amin(
            mX[i2, j0:j2]), np.amin(mX[i0:i2, j0]), np.amin(mX[i0:i2, j2]))
        xmax = max(np.amax(mX[i0, j0:j2]), np.amax(
            mX[i2, j0:j2]), np.amax(mX[i0:i2, j0]), np.amax(mX[i0:i2, j2]))
        ymin = min(np.amin(mY[i0, j0:j2]), np.amin(
            mY[i2, j0:j2]), np.amin(mY[i0:i2, j0]), np.amin(mY[i0:i2, j2]))
        ymax = max(np.amax(mY[i0, j0:j2]), np.amax(
            mY[i2, j0:j2]), np.amax(mY[i0:i2, j0]), np.amax(mY[i0:i2, j2]))
        if p[0] < xmin or p[0] > xmax or p[1] < ymin or p[1] > ymax:
            return None, None
        if i2 > i0+1:
            i1 = int(0.5*(i0+i2))
            if j2 > j0+1:  # Four quadrants to test
                j1 = int(0.5*(j0+j2))
                iAns, jAns = recurIJ(mX, mY, p, (i0, j0), (i1, j1))
                if iAns is None:
                    iAns, jAns = recurIJ(mX, mY, p, (i1, j1), (i2, j2))
                if iAns is None:
                    iAns, jAns = recurIJ(mX, mY, p, (i0, j1), (i1, j2))
                if iAns is None:
                    iAns, jAns = recurIJ(mX, mY, p, (i1, j0), (i2, j1))
            else:  # Two halves, east/west, to test
                j1 = int(0.5*(j0+j2))
                iAns, jAns = recurIJ(mX, mY, p, (i0, j0), (i1, j2))
                if iAns is None:
                    iAns, jAns = recurIJ(mX, mY, p, (i1, j0), (i2, j2))
        else:
            if j2 > j0+1:  # Two halves, north/south, to test
                j1 = int(0.5*(j0+j2))
                iAns, jAns = recurIJ(mX, mY, p, (i0, j0), (i2, j1))
                if iAns is None:
                    iAns, jAns = recurIJ(mX, mY, p, (i0, j1), (i2, j2))
            else:  # Only one cell left (based on the bounding box)
                if not isPointInConvexPolygon(
                    [mX[i0, j0], mX[i0+1, j0], mX[i0+1, j0+1], mX[i0, j0+1]],
                    [mY[i0, j0], mY[i0+1, j0], mY[i0+1, j0+1], mY[i0, j0+1]],
                        p):
                    return None, None
                return i0, j0
        return iAns, jAns
    (ni, nj) = meshX.shape
    ij00 = [0, 0]
    ij22 = [ni-1, nj-1]
    return recurIJ(meshX, meshY, (pointX, pointY), ij00, ij22)


# Calculate a new window by scaling the current window, centering
# on the cursor if possible.
def newLims(cur_xlim, cur_ylim, cursor, xlim, ylim, ni, nj, scale_factor):
    xcursor, ycursor = cursor
    if xcursor is None or ycursor is None:
        return None, None
    cur_xrange = (cur_xlim[1] - cur_xlim[0])
    cur_yrange = (cur_ylim[1] - cur_ylim[0])
    new_xrange = int(round(min(ni, max(10, cur_xrange*scale_factor))))
    new_yrange = int(round(min(nj, (nj/ni)*new_xrange)))
    xL = int(round(xcursor - new_xrange*(xcursor-cur_xlim[0])/cur_xrange))
    xR = int(round(xcursor + new_xrange*(cur_xlim[1]-xcursor)/cur_xrange))
    if xL < 0:
            xL = 0
            xR = xL + new_xrange
    elif xR > ni:
            xR = ni
            xL = xR - new_xrange
    yL = int(round(ycursor - new_yrange*(ycursor-cur_ylim[0])/cur_yrange))
    yR = int(round(ycursor + new_yrange*(cur_ylim[1]-ycursor)/cur_yrange))
    if yL < 0:
            yL = 0
            yR = yL + new_yrange
    elif yR > nj:
            yR = nj
            yL = yR - new_yrange
    if xL == cur_xlim[0] and xR == cur_xlim[1] and \
       yL == cur_ylim[0] and yR == cur_ylim[1]:
            return None, None
    return (xL, xR), (yL, yR)


# Class to handle adding buttons to GUI
class Buttons:
    scale = 0.014
    space = .01

    def __init__(self, bottom=.015, left=.015):
        self.leftEdge = left
        self.bottomEdge = bottom
        self.height = .05
        self.list = []

    def add(self, label, fn):  # fn is callback
        width = self.scale*len(label)
        np = [self.leftEdge, self.bottomEdge, width, self.height]
        self.leftEdge = self.leftEdge + width + self.space
        button = Button(plt.axes(np), label)
        button.on_clicked(fn)
        self.list.append(button)


# Class to contain edits
class Edits:
    def __init__(self):
        self.newDepth = 0.0
        self.ijz = []

    def setVal(self, newVal):
        self.newDepth = newVal

    def get(self): return self.newDepth

    def getEdit(self, i, j):
        for I, J, D in self.ijz:
            if (i, j) == (I, J):
                return D
        return None

    def delete(self, i, j):
        for I, J, D in self.ijz:
            if (i, j) == (I, J):
                self.ijz.remove((I, J, D))

    def add(self, i, j, nVal=None):
        self.delete(i, j)
        if nVal is not None:
            self.ijz.append((i, j, nVal))
        else:
            self.ijz.append((i, j, self.newDepth))

    def pop(self):
        if self.ijz:
            self.ijz.pop()

    def list(self):
        for a in self.ijz:
            print(a)

    def plot(self, topo):
        x = []
        y = []
        for i, j, z in self.ijz:
            tx, ty = topo.cellCoord(j, i)
            if tx:
                x.append(tx)
                y.append(ty)
        h, = plt.plot(x, y, linewidth=0, marker='o', color='red',
                      markersize=5, markerfacecolor='none')
        return h

    def updatePlot(self, topo, h):
        x = []
        y = []
        for i, j, z in self.ijz:
            tx, ty = topo.cellCoord(j, i)
            if tx:
                x.append(tx)
                y.append(ty)
        if x:
            h.set_xdata(x)
            h.set_ydata(y)


# Class to contain data
class Topography:
    def __init__(self, lon, lat, height, ref, fieldname=None):
        self.longitude = lon
        self.latitude = lat
        self.height = np.copy(height)
        self.xlim = (np.min(lon), np.max(lon))
        self.ylim = (np.min(lat), np.max(lat))
        if ref is None:
            self.ref = None
            self.diff = None
            self.haveref = False
        else:
            self.ref = np.copy(ref)
            self.haveref = True
            self.diff = self.height - self.ref
        self.fieldnames = ['Editing', 'Ref', 'Ed - Ref']  # also used for button labels
        self.fields = dict(zip(self.fieldnames, [self.height, self.ref, self.diff]))
        if fieldname is None:
            fieldname = self.fieldnames[0]
        self.plotfield = self.fields[fieldname]  # the field that is actually plotted

    def cloneWindow(self, i0_j0, iw_jw, fieldname=None):
        i0, j0 = i0_j0
        iw, jw = iw_jw
        i1 = i0 + iw
        j1 = j0 + jw
        if self.ref is None:
            return Topography(self.longitude[j0:j1+1, i0:i1+1],
                              self.latitude[j0:j1+1, i0:i1+1],
                              self.height[j0:j1, i0:i1],
                              self.ref,
                              fieldname=fieldname)
        else:
            return Topography(self.longitude[j0:j1+1, i0:i1+1],
                              self.latitude[j0:j1+1, i0:i1+1],
                              self.height[j0:j1, i0:i1],
                              self.ref[j0:j1, i0:i1],
                              fieldname=fieldname)

    def applyEdits(self, origData, ijz):
        for i, j, z in ijz:
            x = (origData.longitude[i, j] + origData.longitude[i+1, j+1])/2.
            y = (origData.latitude[i, j] + origData.latitude[i+1, j+1])/2.
            (I, J) = findPointInMesh(self.longitude, self.latitude, x, y)
            if I is not None:
                self.height[I, J] = z
                if self.haveref:
                    self.diff[I, J] = self.height[I, J] - self.ref[I, J]

    def cellCoord(self, j, i):
        #ni, nj = self.longitude.shape
        # if i<0 or j<0 or i>=ni-1 or j>=nj-1: return None, None
        x = (self.longitude[i, j] + self.longitude[i+1, j+1])/2.
        y = (self.latitude[i, j] + self.latitude[i+1, j+1])/2.
        return x, y

# Class to record the editing window


class View:
    def __init__(self, ni, nj):
        self.ni = ni
        self.nj = nj
        self.i0 = 0
        self.j0 = 0
        self.iw = ni
        self.jw = nj

    def move(self, di, dj):
        self.i0 = min(max(0, self.i0+int(di*self.iw/2.)), self.ni-self.iw)
        self.j0 = min(max(0, self.j0+int(dj*self.jw/2.)), self.nj-self.jw)

    def geti(self): return (self.i0, self.i0+self.iw)

    def getj(self): return (self.j0, self.j0+self.jw)

    def seti(self, xlim):
        self.i0 = xlim[0]
        self.iw = xlim[1] - xlim[0]

    def setj(self, ylim):
        self.j0 = ylim[0]
        self.jw = ylim[1] - ylim[0]


# Invoke main()
if __name__ == '__main__':
    main()
