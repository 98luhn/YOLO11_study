"""
다중 레이어 객체 검출 테스트 스크립트
샘플 이미지를 다운로드하고 다중 레이어 검출을 테스트
"""

import os
import urllib.request
from pathlib import Path
from multi_layer_detector import MultiLayerObjectDetector
import cv2
import matplotlib.pyplot as plt


def download_sample_images():
    """
    테스트용 샘플 이미지 다운로드
    """
    sample_dir = Path("sample_images")
    sample_dir.mkdir(exist_ok=True)
    
    # 다양한 복잡도의 샘플 이미지
    samples = [
        {
            'name': 'street_scene.jpg',
            'url': 'https://ultralytics.com/images/bus.jpg',
            'description': '거리 장면 (차량, 사람 등)'
        },
        {
            'name': 'crowd.jpg',
            'url': 'https://ultralytics.com/images/zidane.jpg',
            'description': '사람이 많은 장면'
        },
        {
            'name': 'indoor.jpg',
            'url': 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=640',
            'description': '실내 장면'
        }
    ]
    
    print("📥 샘플 이미지 다운로드 중...")
    downloaded = []
    
    for sample in samples:
        output_path = sample_dir / sample['name']
        
        if output_path.exists():
            print(f"  ✓ {sample['name']} (이미 존재)")
            downloaded.append(str(output_path))
        else:
            try:
                urllib.request.urlretrieve(sample['url'], output_path)
                print(f"  ✓ {sample['name']} - {sample['description']}")
                downloaded.append(str(output_path))
            except Exception as e:
                print(f"  ✗ {sample['name']} 다운로드 실패: {e}")
    
    return downloaded


def test_multi_layer_detection(image_path):
    """
    다중 레이어 검출 테스트
    
    Args:
        image_path: 테스트 이미지 경로
    """
    print(f"\n🔍 테스트 이미지: {Path(image_path).name}")
    print("-" * 60)
    
    # 검출기 생성
    detector = MultiLayerObjectDetector()
    
    # 다중 레이어 검출 수행
    results = detector.detect_multi_layer(image_path, visualize_layers=True)
    
    if results:
        print("\n📊 테스트 결과:")
        print(f"  • 총 레이어 수: {results['total_layers']}")
        print(f"  • 최종 검출 객체 수: {len(results['final_detections'])}")
        
        # 레이어별 성능 비교
        print("\n  레이어별 검출 성능:")
        for layer_result in results['layer_results']:
            print(f"    - {layer_result['layer_name']}: {layer_result['count']}개")
        
        # 결과 저장
        output_json = f"test_results_{Path(image_path).stem}.json"
        detector.save_results(results, output_json)
        print(f"\n  💾 결과 저장: {output_json}")
    
    return results


def compare_with_single_model(image_path):
    """
    단일 모델과 다중 레이어 모델 비교
    
    Args:
        image_path: 테스트 이미지 경로
    """
    print(f"\n📊 단일 모델 vs 다중 레이어 비교")
    print("-" * 60)
    
    from ultralytics import YOLO
    import time
    
    # 1. 단일 모델 (YOLOv11m)
    print("1️⃣ 단일 모델 (YOLOv11m) 테스트...")
    single_model = YOLO('yolo11m.pt')
    
    start_time = time.time()
    single_results = single_model(image_path, conf=0.5, verbose=False)
    single_time = time.time() - start_time
    
    single_count = len(single_results[0].boxes) if single_results[0].boxes else 0
    print(f"   • 검출 수: {single_count}개")
    print(f"   • 처리 시간: {single_time:.2f}초")
    
    # 2. 다중 레이어 모델
    print("\n2️⃣ 다중 레이어 모델 테스트...")
    detector = MultiLayerObjectDetector()
    
    start_time = time.time()
    multi_results = detector.detect_multi_layer(image_path, visualize_layers=False)
    multi_time = time.time() - start_time
    
    multi_count = len(multi_results['final_detections'])
    print(f"   • 검출 수: {multi_count}개")
    print(f"   • 처리 시간: {multi_time:.2f}초")
    
    # 3. 비교 결과
    print("\n📈 비교 결과:")
    print(f"   • 검출 개수 차이: {multi_count - single_count}개 ({(multi_count/max(single_count, 1) - 1)*100:.1f}%)")
    print(f"   • 처리 시간 차이: {multi_time - single_time:.2f}초")
    
    # 시각화
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    # 검출 수 비교
    axes[0].bar(['단일 모델', '다중 레이어'], [single_count, multi_count])
    axes[0].set_ylabel('검출 객체 수')
    axes[0].set_title('검출 성능 비교')
    
    # 처리 시간 비교
    axes[1].bar(['단일 모델', '다중 레이어'], [single_time, multi_time])
    axes[1].set_ylabel('처리 시간 (초)')
    axes[1].set_title('처리 속도 비교')
    
    plt.suptitle(f'단일 vs 다중 레이어 모델 비교 - {Path(image_path).name}')
    plt.tight_layout()
    
    output_path = f"comparison_{Path(image_path).stem}.png"
    plt.savefig(output_path)
    print(f"\n💾 비교 차트 저장: {output_path}")
    plt.show()


