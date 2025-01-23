import cv2, os

for image_name in os.listdir(r'tests\test_samples/'):
    if image_name.split('.')[-1] != 'png': continue
    image = cv2.imread(r'tests\test_samples/'+image_name)

    cv2.imwrite(r'tests\test_samples/'+''.join(image_name.split('.')[0:-1])+'.jpg', image, [int(cv2.IMWRITE_JPEG_QUALITY), 65])
    os.remove(r'tests\test_samples/'+image_name)