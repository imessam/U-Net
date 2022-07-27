import torch
import sys
import cv2
import numpy as np
from torchvision import transforms
from PIL import Image
from dataset import CustomNormalizeTransform
from model import *
from utils import *

values2classes,classes2values,class2idx,idx2class = readClassLabels()

def run(image_path,weights_path):
    
    
    # Load Model
    model = UNET(noClasses=32)
    model.load_state_dict(torch.load(weights_path))
    model.eval()
    
    
    # Read and process image.
    image_transforms = transforms.Compose([
        transforms.Resize((572,572)),
        transforms.ToTensor(),
        CustomNormalizeTransform()
    ])
    
    image = Image.open(image_path)
    image_processed = image_transforms(image)
    image = torch.tensor(np.array(image).transpose(2,0,1))
    
    
    # Generate the segmented image.
    preds = model(image_processed.unsqueeze(0)).detach()
    preds_mask = torch.softmax(preds,dim = 1)
    preds_mask = torch.argmax(preds_mask.squeeze(0),dim = 0)
    preds_unmasked = unmask(preds_mask,classes2values)

    image = cv2.cvtColor(transforms.Resize((388,388))(image).numpy().transpose(1,2,0).astype(np.uint8),cv2.COLOR_BGR2RGB)
    segmented_image = cv2.cvtColor(preds_unmasked.cpu().numpy().transpose(1,2,0).astype(np.uint8),cv2.COLOR_BGR2RGB)
    
    numpy_horizontal = np.hstack((image, segmented_image))
    
    
    #Show the segmented image.
    cv2.imshow('Display',numpy_horizontal)

    cv2.namedWindow("Display", cv2.WINDOW_FREERATIO)

    # Waiting 0ms for user to press any key
    cv2.waitKey(0)

    # Using cv2.destroyAllWindows() to destroy
    # all created windows open on screen
    cv2.destroyAllWindows()
    
    
    
if __name__ == "__main__":
    
    run(*sys.argv[1:])
    
    
    
