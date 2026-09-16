"""
Folder Monitor - Klasör değişikliklerini izle
"""

import logging
import time
from pathlib import Path
from typing import Callable, Dict, Any
from threading import Thread
import os

logger = logging.getLogger(__name__)


class FolderMonitor:
    """Klasördeki video dosyaların izleme"""
    
    def __init__(self, folder_path: str, config: Dict[str, Any], callback: Callable):
        self.folder_path = Path(folder_path)
        self.config = config
        self.callback = callback
        self.is_running = False
        self.thread = None
        self.processed_files = set()
        self.video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv'}
    
    def start(self):
        """Monitörü başlat"""
        if self.is_running:
            logger.warning("Monitör zaten çalışıyor")
            return
        
        self.is_running = True
        self.thread = Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        logger.info(f"📁 Klasör monitörü başlatıldı: {self.folder_path}")
    
    def stop(self):
        """Monitörü durdur"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("⏹️ Klasör monitörü durduruldu")
    
    def _monitor_loop(self):
        """Monitörü loop'ta çalıştır"""
        check_interval = self.config.get('monitor', {}).get('check_interval', 5)
        
        while self.is_running:
            try:
                self._check_folder()
                time.sleep(check_interval)
            except Exception as e:
                logger.error(f"Monitör hatası: {str(e)}")
                time.sleep(check_interval)
    
    def _check_folder(self):
        """Klasörü kontrol et"""
        if not self.folder_path.exists():
            logger.warning(f"Klasör bulunamadı: {self.folder_path}")
            return
        
        # Tüm video dosyalarını listele
        for file_path in self.folder_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.video_extensions:
                # Dosya henüz işlenmediyse
                if str(file_path) not in self.processed_files:
                    # Dosya tamamen yazıldığını kontrol et
                    if self._is_file_ready(file_path):
                        self.processed_files.add(str(file_path))
                        logger.info(f"📹 Yeni video bulundu: {file_path.name}")
                        self.callback(str(file_path))
    
    def _is_file_ready(self, file_path: Path) -> bool:
        """Dosya yazılmaya hazır mı?"""
        try:
            # Dosya boyutunu kontrol et
            size1 = file_path.stat().st_size
            time.sleep(1)  # 1 saniye bekle
            size2 = file_path.stat().st_size
            
            # Boyut değişmemişse dosya yazılmış demektir
            return size1 == size2 and size1 > 0
        except Exception as e:
            logger.error(f"Dosya kontrol hatası: {str(e)}")
            return False