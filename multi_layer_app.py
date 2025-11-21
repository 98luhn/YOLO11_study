"""
다중 레이어 객체 검출 실행 프로그램
사용자가 이미지를 입력하면 다중 레이어로 분석하여 결과를 제공
"""

import os
import sys
import cv2
import numpy as np
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from multi_layer_detector import MultiLayerObjectDetector
import json
from datetime import datetime
import threading


class MultiLayerDetectorGUI:
    """
    다중 레이어 객체 검출 GUI 애플리케이션
    """
    
    def __init__(self, root):
        """
        GUI 초기화
        """
        self.root = root
        self.root.title("🎯 다중 레이어 객체 검출 시스템")
        self.root.geometry("1400x900")
        
        # 스타일 설정
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # 변수 초기화
        self.current_image_path = None
        self.detector = None
        self.results = None
        
        # GUI 구성
        self.setup_gui()
        
        # 검출기 초기화 (백그라운드)
        self.init_detector_thread()
    
    def setup_gui(self):
        """
        GUI 레이아웃 설정
        """
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 상단 컨트롤 패널
        self.setup_control_panel(main_frame)
        
        # 중앙 이미지 표시 영역
        self.setup_image_area(main_frame)
        
        # 하단 결과 표시 영역
        self.setup_results_area(main_frame)
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
    
    def setup_control_panel(self, parent):
        """
        상단 컨트롤 패널 설정
        """
        control_frame = ttk.LabelFrame(parent, text="제어 패널", padding="10")
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 이미지 선택 버튼
        self.btn_select = ttk.Button(
            control_frame, 
            text="🖼️ 이미지 선택",
            command=self.select_image,
            width=20
        )
        self.btn_select.grid(row=0, column=0, padx=5, pady=5)
        
        # 검출 실행 버튼
        self.btn_detect = ttk.Button(
            control_frame,
            text="🔍 다중 레이어 검출 실행",
            command=self.run_detection,
            width=25,
            state='disabled'
        )
        self.btn_detect.grid(row=0, column=1, padx=5, pady=5)
        
        # 결과 저장 버튼
        self.btn_save = ttk.Button(
            control_frame,
            text="💾 결과 저장",
            command=self.save_results,
            width=15,
            state='disabled'
        )
        self.btn_save.grid(row=0, column=2, padx=5, pady=5)
        
        # 상태 표시
        self.status_label = ttk.Label(control_frame, text="준비 중...")
        self.status_label.grid(row=0, column=3, padx=20, pady=5)
        
        # 프로그레스 바
        self.progress = ttk.Progressbar(
            control_frame,
            mode='indeterminate',
            length=200
        )
        self.progress.grid(row=0, column=4, padx=5, pady=5)
    
    def setup_image_area(self, parent):
        """
        중앙 이미지 표시 영역 설정
        """
        # 이미지 프레임
        image_frame = ttk.LabelFrame(parent, text="이미지 뷰어", padding="10")
        image_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # 캔버스 (이미지 표시용)
        self.canvas = tk.Canvas(image_frame, bg='gray90')
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 스크롤바
        v_scrollbar = ttk.Scrollbar(image_frame, orient='vertical', command=self.canvas.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar = ttk.Scrollbar(image_frame, orient='horizontal', command=self.canvas.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        image_frame.columnconfigure(0, weight=1)
        image_frame.rowconfigure(0, weight=1)
    
    def setup_results_area(self, parent):
        """
        하단 결과 표시 영역 설정
        """
        results_frame = ttk.LabelFrame(parent, text="검출 결과", padding="10")
        results_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 결과 텍스트
        self.results_text = tk.Text(results_frame, height=10, width=80)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(results_frame, orient='vertical', command=self.results_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        results_frame.columnconfigure(0, weight=1)
    
    def init_detector_thread(self):
        """
        백그라운드에서 검출기 초기화
        """
        def init_detector():
            self.update_status("검출기 초기화 중...")
            self.progress.start()
            
            try:
                self.detector = MultiLayerObjectDetector()
                self.update_status("✅ 준비 완료")
                self.progress.stop()
            except Exception as e:
                self.update_status(f"❌ 초기화 실패: {e}")
                self.progress.stop()
        
        thread = threading.Thread(target=init_detector, daemon=True)
        thread.start()
    
    def select_image(self):
        """
        이미지 파일 선택
        """
        file_path = filedialog.askopenfilename(
            title="이미지 선택",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.current_image_path = file_path
            self.display_image(file_path)
            self.btn_detect.config(state='normal')
            self.update_status(f"이미지 로드: {Path(file_path).name}")
            self.results_text.delete(1.0, tk.END)
    
    def display_image(self, image_path):
        """
        이미지를 캔버스에 표시
        """
        # 이미지 로드
        image = Image.open(image_path)
        
        # 캔버스 크기에 맞게 리사이즈 (비율 유지)
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:
            image.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
        
        # PhotoImage로 변환
        self.photo = ImageTk.PhotoImage(image)
        
        # 캔버스에 표시
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
    
    def run_detection(self):
        """
        다중 레이어 검출 실행
        """
        if not self.current_image_path or not self.detector:
            messagebox.showwarning("경고", "이미지를 선택하고 검출기가 준비될 때까지 기다려주세요.")
            return
        
        # 검출 실행 (백그라운드)
        def detect():
            self.update_status("🔍 다중 레이어 검출 진행 중...")
            self.btn_detect.config(state='disabled')
            self.progress.start()
            
            try:
                # 검출 수행
                self.results = self.detector.detect_multi_layer(
                    self.current_image_path,
                    visualize_layers=True
                )
                
                # 결과 표시
                self.display_results()
                self.btn_save.config(state='normal')
                self.update_status("✅ 검출 완료")
                
            except Exception as e:
                messagebox.showerror("오류", f"검출 중 오류 발생:\n{e}")
                self.update_status(f"❌ 검출 실패: {e}")
            
            finally:
                self.btn_detect.config(state='normal')
                self.progress.stop()
        
        thread = threading.Thread(target=detect, daemon=True)
        thread.start()
    
    def display_results(self):
        """
        검출 결과를 텍스트 영역에 표시
        """
        if not self.results:
            return
        
        self.results_text.delete(1.0, tk.END)
        
        # 헤더
        self.results_text.insert(tk.END, "="*60 + "\n")
        self.results_text.insert(tk.END, "📊 다중 레이어 객체 검출 결과\n")
        self.results_text.insert(tk.END, "="*60 + "\n\n")
        
        # 레이어별 결과
        self.results_text.insert(tk.END, "레이어별 검출 수:\n")
        for layer_result in self.results['layer_results']:
            self.results_text.insert(tk.END, 
                f"  • {layer_result['layer_name']}: {layer_result['count']}개\n")
        
        # 최종 결과
        final_count = len(self.results['final_detections'])
        self.results_text.insert(tk.END, f"\n최종 통합 검출 수: {final_count}개\n\n")
        
        # 클래스별 분포
        if final_count > 0 and self.detector.class_names:
            class_counts = {}
            for det in self.results['final_detections']:
                class_name = self.detector.class_names.get(det['class_id'], 'unknown')
                class_counts[class_name] = class_counts.get(class_name, 0) + 1
            
            self.results_text.insert(tk.END, "클래스별 분포:\n")
            for class_name, count in sorted(class_counts.items(), 
                                           key=lambda x: x[1], reverse=True):
                self.results_text.insert(tk.END, f"  • {class_name}: {count}개\n")
        
        # 이미지 크기
        width, height = self.results['image_size']
        self.results_text.insert(tk.END, f"\n이미지 크기: {width} x {height}\n")
        self.results_text.insert(tk.END, f"총 레이어 수: {self.results['total_layers']}\n")
        
        self.results_text.insert(tk.END, "\n" + "="*60 + "\n")
    
    def save_results(self):
        """
        검출 결과 저장
        """
        if not self.results:
            messagebox.showwarning("경고", "저장할 결과가 없습니다.")
            return
        
        # 저장 경로 선택
        file_path = filedialog.asksaveasfilename(
            title="결과 저장",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.detector.save_results(self.results, file_path)
                messagebox.showinfo("성공", f"결과가 저장되었습니다:\n{file_path}")
                self.update_status(f"💾 저장 완료: {Path(file_path).name}")
            except Exception as e:
                messagebox.showerror("오류", f"저장 중 오류 발생:\n{e}")
    
    def update_status(self, message):
        """
        상태 메시지 업데이트
        """
        self.status_label.config(text=message)
        self.root.update_idletasks()


def create_simple_cli():
    """
    간단한 명령줄 인터페이스
    """
    print("="*60)
    print("🎯 다중 레이어 객체 검출 시스템")
    print("="*60)
    
    # 이미지 경로 입력
    while True:
        image_path = input("\n이미지 경로를 입력하세요 (종료: q): ").strip()
        
        if image_path.lower() == 'q':
            print("프로그램을 종료합니다.")
            break
        
        if not os.path.exists(image_path):
            print(f"❌ 파일을 찾을 수 없습니다: {image_path}")
            continue
        
        print("\n처리 중...")
        
        try:
            # 검출기 생성
            detector = MultiLayerObjectDetector()
            
            # 검출 수행
            results = detector.detect_multi_layer(image_path, visualize_layers=True)
            
            # 결과 저장 옵션
            save_option = input("\n결과를 JSON으로 저장하시겠습니까? (y/n): ").strip().lower()
            if save_option == 'y':
                output_path = f"results_{Path(image_path).stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                detector.save_results(results, output_path)
                print(f"✅ 결과 저장: {output_path}")
            
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
        
        print("\n" + "-"*60)


def main():
    """
    메인 실행 함수
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='다중 레이어 객체 검출 애플리케이션')
    parser.add_argument('--gui', action='store_true', help='GUI 모드로 실행')
    parser.add_argument('--cli', action='store_true', help='CLI 모드로 실행')
    parser.add_argument('-i', '--image', help='직접 이미지 경로 지정')
    
    args = parser.parse_args()
    
    if args.gui or (not args.cli and not args.image):
        # GUI 모드
        root = tk.Tk()
        app = MultiLayerDetectorGUI(root)
        root.mainloop()
    elif args.cli:
        # CLI 대화형 모드
        create_simple_cli()
    elif args.image:
        # 단일 이미지 처리
        detector = MultiLayerObjectDetector()
        results = detector.detect_multi_layer(args.image, visualize_layers=True)
        print("\n✅ 처리 완료!")


if __name__ == "__main__":
    main()