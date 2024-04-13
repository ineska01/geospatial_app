import rasterio

with rasterio.open(r"C:\Users\user\Desktop\frontend\data\ort_33.tif") as dataset:
    crs = dataset.crs
    transform = dataset.transform
    bounds = dataset.bounds

    print("CRS:", crs)
    print("Transform:", transform)
    print("Bounds:", bounds)
