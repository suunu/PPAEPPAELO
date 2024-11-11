import mss
import numpy as np
import cv2
import pyautogui
import math
from concurrent.futures import ThreadPoolExecutor


# 특정 영역 캡처 함수 (사진 저장 안 함)
def capture_specific_region(region):
    with mss.mss() as sct:
        screenshot = np.array(sct.grab(region))  # 캡처
        image = screenshot[:, :, :3]  # BGRA -> BGR 변환 (알파 채널 제외)
        return image  # 이미지 반환


# 거리 계산 함수 (유클리드 거리)
def calculate_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


# 템플릿 매칭 및 클릭 함수 (발견 즉시 클릭)
def find_and_click(template_path, screen, region, threshold=0.9, last_clicked_position=None, click_threshold=50):
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)  # 템플릿을 BGR 형식으로 로드 (JPEG 처리)
    if template is None:
        print(f"템플릿 이미지를 로드할 수 없습니다: {template_path}")
        return last_clicked_position

    # 화면에서 템플릿 매칭 수행 (스케일 1.0)
    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        print(f"빼빼로 발견!!! - 위치: {max_loc}, 매칭값: {max_val:.4f}")
        
        # 클릭할 위치 계산
        x, y = max_loc
        h, w, _ = template.shape
        center_x = x/2 + w / 4 + region['left']
        center_y = y/2 + h / 4 + region['top']

        # 직전 클릭 위치와의 거리 계산
        if last_clicked_position is not None:
            distance = calculate_distance((center_x, center_y), last_clicked_position)
            print(f"거리: {distance}")

            # 거리 threshold 이내면 클릭하지 않음
            if distance < click_threshold:
                print(f"직전 클릭 위치와 너무 가까워서 클릭을 건너뜁니다. 위치: ({center_x}, {center_y})")
                return last_clicked_position

        # 클릭
        pyautogui.moveTo(center_x, center_y, duration=0)
        pyautogui.click()
        print(f"클릭 완료 - 위치: ({center_x}, {center_y})")
        
        # 직전 클릭 위치 업데이트
        return (center_x, center_y)

    else:
        print("빼빼로를 찾지 못했습니다.")
        return last_clicked_position


# 캡처와 템플릿 매칭을 병렬로 수행
def continuously_find_and_click_in_region(template_path, region, threshold=0.9, num_workers=4):
    last_clicked_position = None  # 직전 클릭 위치 추적
    try:
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            while True:
                # 병렬로 캡처 작업 수행
                future = executor.submit(capture_specific_region, region)
                screen = future.result()

                # 캡처된 이미지가 있을 경우 템플릿 매칭 수행
                last_clicked_position = find_and_click(template_path, screen, region, threshold, last_clicked_position)

    except KeyboardInterrupt:
        print("프로그램을 종료합니다.")


# 메인 실행
if __name__ == "__main__":
    # 템플릿 이미지 경로
    template_path = "template.jpeg"  # 템플릿 이미지를 JPEG로 준비하세요
    # 캡처할 특정 영역 정의
    region = {"top": 200, "left": 1500, "width": 400, "height": 800}  # 모니터 좌표

    # 더 많은 워커로 병렬화 수준을 높여 속도 최적화
    continuously_find_and_click_in_region(template_path, region, threshold=0.98, num_workers=20)
