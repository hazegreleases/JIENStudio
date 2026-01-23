import cv2
import albumentations as A
import numpy as np

def test_gaussian():
    # Create valid dummy image
    image = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
    
    # Defaults from the class
    blur_limit = 7
    sigma_limit_min = 0
    sigma_limit_max = 0
    
    limit = blur_limit if blur_limit % 2 != 0 else blur_limit + 1
    sigma = (sigma_limit_min, sigma_limit_max) if sigma_limit_max > 0 else (0.1, 2.0)
    
    print(f"Testing with blur_limit={limit}, sigma_limit={sigma}")
    
    transform = A.GaussianBlur(blur_limit=limit, sigma_limit=sigma, p=1.0)
    
    try:
        res = transform(image=image)['image']
        print(f"Min: {res.min()}, Max: {res.max()}, Mean: {res.mean()}")
        if res.mean() < 1:
            print("Output is BLACK!")
        else:
            print("Output seems OK.")
            
    except Exception as e:
        print(f"Error: {e}")

test_gaussian()
