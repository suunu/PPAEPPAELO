import mss
import numpy as np
import cv2

# 캡처할 화면 영역 설정
region = {"top": 200, "left": 1500, "width": 400, "height": 800}  # 필요에 맞게 조정하세요

# 특정 영역 캡처 함수
def capture_and_save(region, output_path="captured_region.jpeg"):
    with mss.mss() as sct:
        screenshot = np.array(sct.grab(region))
        image = screenshot[:, :, :3]

        # 이미지 저장 (JPEG 형식)
        cv2.imwrite(output_path, image, [int(cv2.IMWRITE_JPEG_QUALITY), 95])  # 품질 95로 설정
        print(f"이미지가 저장되었습니다: {output_path}")

# 캡처 및 저장
capture_and_save(region)
