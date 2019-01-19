#!/usr/bin/env python3

## Auto batch process for Agisoft PhotoScan
##
## Author: Emiliano Molinaro
## email: molinaro@imada.sdu.dk
## Date: 16-01-2019

import PhotoScan
import os,re

# get the photo (.JPG) r
def getPhotoList(path, photoList):    
	pattern = '.JPG$'
	for root, dirs, files in os.walk(path):
		for name in files:
			if re.search(pattern,name):
				cur_path = os.path.join(root, name)
				photoList.append(cur_path)
							
def BatchProcess(path, file, options):
	
	PhotoScan.app.console.clear()
	## construct the document class
	doc = PhotoScan.app.document
	psxfile = path + file    
	list_files = os.listdir(path)
	
	if file in list_files:
		doc.open(psxfile)
		chunk = doc.chunk
		chunk = doc.addChunk()
	else:
		doc.save(psxfile)
		print ("Project saved to: " + psxfile)
		chunk = doc.addChunk()
		### get photo list... 
		photoList = []
		getPhotoList(path, photoList)
		### add photos... 
		chunk.addPhotos(photoList) 
		doc.save(psxfile)
	
	if options[0] == 'y':
		### matching photos...multiple nodes and GPU acceleration
		## the accuracy is one of [HighestAccuracy, HighAccuracy, MediumAccuracy, LowAccuracy, LowestAccuracy]
		chunk.matchPhotos(accuracy=PhotoScan.HighAccuracy, preselection=PhotoScan.NoPreselection, 
					   filter_mask=False, keypoint_limit=40000, tiepoint_limit=4000)
		doc.save(psxfile)
		
	if options[1] == 'y':
		### photos alignment...only on 1 node and no GPU acceleration
		chunk.alignCameras()
		doc.save(psxfile)
		
	if options[2] == 'y':
		### build depth maps...multiple nodes and GPU acceleration
		## the quality is one of [UltraQuality, HighQuality, MediumQuality, LowQuality, LowestQuality]
		chunk.buildDepthMaps(quality=PhotoScan.MediumQuality, filter=PhotoScan.AggressiveFiltering, reuse_depth=True)
		doc.save(psxfile)
	
	if options[3] == 'y':
		### build dense cloud (filtering the depth maps)...multiple nodes and no GPU acceleration
		chunk.buildDenseCloud(keep_depth=True)
		doc.save(psxfile)
		
	if options[4] == 'y':
		### build mesh...multiple nodes?? and no GPU acceleration
		## the quality is one of [UltraQuality, HighQuality, MediumQuality, LowQuality, LowestQuality]
		chunk.buildModel(surface=PhotoScan.Arbitrary, face_count=PhotoScan.HighFaceCount, 
						 interpolation=PhotoScan.EnabledInterpolation, quality=PhotoScan.MediumQuality, keep_depth=True, reuse_depth=True)
		doc.save(psxfile)
		
	if options[5] == 'y':
		### build texture...
		chunk.buildUV(mapping=PhotoScan.GenericMapping, count=1) # multiple nodes?? and no GPU acceleration
		chunk.buildTexture(blending=PhotoScan.MosaicBlending, size=2048) # multiple nodes?? and no GPU acceleration
		doc.save(psxfile)
		
		### export model
		model_file = psxfile[:-4] + "-model.ply"
		chunk.exportModel(path=model_file)

		### export report    
		report_file = psxfile[:-4] + "-report.pdf"
		description = " "
		title = "REPORT"
		chunk.exportReport(path=report_file, title=title, description=description, page_numbers=1)
	

def main():
	
	MP= "y" # matchPhotos (y/n)       # <<<<<<<<<<<<<<<<<<<
	AC= "y" # alignCameras (y/n)      # <<<<<<<<<<<<<<<<<<<
	DM= "y" # buildDepthMaps (y/n)    # <<<<<<<<<<<<<<<<<<<
	DC= "y" # buildDenseCloud (y/n)   # <<<<<<<<<<<<<<<<<<<
	BM= "y" # buildModel (y/n)        # <<<<<<<<<<<<<<<<<<<
	BT= "y" # buildTexture (y/n)      # <<<<<<<<<<<<<<<<<<<
	
	options = [MP,AC,DM,DC,BM,BT]
	
	path = "/work/sysops/molinaro/photoscan-pro/"
	
	folder = "GT18_B"                 # <<<<<<<<<<<<<<<<<<<
	file = "project2-EM.psx"          # <<<<<<<<<<<<<<<<<<<
	
	path = "/work/sysops/molinaro/photoscan-pro/" + folder + "/"

	BatchProcess(path, file, options)
	
if __name__ == "__main__":
	main()








