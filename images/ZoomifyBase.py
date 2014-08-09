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

import os, sys, shutil, tempfile
import PIL.Image

class ZoomifyBase:

  _v_imageFilename = ''
  format = ''
  originalWidth = 0
  originalHeight = 0
  _v_scaleInfo = []
  numberOfTiles = 0
  _v_tileGroupMappings = {}
  qualitySetting = 100
  tileSize = 256
 
 
  def openImage(self):
    """ load the image data """
    
    pass
      
    return
    
    
  def getImageInfo(self):
    """ """
    
    image = self.openImage()
    
    self.format = image.format
    self.originalWidth, self.originalHeight = image.size
    image = None
    
    width, height = (self.originalWidth, self.originalHeight)
    self._v_scaleInfo = [(width, height)]
    while (width > self.tileSize) or (height > self.tileSize):
      width, height = (width / 2, height / 2)
      self._v_scaleInfo.insert(0, (width, height))
    
    totalTiles=0
    tier, rows, columns = (0,0,0)
    for tierInfo in self._v_scaleInfo:
      #print '____________________'
      #print 'tier: ' + str(tier)
      width, height = tierInfo
      #print 'width: ' + str(width)
      #print 'height: ' + str(height)
      rows = height/self.tileSize
      if height % self.tileSize > 0:
        rows +=1
      #print 'rows: ' + str(rows)
      columns = width/self.tileSize
      if width%self.tileSize > 0:
        columns += 1
      #print 'columns: ' + str(columns)
      #print 'total tiles for tier: ' + str(rows * columns)
      totalTiles += rows * columns
      #print ''
      tier += 1
      
    #print 'total tiles for all tiers: ' + str(totalTiles)
      
  def getImageMetadata(self):
    """ given an image name, load it and extract metadata """
    
    image = self.openImage()
    
    self.format = image.format
    self.originalWidth, self.originalHeight = image.size
    image = None
    
    # get scaling information
    width, height = (self.originalWidth, self.originalHeight)
    self._v_scaleInfo = [(width, height)]
    while (width > self.tileSize) or (height > self.tileSize):
      width, height = (width / 2, height / 2)
      self._v_scaleInfo.insert(0, (width, height))
    
    # tile and tile group information
    self.preProcess()
    
    return
    
    
  def createDataContainer(self, imageName):
    """ create a container for tile groups and tile metadata """
    
    pass
    
    return
    
    
  def getAssignedTileContainerName(self, tileFileName=None):
    """ return the name of the tile group for the indicated tile """
    if tileFileName:
      if hasattr(self, '_v_tileGroupMappings') and self._v_tileGroupMappings:
        containerName = self._v_tileGroupMappings.get(tileFileName, None)
        if containerName:
          return containerName
    return self.getNewTileContainerName()
    
  def getNewTileContainerName(self, tileGroupNumber=0):
    """ return the name of the next tile group container """
    return 'TileGroup' + str(tileGroupNumber)
    
    
  def createTileContainer(self, tileContainerName=None):
    """ create a container for the next group of tiles within the data container """
    
    pass
    
    return
 
    
    
  def getTileFileName(self, scaleNumber, columnNumber, rowNumber):
    """ get the name of the file the tile will be saved as """
    
    return '%s-%s-%s.jpg' % (str(scaleNumber), str(columnNumber), str(rowNumber))
    
    
  def getFileReference(self, scaleNumber, columnNumber, rowNumber):
    """ get the full path of the file the tile will be saved as """
    
    pass
    
    return 
    
    
  def getNumberOfTiles(self):
    """ get the number of tiles generated 
        Should this be implemented as a safeguard, or just use the count of 
        tiles gotten from processing? (This would make subclassing a little
        easier.) """

    return self.numberOfTiles
    
    
  def getXMLOutput(self):
    """ create xml metadata about the tiles """
    
    numberOfTiles = self.getNumberOfTiles()
    xmlOutput = '<IMAGE_PROPERTIES WIDTH="%s" HEIGHT="%s" NUMTILES="%s" NUMIMAGES="1" VERSION="1.8" TILESIZE="%s" />'
    xmlOutput = xmlOutput % (str(self.originalWidth), str(self.originalHeight), str(numberOfTiles), str(self.tileSize))
    
    return xmlOutput
    
    
  def saveXMLOutput(self):
    """ save xml metadata about the tiles """
    
    pass
    
    return
    
  
  def saveTile(self, image, scaleNumber, column, row):
    """ save the cropped region """
    
    pass
    
    return
    

  def processImage(self):
    """ starting with the original image, start processing each row """
    tier=(len(self._v_scaleInfo) -1)
    row = 0
    ul_y, lr_y = (0,0)
    root, ext = os.path.splitext(self._v_imageFilename)  
    if not root:
      root = self._v_imageFilename
    ext = '.jpg'
    while row * self.tileSize < self.originalHeight:
      ul_y = row * self.tileSize
      if (ul_y + self.tileSize) < self.originalHeight:
        lr_y = ul_y + self.tileSize
      else:
        lr_y = self.originalHeight
      image = self.openImage()
      imageRow = image.crop([0, ul_y, self.originalWidth, lr_y])
      saveFilename = root + str(tier) + '-' + str(row) +  ext
      if imageRow.mode != 'RGB':
        imageRow = imageRow.convert('RGB')
      imageRow.save(os.path.join(tempfile.gettempdir(), saveFilename), 'JPEG', quality=100)
      image = None
      imageRow = None
      if os.path.exists(os.path.join(tempfile.gettempdir(), saveFilename)): 
        self.processRowImage(tier=tier, row=row)
      row += 1
    
  def processRowImage(self, tier=0, row=0):
    """ for an image, create and save tiles """
      
    #print '*** processing tier: ' + str(tier) + ' row: ' + str(row)
    
    tierWidth, tierHeight = self._v_scaleInfo[tier]
    rowsForTier = tierHeight/self.tileSize
    if tierHeight % self.tileSize > 0:
      rowsForTier +=1
    root, ext = os.path.splitext(self._v_imageFilename)  
    if not root:
      root = self._v_imageFilename
    ext = '.jpg'
    
    imageRow = None
    
    if tier == (len(self._v_scaleInfo) -1):
      firstTierRowFile = root + str(tier) + '-' + str(row) + ext
      if os.path.exists(os.path.join(tempfile.gettempdir(),firstTierRowFile)):
        imageRow = PIL.Image.open(os.path.join(tempfile.gettempdir(), firstTierRowFile))
    else:
      # create this row from previous tier's rows
      imageRow = PIL.Image.new('RGB', (tierWidth, self.tileSize))
      
      firstRowFile = root + str(tier+1) + '-' + str(row + row) + ext
      firstRowWidth, firstRowHeight = (0,0)
      secondRowWidth, secondRowHeight = (0,0)
      if os.path.exists(os.path.join(tempfile.gettempdir(),firstRowFile)):
        firstRowImage = PIL.Image.open(os.path.join(tempfile.gettempdir(),firstRowFile))
        firstRowWidth, firstRowHeight = firstRowImage.size
        imageRow.paste(firstRowImage, (0,0))
        os.remove(os.path.join(tempfile.gettempdir(), firstRowFile))
      
      secondRowFile = root + str(tier+1) + '-' + str(row + row +1) + ext
      # there may not be a second row at the bottom of the image...
      if os.path.exists(os.path.join(tempfile.gettempdir(), secondRowFile)):
        secondRowImage = PIL.Image.open(os.path.join(tempfile.gettempdir(), secondRowFile))
        secondRowWidth, secondRowHeight = secondRowImage.size
        imageRow.paste(secondRowImage, (0, firstRowHeight))
        os.remove(os.path.join(tempfile.gettempdir(), secondRowFile))
        
      # the last row may be less than self.tileSize...
      if (firstRowHeight + secondRowHeight) < (self.tileSize*2):
        imageRow = imageRow.crop((0, 0, tierWidth, (firstRowHeight+secondRowHeight)))
      
    if imageRow:

      # cycle through columns, then rows
      column = 0
      imageWidth, imageHeight = imageRow.size
      ul_x, ul_y, lr_x, lr_y = (0,0,0,0) # final crop coordinates
      while not ((lr_x == imageWidth) and (lr_y == imageHeight)):
        
        # set lower right cropping point
        if (ul_x + self.tileSize) < imageWidth:
          lr_x = ul_x + self.tileSize
        else:
          lr_x = imageWidth
          
        if (ul_y + self.tileSize) < imageHeight:
          lr_y = ul_y + self.tileSize
        else:
          lr_y = imageHeight
            
        #tierLabel = len(self._v_scaleInfo) - tier
        self.saveTile(imageRow.crop([ul_x, ul_y, lr_x, lr_y]), tier, column, row)
        self.numberOfTiles += 1
        #print 'created tile: ' + str(self.numberOfTiles) + ' (' + str(tier) + ',' + str(column) + ',' + str(row) + ')'

        # set upper left cropping point
        if (lr_x == imageWidth):
          ul_x=0
          ul_y = lr_y
          column = 0
          #row += 1
        else:
          ul_x = lr_x
          column += 1
        
      if tier > 0:
        # a bug was discovered when a row was exactly 1 pixel in height
        # this extra checking accounts for that
        if imageHeight > 1:
          tempImage = imageRow.resize((imageWidth/2, imageHeight/2), PIL.Image.ANTIALIAS)
          tempImage.save(os.path.join(tempfile.gettempdir(), root + str(tier) + '-' + str(row) + ext))
          tempImage = None
      rowImage = None
      
      
      #if tier > 0:
        #tempImage = imageRow.resize((imageWidth/2, imageHeight/2), PIL.Image.ANTIALIAS)
        #tempImage.save(root + str(tier) + '-' + str(row) + ext)
        #print 'saved row file: ' + root + str(tier) + '-' + str(row) + ext
        #tempImage = None
      #rowImage = None
      
      if tier > 0:
        if row % 2 != 0:
          self.processRowImage(tier=(tier-1), row=((row-1)/2))
        elif row == rowsForTier-1:
          self.processRowImage(tier=(tier-1), row=(row/2))
        
    return
    
          
  def ZoomifyProcess(self, imageNames):
    """ the method the client calls to generate zoomify metadata """
      
    pass
      
    return


  def preProcess(self):
    """ plan for the arrangement of the tile groups """
   
    tier = 0
    tileGroupNumber = 0
    numberOfTiles = 0
    for width, height in self._v_scaleInfo:
  
      #cycle through columns, then rows
      row, column = (0,0)
      ul_x, ul_y, lr_x, lr_y = (0,0,0,0)  #final crop coordinates
      while not ((lr_x == width) and (lr_y == height)):
       
        tileFileName = self.getTileFileName(tier, column, row)
        tileContainerName = self.getNewTileContainerName(tileGroupNumber=tileGroupNumber)
        if numberOfTiles ==0:
          self.createTileContainer(tileContainerName=tileContainerName)
        elif (numberOfTiles % self.tileSize) == 0:
          tileGroupNumber += 1
          tileContainerName = self.getNewTileContainerName(tileGroupNumber=tileGroupNumber)
          self.createTileContainer(tileContainerName=tileContainerName)
        self._v_tileGroupMappings[tileFileName] = tileContainerName
        numberOfTiles += 1
       
        # for the next tile, set lower right cropping point
        if (ul_x + self.tileSize) < width:
          lr_x = ul_x + self.tileSize
        else:
          lr_x = width
         
        if (ul_y + self.tileSize) < height:
          lr_y = ul_y + self.tileSize
        else:
          lr_y = height
  
        # for the next tile, set upper left cropping point
        if (lr_x == width):
          ul_x=0
          ul_y = lr_y
          column = 0
          row += 1
        else:
          ul_x = lr_x
          column += 1
       
      tier += 1
       

