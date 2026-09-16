"""
Process Manager - İşlem yönetimi
"""

import logging
from typing import Dict, List, Any
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class ProcessStatus(Enum):
    """İşlem durumu"""
    PENDING = "⏳ Bekleniyor"
    ANALYZING = "📹 Analiz Ediliyor"
    PLANNING = "🎯 Plan Oluşturuluyor"
    CREATING = "🎬 Proje Oluşturuluyor"
    RENDERING = "💾 Render Ediliyor"
    COMPLETED = "✅ Tamamlandı"
    FAILED = "❌ Başarısız"


class ProcessManager:
    """İşlem yöneticisi"""
    
    def __init__(self):
        self.processes: Dict[str, Dict[str, Any]] = {}
    
    def add_process(self, process_id: str, file_path: str) -> None:
        """Yeni işlem ekle"""
        self.processes[process_id] = {
            'file_path': file_path,
            'status': ProcessStatus.PENDING,
            'progress': 0,
            'started_at': datetime.now(),
            'completed_at': None,
            'output': None,
            'error': None
        }
        logger.info(f"📝 Yeni işlem eklendi: {process_id}")
    
    def update_status(self, process_id: str, status: ProcessStatus, 
                     progress: int = None) -> None:
        """İşlem durumunu güncelle"""
        if process_id in self.processes:
            self.processes[process_id]['status'] = status
            if progress is not None:
                self.processes[process_id]['progress'] = progress
            logger.info(f"🔄 İşlem güncellendi: {process_id} - {status.value}")
    
    def complete_process(self, process_id: str, output: str) -> None:
        """İşlemi tamamla"""
        if process_id in self.processes:
            self.processes[process_id]['status'] = ProcessStatus.COMPLETED
            self.processes[process_id]['progress'] = 100
            self.processes[process_id]['completed_at'] = datetime.now()
            self.processes[process_id]['output'] = output
            logger.info(f"✅ İşlem tamamlandı: {process_id}")
    
    def fail_process(self, process_id: str, error: str) -> None:
        """İşlemi başarısız olarak işaretle"""
        if process_id in self.processes:
            self.processes[process_id]['status'] = ProcessStatus.FAILED
            self.processes[process_id]['completed_at'] = datetime.now()
            self.processes[process_id]['error'] = error
            logger.error(f"❌ İşlem başarısız: {process_id} - {error}")
    
    def get_process(self, process_id: str) -> Dict[str, Any]:
        """İşlem detaylarını al"""
        return self.processes.get(process_id)
    
    def get_all_processes(self) -> Dict[str, Dict[str, Any]]:
        """Tüm işlemleri al"""
        return self.processes
    
    def get_active_processes(self) -> List[str]:
        """Aktif işlemleri al"""
        return [
            pid for pid, proc in self.processes.items()
            if proc['status'] not in [ProcessStatus.COMPLETED, ProcessStatus.FAILED]
        ]
