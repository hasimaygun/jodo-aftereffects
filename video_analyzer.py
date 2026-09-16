"""
Video Analyzer - Claude Vision ile video analizi
"""

import base64
import logging
import cv2
from pathlib import Path
from typing import Dict, List, Any
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class VideoAnalyzer:
    """Claude Vision kullanarak video analizi"""
    
    def __init__(self, config: dict):
        self.config = config
        self.client = Anthropic()
        self.api_key = config.get("anthropic_api_key")
        self.model = config.get("video_analysis", {}).get("model", "claude-3-5-sonnet-20241022")
        self.scene_types = config.get("video_analysis", {}).get("scene_types", [])
        self.frame_skip = config.get("video_processing", {}).get("frame_skip", 5)
    
    def extract_frames(self, video_path: str) -> List[tuple]:
        """Videodan çerçeveleri çıkart"""
        logger.info(f"📹 Video açılıyor: {video_path}")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Video açılamadı: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        logger.info(f"FPS: {fps}, Toplam Çerçeve: {total_frames}")
        
        frames = []
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Her N çerçevede bir al
            if frame_count % self.frame_skip == 0:
                timestamp = frame_count / fps
                frames.append((frame, timestamp))
            
            frame_count += 1
        
        cap.release()
        logger.info(f"✅ {len(frames)} çerçeve çıkartıldı")
        
        return frames
    
    def frame_to_base64(self, frame) -> str:
        """OpenCV frame'i base64'e dönüştür"""
        _, buffer = cv2.imencode('.jpg', frame)
        return base64.standard_b64encode(buffer).decode('utf-8')
    
    def analyze_frame(self, frame_b64: str, timestamp: float) -> Dict[str, Any]:
        """Tek bir çerçeveyi analiz et"""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": frame_b64,
                                },
                            },
                            {
                                "type": "text",
                                "text": """Bu video çerçevesini analiz et ve şunları belirle:
                                1. Sahne türü: action (hızlı/dinamik), dialogue (konuşma), nature (doğa), transition (geçiş), reaction (tepki)
                                2. Hareket seviyesi: low, medium, high
                                3. Önerilen hız: normal (1.0x), slow-mo (0.5x), fast (1.5x)
                                4. Açıklama: Kısa açıklama
                                
                                JSON formatında cevap ver:
                                {
                                    "scene_type": "...",
                                    "motion_level": "...",
                                    "suggested_speed": 1.0,
                                    "description": "..."
                                }"""
                            }
                        ],
                    }
                ],
            )
            
            # API yanıtını parse et
            response_text = message.content[0].text
            
            # JSON'u çıkart
            import json
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                analysis['timestamp'] = timestamp
                return analysis
            
            return {
                'timestamp': timestamp,
                'scene_type': 'unknown',
                'motion_level': 'medium',
                'suggested_speed': 1.0,
                'description': response_text
            }
            
        except Exception as e:
            logger.error(f"Çerçeve analizi hatası: {str(e)}")
            return {
                'timestamp': timestamp,
                'scene_type': 'unknown',
                'motion_level': 'medium',
                'suggested_speed': 1.0,
                'error': str(e)
            }
    
    def analyze(self, video_path: str) -> Dict[str, Any]:
        """Videoyu tam analiz et"""
        logger.info(f"🎬 Video analizi başlıyor: {video_path}")
        
        # Videoyu kontrol et
        if not Path(video_path).exists():
            raise FileNotFoundError(f"Video bulunamadı: {video_path}")
        
        # Çerçeveleri çıkart
        frames = self.extract_frames(video_path)
        
        if not frames:
            raise ValueError("Video'dan çerçeve çıkartılamadı")
        
        # Her çerçeveyi analiz et
        scenes = []
        for i, (frame, timestamp) in enumerate(frames):
            logger.info(f"Analiz ediliyor: {i+1}/{len(frames)} ({timestamp:.2f}s)")
            
            frame_b64 = self.frame_to_base64(frame)
            analysis = self.analyze_frame(frame_b64, timestamp)
            scenes.append(analysis)
        
        # Özet oluştur
        summary = self._create_summary(scenes)
        
        return {
            'video_path': video_path,
            'duration': frames[-1][1] if frames else 0,
            'frame_count': len(frames),
            'scenes': scenes,
            'summary': summary
        }
    
    def _create_summary(self, scenes: List[Dict]) -> Dict[str, Any]:
        """Analiz özeti oluştur"""
        if not scenes:
            return {}
        
        scene_types = {}
        motion_levels = {}
        speeds = []
        
        for scene in scenes:
            # Sahne türlerini say
            scene_type = scene.get('scene_type', 'unknown')
            scene_types[scene_type] = scene_types.get(scene_type, 0) + 1
            
            # Hareket seviyelerini say
            motion = scene.get('motion_level', 'medium')
            motion_levels[motion] = motion_levels.get(motion, 0) + 1
            
            # Hızları topla
            speed = scene.get('suggested_speed', 1.0)
            speeds.append(speed)
        
        return {
            'scene_types': scene_types,
            'motion_levels': motion_levels,
            'average_speed': sum(speeds) / len(speeds) if speeds else 1.0,
            'speed_range': (min(speeds), max(speeds)) if speeds else (1.0, 1.0),
            'total_scenes': len(scenes)
        }