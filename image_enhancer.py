import cv2
import numpy as np
import os

def enhance_image_ai(image_path: str, output_path: str) -> bool:
    """
    Applies algorithms to perform AI Smart Enhancement.
    The goal is to automatically enhance diagnostic clarity using:
    - Adaptive Histogram Equalization (CLAHE) for Contrast Enhancement
    - Non-Local Means Denoising for Noise Reduction
    - Unsharp Masking for Edge Sharpening
    """
    if not os.path.exists(image_path):
        return False

    # Read the image
    img = cv2.imread(image_path)
    if img is None:
        return False

    # Convert to grayscale (medical images work best this way)
    # If the original image had colors (like some overlays), we might want to keep the hue.
    # But usually, X-Rays / Ultrasounds are grayscale.
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 1. Noise Reduction
    # Non-local means denoising is excellent for medical images
    denoised = cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)

    # 2. Contrast Enhancement using CLAHE
    # CLAHE prevents over-amplification of noise compared to standard histogram equalization
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
    contrast_enhanced = clahe.apply(denoised)

    # 3. Edge Sharpening (Unsharp Masking)
    gaussian_blur = cv2.GaussianBlur(contrast_enhanced, (0, 0), 2.0)
    # unsharp = original + (original - blurred) * amount
    # Maximize the weight (4.0 & -3.0) to give extremely prominent structural sharpening 
    sharpened = cv2.addWeighted(contrast_enhanced, 4.0, gaussian_blur, -3.0, 0)

    # We convert back to BGR so it saves in standard format correctly
    final_img = cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)

    # Save to output_path
    cv2.imwrite(output_path, final_img)

    return True

def manual_enhance_image(image_path: str, output_path: str, noise_reduction: float, contrast: float, sharpening: float) -> bool:
    """
    Applies algorithms for Manual Enhancement based on user sliders.
    Inputs are expected as percentages or normalized values, e.g., 0 to 100.
    """
    if not os.path.exists(image_path):
        return False

    img = cv2.imread(image_path)
    if img is None:
        return False

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    enhanced = gray.copy()

    # 1. Manual Noise Reduction (simulate using filter)
    if noise_reduction > 0:
        h_val = float(noise_reduction) * 0.2  # scale it down to appropriate parameter
        enhanced = cv2.fastNlMeansDenoising(enhanced, None, h=h_val, templateWindowSize=7, searchWindowSize=21)

    # 2. Manual Contrast
    if contrast != 0:
        # Scale contrast typical alpha range [1.0, 3.0]
        # contrast is e.g., -100 to 100
        alpha = 1.0 + (contrast / 100.0) 
        alpha = max(0.1, alpha)  # prevent completely zero contrast
        enhanced = cv2.convertScaleAbs(enhanced, alpha=alpha, beta=0)

    # 3. Manual Sharpening
    if sharpening > 0:
        gaussian_blur = cv2.GaussianBlur(enhanced, (0, 0), 2.0)
        weight = float(sharpening) / 100.0
        enhanced = cv2.addWeighted(enhanced, 1.0 + weight, gaussian_blur, -weight, 0)

    final_img = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
    cv2.imwrite(output_path, final_img)
    return True