def run_comprehensive_test():
    """
    종합 테스트 실행
    """
    print("="*60)
    print("🎯 다중 레이어 객체 검출 종합 테스트")
    print("="*60)
    
    # 1. 샘플 이미지 다운로드
    sample_images = download_sample_images()
    
    if not sample_images:
        print("❌ 샘플 이미지를 다운로드할 수 없습니다.")
        return
    
    # 2. 각 이미지에 대해 테스트
    all_results = []
    
    for image_path in sample_images:
        # 다중 레이어 검출 테스트
        results = test_multi_layer_detection(image_path)
        all_results.append(results)
        
        # 단일 모델과 비교 (첫 번째 이미지만)
        if image_path == sample_images[0]:
            compare_with_single_model(image_path)
    
    # 3. 종합 통계
    print("\n" + "="*60)
    print("📊 종합 테스트 결과")
    print("="*60)
    
    total_detections = sum(len(r['final_detections']) for r in all_results if r)
    avg_detections = total_detections / len(all_results) if all_results else 0
    
    print(f"• 테스트 이미지 수: {len(sample_images)}")
    print(f"• 총 검출 객체 수: {total_detections}")
    print(f"• 평균 검출 객체 수: {avg_detections:.1f}")
    
    # 클래스 분포
    class_distribution = {}
    detector = MultiLayerObjectDetector()
    
    for results in all_results:
        if results and detector.class_names:
            for det in results['final_detections']:
                class_name = detector.class_names.get(det['class_id'], 'unknown')
                class_distribution[class_name] = class_distribution.get(class_name, 0) + 1
    
    if class_distribution:
        print("\n• 전체 클래스 분포:")
        for class_name, count in sorted(class_distribution.items(), 
                                       key=lambda x: x[1], reverse=True)[:10]:
            print(f"  - {class_name}: {count}개")
    
    print("\n✅ 종합 테스트 완료!")


def test_custom_image():
    """
    사용자 지정 이미지 테스트
    """
    print("="*60)
    print("🎯 사용자 이미지 다중 레이어 검출 테스트")
    print("="*60)
    
    image_path = input("\n이미지 경로를 입력하세요: ").strip()
    
    if not os.path.exists(image_path):
        print(f"❌ 파일을 찾을 수 없습니다: {image_path}")
        return
    
    # 다중 레이어 검출 수행
    detector = MultiLayerObjectDetector()
    results = detector.detect_multi_layer(image_path, visualize_layers=True)
    
    # 결과 저장 옵션
    save_option = input("\n결과를 저장하시겠습니까? (y/n): ").strip().lower()
    if save_option == 'y':
        output_path = f"custom_results_{Path(image_path).stem}.json"
        detector.save_results(results, output_path)
        print(f"✅ 결과 저장: {output_path}")
    
    print("\n✅ 테스트 완료!")


def main():
    """
    메인 테스트 함수
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='다중 레이어 객체 검출 테스트')
    parser.add_argument('--comprehensive', action='store_true', 
                       help='종합 테스트 실행')
    parser.add_argument('--custom', action='store_true',
                       help='사용자 지정 이미지 테스트')
    parser.add_argument('-i', '--image', 
                       help='특정 이미지 경로 지정')
    
    args = parser.parse_args()
    
    if args.comprehensive:
        run_comprehensive_test()
    elif args.custom:
        test_custom_image()
    elif args.image:
        test_multi_layer_detection(args.image)
    else:
        # 기본: 종합 테스트
        run_comprehensive_test()


if __name__ == "__main__":
    main()