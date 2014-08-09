##############################################################################
# Copyright (C) 2005  Adam Smith  asmith@agile-software.com
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##############################################################################

import os, sys, shutil
import PIL.Image
from ZoomifyBase import ZoomifyBase

class ZoomifyFileProcessor(ZoomifyBase):

  _v_saveToLocation = ''


  def openImage(self):
    """ load the image data """

    try:
      return PIL.Image.open(self._v_imageFilename)
    except Exception, ex:
      print 'could not open file named: ' + self._v_imageFilename
      print ex
      sys.exit()
    #print self.getImageInfo()
    return None


  def createTileContainer(self, tileContainerName=None):
    """ create a container for the next group of tiles within the data container """

    tileContainerPath = os.path.join(self._v_saveToLocation, tileContainerName)
    if not os.path.exists(tileContainerPath):
      os.mkdir(tileContainerPath)

    return


  def createDataContainer(self, imageName):
    """ create a container for tiles and tile metadata """

    directory, filename = os.path.split(imageName)
    if not directory:
      directory = os.getcwd()
    root, ext = os.path.splitext(filename)
    if not ext:
      root = root + '_data'

    self._v_saveToLocation = os.path.join(directory, root)

    # If the paths already exist, an image is being re-processed, clean up for it.
    try:
      if os.path.exists(self._v_saveToLocation):
        shutil.rmtree(self._v_saveToLocation)

      if not os.path.exists(self._v_saveToLocation):
        os.mkdir(self._v_saveToLocation)

    except Exception, ex:
      print ex
      sys.exit()

    return


  def getFileReference(self, scaleNumber, columnNumber, rowNumber):
    """ get the full path of the file the tile will be saved as """

    tileFileName = self.getTileFileName(scaleNumber, columnNumber, rowNumber)
    tileContainerName = self.getAssignedTileContainerName(tileFileName=tileFileName)
    return os.path.join(os.path.join(self._v_saveToLocation, tileContainerName), tileFileName)


  def getNumberOfTiles(self):
    """ get the number of tiles generated """

    #return len(os.listdir(self._v_tileContainerPath))
    return self.numberOfTiles

  def saveXMLOutput(self):
    """ save xml metadata about the tiles """

    xmlFile = open(os.path.join(self._v_saveToLocation, 'ImageProperties.xml'), 'w')
    xmlFile.write(self.getXMLOutput())
    xmlFile.close()

    return


  def saveTile(self, image, scaleNumber, column, row):
    """ save the cropped region """

    w,h = image.size
    if w != 0 and h != 0:
      #print 'saving tile: ' + str(h) + 'x'+ str(h)
      image.save(self.getFileReference(scaleNumber, column, row), 'JPEG', quality=self.qualitySetting)

    return


  def ZoomifyProcess(self, imageNames=[]):
    """ the method the client calls to generate zoomify metadata """

    if type(imageNames) is type(''):
      # !!! add code to pass a directory path as a string and process all files
      # !!! in the directory
      imageNames = [imageNames]

    for imageName in imageNames:
      self._v_imageFilename = imageName
      self.createDataContainer(imageName)
      self.getImageMetadata()
      self.processImage()
      self.saveXMLOutput()

    return


processor = ZoomifyFileProcessor()
processor.ZoomifyProcess(sys.argv[1:])
