#############################################################################
#############################################################################
### PhotoScan v1.4 Task Network Processing
### 
### Author:         Emiliano Molinaro <molinaro@imada.sdu.dk>
### Institution:    SDU eScience Center
### Date:           20-01-2019
#
# The list of the tasks that support the fine level task subdistribution is: 
# MatchPhotos, AlignCameras, BuildDepthMaps, BuildDenseCloud, BuildTiledModel, 
# BuildDem, BuildOrthomosaic
#
###
#############################################################################
#############################################################################


import PhotoScan

path = PhotoScan.app.getOpenFileName("Specify path to the document:")
root = PhotoScan.app.getExistingDirectory("Specify network root path:")

doc = PhotoScan.Document()
doc.open(path)
chunk = doc.chunk
client = PhotoScan.NetworkClient()

tasks = list()

#############################################################################
## 1 ## matching photos...multiple nodes and GPU acceleration
#############################################################################

task = PhotoScan.Tasks.MatchPhotos()
task.downscale = int(PhotoScan.HighestAccuracy)
task.keypoint_limit = 40000
task.tiepoint_limit = 10000
task.filter_mask = False
task.preselection_generic = True
task.preselection_reference = True
task.network_distribute = True
network_task = PhotoScan.NetworkTask()
network_task.name = task.name
network_task.params = task.encode()
network_task.frames.append((chunk.key, 0))
tasks.append(network_task)

#############################################################################
## 2 ## photos alignment...multiple nodes and no GPU acceleration
#############################################################################

task = PhotoScan.Tasks.AlignCameras()
task.network_distribute = True
network_task = PhotoScan.NetworkTask()
network_task.name = task.name
network_task.params = task.encode()
network_task.chunks.append(chunk.key) #such approach should be used for AlignCameras and OptimizeCameras tasks
tasks.append(network_task)

#############################################################################
## 3 ## build depth maps...multiple nodes and GPU acceleration
#############################################################################

task = PhotoScan.Tasks.BuildDepthMaps()
task.downscale = int(PhotoScan.HighQuality)
task.filter_mode = PhotoScan.FilterMode.AggressiveFiltering
task.reuse_depth = True  
task.network_distribute = True
network_task = PhotoScan.NetworkTask()
network_task.name = task.name
network_task.params = task.encode()
network_task.frames.append((chunk.key, 0))
tasks.append(network_task)

#############################################################################
## 4 ## build dense cloud (filtering the depth maps)...multiple nodes and no GPU acceleration
#############################################################################

task = PhotoScan.Tasks.BuildDenseCloud()
task.store_depth = True   
task.network_distribute = True
network_task = PhotoScan.NetworkTask()
network_task.name = task.name
network_task.params = task.encode()
network_task.frames.append((chunk.key, 0))
tasks.append(network_task)

#############################################################################
## 5 ## build mesh...only one node and no GPU acceleration
#############################################################################

task = PhotoScan.Tasks.BuildModel()
task.surface_type = PhotoScan.SurfaceType.Arbitrary
task.face_count = PhotoScan.FaceCount.HighFaceCount
task.interpolation = PhotoScan.EnabledInterpolation
task.downscale = int(PhotoScan.HighQuality)
task.source_data = PhotoScan.DataSource.DenseCloudData
task.store_depth=True    
task.reuse_depth=True    
task.network_distribute = True
network_task = PhotoScan.NetworkTask()
network_task.name = task.name
network_task.params = task.encode()
network_task.frames.append((chunk.key, 0))
tasks.append(network_task)

#############################################################################
## 6 ## build UV map...only one nd no GPU acceleration
#############################################################################

task = PhotoScan.Tasks.BuildUV()
task.mapping_mode = PhotoScan.MappingMode.GenericMapping
task.texture_count = 1
network_task = PhotoScan.NetworkTask()
network_task.name = task.name
network_task.params = task.encode()
network_task.frames.append((chunk.key, 0))
tasks.append(network_task)

#############################################################################
## 7 ## build texture...only one node and no GPU acceleration
#############################################################################

task = PhotoScan.Tasks.BuildTexture()
task.blending_mode = PhotoScan.BlendingMode.MosaicBlending
task.texture_size = 2048
network_task = PhotoScan.NetworkTask()
network_task.name = task.name
network_task.params = task.encode()
network_task.frames.append((chunk.key, 0))
tasks.append(network_task)
doc.save(path)

#############################################################################
## 8 ## export model (PLY, OBJ, PDF)
#############################################################################

model_file = path[:-4] + "-model.ply"
task = PhotoScan.Tasks.ExportModel()
task.export_texture = True
task.path = model_file
task.format = PhotoScan.ModelFormat.ModelFormatPLY
network_task = PhotoScan.NetworkTask()
network_task.name = task.name
network_task.params = task.encode()
network_task.frames.append((chunk.key, 0))
tasks.append(network_task)

model_file = path[:-4] + "-model.obj"
task = PhotoScan.Tasks.ExportModel()
task.export_texture = True
task.path = model_file
task.format = PhotoScan.ModelFormat.ModelFormatOBJ
network_task = PhotoScan.NetworkTask()
network_task.name = task.name
network_task.params = task.encode()
network_task.frames.append((chunk.key, 0))
tasks.append(network_task)

model_file = path[:-4] + "-model.pdf"
task = PhotoScan.Tasks.ExportModel()
task.export_texture = True
task.path = model_file
task.format = PhotoScan.ModelFormat.ModelFormatPDF
network_task = PhotoScan.NetworkTask()
network_task.name = task.name
network_task.params = task.encode()
network_task.frames.append((chunk.key, 0))
tasks.append(network_task)

#############################################################################
## 9 ## export report 
#############################################################################

report_file = path[:-4] + "-report.pdf"
description = " "  # add a description 
title = "REPORT"
task = PhotoScan.Tasks.ExportReport()
task.path = report_file
task.title = title
task.description = description
task.page_numbers = True  # add page numbers
network_task = PhotoScan.NetworkTask()
network_task.name = task.name
network_task.params = task.encode()
network_task.frames.append((chunk.key, 0))
tasks.append(network_task)

#############################################################################
## 10 ## distribute the tasks over the network
#############################################################################

client.connect('172.24.0.5', 5840) #server ip
batch_id = client.createBatch(path[len(root):], tasks)
client.resumeBatch(batch_id)

print("...")
print("Batch process distributed over the network...")
