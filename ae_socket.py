"""
After Effects Socket Controller - After Effects'e Socket üzerinden bağlan
"""

import logging
import socket
import time
from typing import Dict, Any, Optional
import json

logger = logging.getLogger(__name__)


class AESocketController:
    """After Effects'e Socket üzerinden bağlantı"""
    
    def __init__(self, host: str = 'localhost', port: int = 4444):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
    
    def connect(self) -> bool:
        """After Effects'e bağlan"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            logger.info(f"✅ After Effects'e bağlandı: {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Bağlantı hatası: {str(e)}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Bağlantıyı kapat"""
        if self.socket:
            try:
                self.socket.close()
                self.connected = False
                logger.info("⏹️ After Effects bağlantısı kapatıldı")
            except Exception as e:
                logger.error(f"Bağlantı kapatma hatası: {str(e)}")
    
    def send_command(self, command: str) -> Optional[str]:
        """After Effects'e komut gönder"""
        if not self.connected:
            logger.error("After Effects'e bağlı değiliz")
            return None
        
        try:
            self.socket.send(command.encode('utf-8'))
            response = self.socket.recv(4096).decode('utf-8')
            return response
        except Exception as e:
            logger.error(f"Komut gönderme hatası: {str(e)}")
            self.connected = False
            return None
    
    def create_project(self, project_name: str) -> bool:
        """Yeni proje oluştur"""
        command = f'app.newProject(); app.project.file = new File("{project_name}");'
        response = self.send_command(command)
        return response is not None
    
    def add_composition(self, comp_name: str, width: int, height: int, 
                       fps: float, duration: float) -> bool:
        """Composition ekle"""
        command = f"""app.project.items.addComp(
            \"{comp_name}\",
            {width},
            {height},
            1,
            {duration},
            {fps}
        );"""
        response = self.send_command(command)
        return response is not None
    
    def import_video(self, file_path: str) -> bool:
        """Video import et"""
        command = f'app.project.importFile(new File("{file_path}"));'
        response = self.send_command(command)
        return response is not None
    
    def apply_speed_ramp(self, layer_index: int, timestamp: float, 
                         start_speed: float, end_speed: float, duration: float) -> bool:
        """Speed ramp efekti uygula"""
        command = f"""var layer = app.project.activeItem.layers[{layer_index}];
layer.timeRemapEnabled = true;
layer.timeRemap.setValueAtTime({timestamp}, {timestamp} * {start_speed});
layer.timeRemap.setValueAtTime({timestamp} + {duration}, {timestamp} * {end_speed});"""
        response = self.send_command(command)
        return response is not None
