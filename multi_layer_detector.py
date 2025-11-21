"""
다중 레이어 객체 인식 프로그램
여러 YOLO 모델을 계층적으로 사용하여 더 정밀한 객체 검출 수행
"""

import cv2
import numpy as np
from ultralytics import YOLO
import torch
from pathlib import Path
import argparse
import json
from typing import List, Dict, Tuple, Optional
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class MultiLayerObjectDetector:
    """
    다중 레이어 객체 검출기
    여러 모델을 계층적으로 사용하여 점진적으로 정밀한 검출 수행
    """
    
    def __init__(self, device='auto'):
        """
        초기화
        
        Args:
            device: 'auto', 'cpu', 'cuda'
        """
        if device == 'auto':
            self.device = 0 if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
            
        print(f"🚀 다중 레이어 객체 검출기 초기화")
        print(f"   Device: {self.device}")
        
        # 레이어별 모델 정의 (점진적으로 강력한 모델 사용)
        self.layers = self._initialize_layers()
        
        # 클래스 이름
        self.class_names = None
        
        # 색상 맵 (클래스별 색상)
        self.colors = None
        
    def _initialize_layers(self):
        """
        다중 레이어 초기화
        각 레이어는 다른 목적과 성능 특성을 가짐
        """
        layers = [
            {
                'name': 'Layer 1: 빠른 스캔',
                'model': YOLO('yolo11n.pt'),  # Nano - 가장 빠름
                'confidence': 0.3,
                'iou': 0.5,
                'purpose': '전체 이미지에서 빠르게 객체 영역 탐지',
                'color': (255, 0, 0)  # Red
            },
            {
                'name': 'Layer 2: 일반 검출',
                'model': YOLO('yolo11s.pt'),  # Small
                'confidence': 0.4,
                'iou': 0.45,
                'purpose': '중간 정확도로 객체 분류 및 위치 정제',
                'color': (0, 255, 0)  # Green
            },
            {
                'name': 'Layer 3: 정밀 검출',
                'model': YOLO('yolo11m.pt'),  # Medium
                'confidence': 0.5,
                'iou': 0.4,
                'purpose': '높은 정확도로 최종 검출 수행',
                'color': (0, 0, 255)  # Blue
            },
            {
                'name': 'Layer 4: 세그멘테이션',
                'model': YOLO('yolo11n-seg.pt'),  # Segmentation
                'confidence': 0.5,
                'iou': 0.4,
                'purpose': '픽셀 단위 정밀 분할',
                'color': (255, 255, 0)  # Yellow
            }
        ]
        
        print("\n📊 레이어 구성:")
        for i, layer in enumerate(layers, 1):
            print(f"   {layer['name']}: {layer['purpose']}")
            
        return layers
    
    def detect_multi_layer(self, image_path: str, visualize_layers: bool = True):
        """
        다중 레이어 객체 검출 수행
        
        Args:
            image_path: 입력 이미지 경로
            visualize_layers: 각 레이어 결과 시각화 여부
            
        Returns:
            최종 통합 검출 결과
        """
        print(f"\n🔍 이미지 분석 시작: {image_path}")
        
        # 이미지 로드
        image = cv2.imread(image_path)
        if image is None:
            print(f"❌ 이미지를 로드할 수 없습니다: {image_path}")
            return None
            
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width = image.shape[:2]
        
        # 각 레이어별 검출 결과 저장
        layer_results = []
        all_detections = []
        
        # 각 레이어 순차적으로 실행
        for i, layer in enumerate(self.layers):
            print(f"\n⚙️ {layer['name']} 실행 중...")
            
            try:
                # 검출 수행
                results = layer['model'](
                    image,
                    conf=layer['confidence'],
                    iou=layer['iou'],
                    verbose=False,
                    device=self.device
                )
                
                # 결과 파싱
                detections = self._parse_results(results[0], layer_idx=i)
                
                if detections:
                    layer_results.append({
                        'layer_name': layer['name'],
                        'layer_idx': i,
                        'detections': detections,
                        'count': len(detections)
                    })
                    all_detections.extend(detections)
                    
                    print(f"   ✓ {len(detections)}개 객체 검출")
                else:
                    print(f"   - 검출된 객체 없음")
                    
            except Exception as e:
                print(f"   ❌ 에러 발생: {e}")
                continue
        
        # 클래스 이름 설정 (첫 번째 성공한 모델에서)
        if self.class_names is None and layer_results:
            first_model = self.layers[layer_results[0]['layer_idx']]['model']
            self.class_names = first_model.names
            self.colors = self._generate_colors(len(self.class_names))
        
        # 검출 결과 통합 및 중복 제거
        final_detections = self._merge_detections(all_detections)
        
        # 시각화
        if visualize_layers:
            self._visualize_all_layers(image_rgb, layer_results, final_detections)
        
        # 결과 요약
        self._print_summary(layer_results, final_detections)
        
        return {
            'layer_results': layer_results,
            'final_detections': final_detections,
            'image_size': (width, height),
            'total_layers': len(self.layers)
        }
    
    def _parse_results(self, result, layer_idx: int):
        """
        YOLO 결과 파싱
        
        Args:
            result: YOLO 검출 결과
            layer_idx: 레이어 인덱스
            
        Returns:
            파싱된 검출 리스트
        """
        detections = []
        
        # 바운딩 박스 검출
        if hasattr(result, 'boxes') and result.boxes is not None:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                cls_id = int(box.cls[0])
                confidence = float(box.conf[0])
                
                detection = {
                    'bbox': [float(x1), float(y1), float(x2), float(y2)],
                    'class_id': cls_id,
                    'confidence': confidence,
                    'layer': layer_idx,
                    'type': 'box'
                }
                detections.append(detection)
        
        # 세그멘테이션 마스크 (Layer 4)
        if hasattr(result, 'masks') and result.masks is not None:
            for i, mask in enumerate(result.masks):
                if i < len(result.boxes):
                    box = result.boxes[i]
                    detection = detections[i] if i < len(detections) else {}
                    
                    # 마스크 폴리곤 추가
                    if hasattr(mask, 'xy') and len(mask.xy) > 0:
                        detection['mask'] = mask.xy[0].tolist()
                        detection['type'] = 'segment'
        
        return detections
    
    def _merge_detections(self, all_detections: List[Dict], iou_threshold: float = 0.5):
        """
        다중 레이어 검출 결과 통합 및 중복 제거
        
        Args:
            all_detections: 모든 레이어의 검출 결과
            iou_threshold: 중복 판단 IoU 임계값
            
        Returns:
            통합된 최종 검출 결과
        """
        if not all_detections:
            return []
        
        # 신뢰도 순으로 정렬
        sorted_detections = sorted(all_detections, key=lambda x: x['confidence'], reverse=True)
        
        # NMS (Non-Maximum Suppression) 적용
        final_detections = []
        
        for detection in sorted_detections:
            is_duplicate = False
            
            for final_det in final_detections:
                # 같은 클래스인 경우만 비교
                if detection['class_id'] == final_det['class_id']:
                    iou = self._calculate_iou(detection['bbox'], final_det['bbox'])
                    if iou > iou_threshold:
                        # 중복이면 더 높은 신뢰도의 레이어 정보 유지
                        if detection['confidence'] > final_det['confidence']:
                            final_det.update(detection)
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                final_detections.append(detection)
        
        return final_detections
    
    def _calculate_iou(self, box1: List[float], box2: List[float]) -> float:
        """
        두 바운딩 박스의 IoU 계산
        """
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        
        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0
    
    def _generate_colors(self, num_classes: int):
        """
        클래스별 색상 생성
        """
        colors = []
        for i in range(num_classes):
            hue = i / num_classes
            color = plt.cm.hsv(hue)[:3]
            colors.append(tuple(int(c * 255) for c in color))
        return colors
    
    def _visualize_all_layers(self, image: np.ndarray, layer_results: List[Dict], 
                             final_detections: List[Dict]):
        """
        모든 레이어 결과 시각화
        """
        num_layers = len(layer_results) + 1  # 레이어별 + 최종 통합
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()
        
        # 각 레이어 결과 시각화
        for i, layer_result in enumerate(layer_results):
            ax = axes[i]
            ax.imshow(image)
            ax.set_title(f"{layer_result['layer_name']} ({layer_result['count']}개 검출)")
            ax.axis('off')
            
            # 검출 결과 그리기
            for det in layer_result['detections']:
                self._draw_detection(ax, det, self.layers[i]['color'])
        
        # 최종 통합 결과 시각화
        ax = axes[len(layer_results)]
        ax.imshow(image)
        ax.set_title(f"최종 통합 결과 ({len(final_detections)}개 검출)")
        ax.axis('off')
        
        for det in final_detections:
            color = self.colors[det['class_id']] if self.colors else (0, 255, 0)
            self._draw_detection(ax, det, color, show_label=True)
        
        # 빈 subplot 숨기기
        for i in range(len(layer_results) + 1, len(axes)):
            axes[i].axis('off')
        
        plt.tight_layout()
        
        # 저장
        output_path = f"multi_layer_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(output_path, dpi=100, bbox_inches='tight')
        print(f"\n💾 결과 이미지 저장: {output_path}")
        
        plt.show()
    
    def _draw_detection(self, ax, detection: Dict, color: Tuple, show_label: bool = False):
        """
        검출 결과 그리기
        """
        bbox = detection['bbox']
        x1, y1, x2, y2 = bbox
        
        # 바운딩 박스
        rect = patches.Rectangle(
            (x1, y1), x2 - x1, y2 - y1,
            linewidth=2, edgecolor=color, facecolor='none', alpha=0.8
        )
        ax.add_patch(rect)
        
        # 라벨
        if show_label and self.class_names:
            class_name = self.class_names.get(detection['class_id'], 'unknown')
            label = f"{class_name}: {detection['confidence']:.2f}"
            ax.text(x1, y1 - 5, label, fontsize=10,
                   bbox=dict(boxstyle="round,pad=0.3", facecolor=color, alpha=0.7),
                   color='white')
        
        # 세그멘테이션 마스크 (있는 경우)
        if 'mask' in detection and detection.get('type') == 'segment':
            mask_points = np.array(detection['mask'])
            if len(mask_points) > 0:
                poly = patches.Polygon(mask_points, closed=True,
                                      edgecolor=color, facecolor=color,
                                      alpha=0.3, linewidth=2)
                ax.add_patch(poly)
    
    def _print_summary(self, layer_results: List[Dict], final_detections: List[Dict]):
        """
        검출 결과 요약 출력
        """
        print("\n" + "="*60)
        print("📊 다중 레이어 검출 결과 요약")
        print("="*60)
        
        # 레이어별 결과
        print("\n레이어별 검출 수:")
        for result in layer_results:
            print(f"  • {result['layer_name']}: {result['count']}개")
        
        # 최종 통합 결과
        print(f"\n최종 통합 검출 수: {len(final_detections)}개")
        
        # 클래스별 분포
        if self.class_names and final_detections:
            class_counts = {}
            for det in final_detections:
                class_name = self.class_names.get(det['class_id'], 'unknown')
                class_counts[class_name] = class_counts.get(class_name, 0) + 1
            
            print("\n클래스별 분포:")
            for class_name, count in sorted(class_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"  • {class_name}: {count}개")
        
        # 신뢰도 통계
        if final_detections:
            confidences = [det['confidence'] for det in final_detections]
            print(f"\n신뢰도 통계:")
            print(f"  • 평균: {np.mean(confidences):.3f}")
            print(f"  • 최대: {np.max(confidences):.3f}")
            print(f"  • 최소: {np.min(confidences):.3f}")
        
        print("="*60)
    
    def save_results(self, results: Dict, output_path: str = None):
        """
        검출 결과를 JSON 파일로 저장
        
        Args:
            results: 검출 결과
            output_path: 저장 경로
        """
        if output_path is None:
            output_path = f"detection_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # numpy 타입을 JSON 직렬화 가능한 형태로 변환
        def convert_to_serializable(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, (np.float32, np.float64)):
                return float(obj)
            elif isinstance(obj, (np.int32, np.int64)):
                return int(obj)
            elif isinstance(obj, dict):
                return {k: convert_to_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_serializable(item) for item in obj]
            return obj
        
        serializable_results = convert_to_serializable(results)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2, ensure_ascii=False)
        
        print(f"📄 결과 저장: {output_path}")


def main():
    """
    메인 실행 함수
    """
    parser = argparse.ArgumentParser(description='다중 레이어 객체 검출 프로그램')
    parser.add_argument('-i', '--image', required=True, help='입력 이미지 경로')
    parser.add_argument('-v', '--visualize', action='store_true', 
                       help='레이어별 시각화 (기본: True)', default=True)
    parser.add_argument('-s', '--save', action='store_true',
                       help='결과를 JSON으로 저장', default=False)
    parser.add_argument('--device', default='auto',
                       choices=['auto', 'cpu', 'cuda'],
                       help='실행 디바이스 (기본: auto)')
    
    args = parser.parse_args()
    
    print("="*60)
    print("🎯 다중 레이어 객체 검출 시스템")
    print("="*60)
    
    # 검출기 초기화
    detector = MultiLayerObjectDetector(device=args.device)
    
    # 다중 레이어 검출 수행
    results = detector.detect_multi_layer(
        image_path=args.image,
        visualize_layers=args.visualize
    )
    
    # 결과 저장
    if args.save and results:
        detector.save_results(results)
    
    print("\n✅ 처리 완료!")


if __name__ == "__main__":
    main()