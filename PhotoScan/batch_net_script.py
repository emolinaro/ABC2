import PhotoScan

path = PhotoScan.app.getOpenFileName("Specify path to the document:")
root = PhotoScan.app.getExistingDirectory("Specify network root path:")

doc = PhotoScan.Document()
doc.open(path)
chunk = doc.chunk
client = PhotoScan.NetworkClient()

tasks = list()

### matching photos...multiple nodes and GPU acceleration

task = PhotoScan.Tasks.MatchPhotos()
task.downscale = int(PhotoScan.HighAccuracy)
task.keypoint_limit = 40000
task.tiepoint_limit = 10000
task.select_pairs = int(PhotoScan.NoPreselection)
network_task = PhotoScan.NetworkTask()
network_task.name = task.name
network_task.params = task.encode()
network_task.frames.append((chunk.key, 0))
tasks.append(network_task)
doc.save(path)

### photos alignment...only on 1 node and no GPU acceleration

task = PhotoScan.Tasks.AlignCameras()
network_task = PhotoScan.NetworkTask()
network_task.name = task.name
network_task.params = task.encode()
network_task.chunks.append(chunk.key) #such approach should be used for AlignCameras and OptimizeCameras tasks
network_task.network_distribute = True
tasks.append(network_task)
doc.save(path)

### build depth maps...multiple nodes and GPU acceleration

task = PhotoScan.Tasks.BuildDepthMaps()
task.downscale = int(PhotoScan.MediumQuality)
task.filter_mode = PhotoScan.FilterMode.AggressiveFiltering
task.reuse_depth = True  #  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
network_task = PhotoScan.NetworkTask()
network_task.name = task.name
network_task.params = task.encode()
network_task.frames.append((chunk.key, 0))
network_task.network_distribute = True
tasks.append(network_task)
doc.save(path)

### build dense cloud (filtering the depth maps)...multiple nodes and no GPU acceleration

task = PhotoScan.Tasks.buildDenseCloud()
task.keep_depth = True   #  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
network_task = PhotoScan.NetworkTask()
network_task.name = task.name
network_task.params = task.encode()
network_task.frames.append((chunk.key, 0))
network_task.network_distribute = True
tasks.append(network_task)
doc.save(path)

### build mesh...multiple nodes?? and no GPU acceleration

task = PhotoScan.Tasks.buildModel()
task.surface = PhotoScan.Arbitrary
task.face_count = PhotoScan.HighFaceCount
task.interpolation = PhotoScan.EnabledInterpolation
task.downscale = int(PhotoScan.MediumQuality)
task.source = PhotoScan.DataSource.DenseCloudData
task.keep_depth=True     #  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
task.reuse_depth=True    #  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
network_task = PhotoScan.NetworkTask()
network_task.name = task.name
network_task.params = task.encode()
network_task.frames.append((chunk.key, 0))
network_task.network_distribute = True
tasks.append(network_task)
doc.save(path)

### build UV map...multiple nodes?? and no GPU acceleration

task = PhotoScan.Tasks.buildUV()
task.mapping = PhotoScan.GenericMapping
task.count = 1
network_task = PhotoScan.NetworkTask()
network_task.name = task.name
network_task.params = task.encode()
network_task.frames.append((chunk.key, 0))
network_task.network_distribute = True
tasks.append(network_task)
doc.save(path)

### build texture...multiple nodes?? and no GPU acceleration

task = PhotoScan.Tasks.buildTexture()
task.blending = PhotoScan.MosaicBlending
task.size = 2048
network_task = PhotoScan.NetworkTask()
network_task.name = task.name
network_task.params = task.encode()
network_task.frames.append((chunk.key, 0))
network_task.network_distribute = True
tasks.append(network_task)
doc.save(path)

### export model

model_file = path[:-4] + "-model.ply"
task = PhotoScan.Tasks.exportModel()
task.path = model_file
task.format = PhotoScan.ModelFormatPLY
network_task = PhotoScan.NetworkTask()
network_task.name = task.name
network_task.params = task.encode()
tasks.append(network_task)

model_file = path[:-4] + "-model.obj"
task = PhotoScan.Tasks.exportModel()
task.path = model_file
task.format = PhotoScan.ModelFormatOBJ
network_task = PhotoScan.NetworkTask()
network_task.name = task.name
network_task.params = task.encode()
tasks.append(network_task)

model_file = path[:-4] + "-model.pdf"
task = PhotoScan.Tasks.exportModel()
task.path = model_file
task.format = PhotoScan.ModelFormatPDF
network_task = PhotoScan.NetworkTask()
network_task.name = task.name
network_task.params = task.encode()
tasks.append(network_task)

### export report 

model_file = path[:-4] + "-report.pdf"
description = " "  # add a description 
title = "REPORT"
task = PhotoScan.Tasks.exportReport()
task.path = model_file
task.title=title
task.description = description
task.page_numbers = 1  # add page numbers


client.connect('172.24.0.5', 5840) #server ip
batch_id = client.createBatch(path[len(root):], tasks)
client.resumeBatch(batch_id)