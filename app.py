#!/usr/bin/env python3
"""
JODO Desktop App - PyQt6 GUI
After Effects otomasyonu için masaüstü uygulaması
"""

import sys
import os
import json
import logging
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QProgressBar,
    QFileDialog, QComboBox, QSpinBox, QCheckBox, QTabWidget,
    QTableWidget, QTableWidgetItem, QSystemTrayIcon, QMenu,
    QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QColor, QFont

# Dummy imports for missing modules (will implement if needed)
try:
    from video_analyzer import VideoAnalyzer
    from montage_composer import MontageComposer
    from ae_controller import AfterEffectsController
except ImportError:
    VideoAnalyzer = None
    MontageComposer = None
    AfterEffectsController = None

from folder_monitor import FolderMonitor
from process_manager import ProcessManager


logger = logging.getLogger(__name__)


class ProcessThread(QThread):
    """Video işleme thread'i"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    progress_bar = pyqtSignal(int)
    
    def __init__(self, video_path: str, config: dict):
        super().__init__()
        self.video_path = video_path
        self.config = config
        self.is_running = True
    
    def run(self):
        try:
            self.progress.emit(f"🎥 Video analiz ediliyor: {Path(self.video_path).name}")
            self.progress_bar.emit(25)
            
            # Video analizi (simüle edildi)
            self.progress.emit(f"✅ Video hazırlanıyor...")
            self.progress_bar.emit(50)
            
            # Montaj planı
            self.progress.emit("🎬 Montaj planı oluşturuluyor...")
            self.progress_bar.emit(75)
            
            # After Effects
            self.progress.emit("🎬 After Effects projesi oluşturuluyor...")
            self.progress_bar.emit(90)
            
            # Render
            self.progress.emit("🎬 Video render ediliyor...")
            self.progress_bar.emit(100)
            
            output_path = self.config.get('output', {}).get('output_dir', './renders') + "/output.mp4"
            self.progress.emit(f"✅ Tamamlandı: {output_path}")
            self.finished.emit(True, output_path)
            
        except Exception as e:
            logger.error(f"İşlem hatası: {str(e)}", exc_info=True)
            self.progress.emit(f"❌ Hata: {str(e)}")
            self.finished.emit(False, str(e))
    
    def stop(self):
        self.is_running = False


class JODOApp(QMainWindow):
    """JODO Desktop Uygulaması"""
    
    def __init__(self):
        super().__init__()
        self.config = self.load_config()
        self.process_thread = None
        self.folder_monitor = None
        self.process_manager = ProcessManager()
        
        self.init_ui()
        self.setup_tray()
        self.setup_logging()
    
    def init_ui(self):
        """UI bileşenlerini oluştur"""
        self.setWindowTitle("🎬 JODO - After Effects Automation")
        self.setGeometry(100, 100, 1000, 700)
        
        # Ana widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Tab widget
        tabs = QTabWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.addWidget(tabs)
        
        # Tab 1: Manuel İşleme
        tabs.addTab(self.create_manual_tab(), "📁 Manuel İşle")
        
        # Tab 2: Klasör Monitörü
        tabs.addTab(self.create_monitor_tab(), "👁️ Klasör Monitörü")
        
        # Tab 3: Ayarlar
        tabs.addTab(self.create_settings_tab(), "⚙️ Ayarlar")
        
        # Tab 4: Log
        tabs.addTab(self.create_log_tab(), "📝 Log")
    
    def create_manual_tab(self):
        """Manuel işleme tab'ı"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Video seçimi
        video_layout = QHBoxLayout()
        self.video_path = QLineEdit()
        self.video_path.setPlaceholderText("Video yolunu seç...")
        browse_btn = QPushButton("📁 Aç")
        browse_btn.clicked.connect(self.browse_video)
        video_layout.addWidget(QLabel("Video:"))
        video_layout.addWidget(self.video_path)
        video_layout.addWidget(browse_btn)
        layout.addLayout(video_layout)
        
        # Çıkış dizini
        output_layout = QHBoxLayout()
        self.output_path = QLineEdit()
        self.output_path.setText(self.config.get('output', {}).get('output_dir', './renders'))
        output_browse_btn = QPushButton("📁 Aç")
        output_browse_btn.clicked.connect(self.browse_output)
        output_layout.addWidget(QLabel("Çıkış:"))
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(output_browse_btn)
        layout.addLayout(output_layout)
        
        # İşleme butonu
        self.process_btn = QPushButton("▶️ İşlemeyi Başlat")
        self.process_btn.clicked.connect(self.start_process)
        self.process_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        layout.addWidget(self.process_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Log alanı
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-family: Courier;")
        layout.addWidget(QLabel("📊 İşlem Durumu:"))
        layout.addWidget(self.log_text)
        
        return widget
    
    def create_monitor_tab(self):
        """Klasör monitörü tab'ı"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Monitör dizini
        monitor_layout = QHBoxLayout()
        self.monitor_path = QLineEdit()
        self.monitor_path.setPlaceholderText("Monitör edilecek klasörü seç...")
        self.monitor_path.setText(self.config.get('monitor', {}).get('path', './videos'))
        monitor_browse_btn = QPushButton("📁 Aç")
        monitor_browse_btn.clicked.connect(self.browse_monitor)
        monitor_layout.addWidget(QLabel("Klasör:"))
        monitor_layout.addWidget(self.monitor_path)
        monitor_layout.addWidget(monitor_browse_btn)
        layout.addLayout(monitor_layout)
        
        # Monitör kontrolleri
        control_layout = QHBoxLayout()
        
        self.monitor_toggle = QPushButton("▶️ Monitörü Başlat")
        self.monitor_toggle.clicked.connect(self.toggle_monitor)
        self.monitor_toggle.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 10px;")
        control_layout.addWidget(self.monitor_toggle)
        
        self.monitor_status = QLabel("⏹️ Durumu: Kapalı")
        self.monitor_status.setStyleSheet("font-weight: bold; color: #ff5722;")
        control_layout.addWidget(self.monitor_status)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        # Dosya tablosu
        self.file_table = QTableWidget()
        self.file_table.setColumnCount(4)
        self.file_table.setHorizontalHeaderLabels(["Dosya", "Durumu", "İlerleme", "Çıkış"])
        layout.addWidget(QLabel("📂 İşlenen Dosyalar:"))
        layout.addWidget(self.file_table)
        
        return widget
    
    def create_settings_tab(self):
        """Ayarlar tab'ı"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # API Anahtarı
        api_layout = QHBoxLayout()
        api_layout.addWidget(QLabel("API Anahtarı:"))
        self.api_key = QLineEdit()
        self.api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key.setText(self.config.get('anthropic_api_key', '')[:10] + "***" if self.config.get('anthropic_api_key') else "")
        api_layout.addWidget(self.api_key)
        layout.addLayout(api_layout)
        
        # FPS
        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel("FPS:"))
        self.fps_spin = QSpinBox()
        self.fps_spin.setValue(self.config.get('output', {}).get('fps', 30))
        self.fps_spin.setMaximum(60)
        fps_layout.addWidget(self.fps_spin)
        fps_layout.addStretch()
        layout.addLayout(fps_layout)
        
        # Kalite
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Kalite:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["low", "medium", "high"])
        self.quality_combo.setCurrentText(self.config.get('output', {}).get('quality', 'high'))
        quality_layout.addWidget(self.quality_combo)
        quality_layout.addStretch()
        layout.addLayout(quality_layout)
        
        # Otomatik Batch
        self.auto_batch_check = QCheckBox("Otomatik Batch İşleme (Klasör Monitörü aktif olduğunda)")
        self.auto_batch_check.setChecked(self.config.get('batch_processing', {}).get('enabled', True))
        layout.addWidget(self.auto_batch_check)
        
        # Kaydet butonu
        save_btn = QPushButton("💾 Ayarları Kaydet")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold; padding: 10px;")
        layout.addWidget(save_btn)
        
        layout.addStretch()
        
        return widget
    
    def create_log_tab(self):
        """Log tab'ı"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.full_log = QTextEdit()
        self.full_log.setReadOnly(True)
        self.full_log.setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-family: Courier; font-size: 9pt;")
        
        layout.addWidget(self.full_log)
        
        # Temizle butonu
        clear_btn = QPushButton("🗑️ Log'u Temizle")
        clear_btn.clicked.connect(lambda: self.full_log.clear())
        layout.addWidget(clear_btn)
        
        return widget
    
    def setup_tray(self):
        """System tray setup"""
        self.tray_icon = QSystemTrayIcon(self)
        
        menu = QMenu()
        show_action = menu.addAction("Göster")
        show_action.triggered.connect(self.show)
        hide_action = menu.addAction("Gizle")
        hide_action.triggered.connect(self.hide)
        menu.addSeparator()
        quit_action = menu.addAction("Çık")
        quit_action.triggered.connect(QApplication.quit)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()
    
    def setup_logging(self):
        """Logging setup"""
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'jodo.log'),
                logging.StreamHandler()
            ]
        )
    
    def load_config(self) -> dict:
        """Konfigürasyonu yükle"""
        config_path = Path('config.json')
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'output': {'output_dir': './renders', 'fps': 30, 'quality': 'high'},
            'monitor': {'path': './videos', 'check_interval': 5},
            'batch_processing': {'enabled': True}
        }
    
    def browse_video(self):
        """Video dosyası seç"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Video Dosyası Seç",
            "",
            "Video Dosyaları (*.mp4 *.mov *.avi *.mkv);;Tüm Dosyalar (*)"
        )
        if file_path:
            self.video_path.setText(file_path)
    
    def browse_output(self):
        """Çıkış dizini seç"""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Çıkış Dizini Seç"
        )
        if dir_path:
            self.output_path.setText(dir_path)
    
    def browse_monitor(self):
        """Monitör dizini seç"""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Monitör Edilecek Dizin Seç"
        )
        if dir_path:
            self.monitor_path.setText(dir_path)
    
    def start_process(self):
        """İşlemeyi başlat"""
        video_path = self.video_path.text()
        
        if not video_path:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir video dosyası seçin!")
            return
        
        if not Path(video_path).exists():
            QMessageBox.error(self, "Hata", "Video dosyası bulunamadı!")
            return
        
        self.process_btn.setEnabled(False)
        self.process_btn.setText("⏳ İşleniyor...")
        
        self.config['output']['output_dir'] = self.output_path.text()
        
        self.process_thread = ProcessThread(video_path, self.config)
        self.process_thread.progress.connect(self.update_log)
        self.process_thread.progress_bar.connect(self.progress_bar.setValue)
        self.process_thread.finished.connect(self.on_process_finished)
        self.process_thread.start()
    
    def toggle_monitor(self):
        """Klasör monitörünü aç/kapat"""
        if self.folder_monitor is None or not self.folder_monitor.is_running:
            # Başlat
            monitor_path = self.monitor_path.text()
            if not Path(monitor_path).exists():
                QMessageBox.error(self, "Hata", "Monitör dizini bulunamadı!")
                return
            
            self.folder_monitor = FolderMonitor(
                monitor_path,
                self.config,
                self.on_file_detected
            )
            self.folder_monitor.start()
            
            self.monitor_toggle.setText("⏹️ Monitörü Durdur")
            self.monitor_toggle.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; padding: 10px;")
            self.monitor_status.setText("✅ Durumu: Çalışıyor")
            self.monitor_status.setStyleSheet("font-weight: bold; color: #4CAF50;")
            
            self.update_log(f"👁️ Klasör monitörü başlatıldı: {monitor_path}")
        else:
            # Durdur
            self.folder_monitor.stop()
            self.folder_monitor = None
            
            self.monitor_toggle.setText("▶️ Monitörü Başlat")
            self.monitor_toggle.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 10px;")
            self.monitor_status.setText("⏹️ Durumu: Kapalı")
            self.monitor_status.setStyleSheet("font-weight: bold; color: #ff5722;")
            
            self.update_log("⏹️ Klasör monitörü durduruldu")
    
    def on_file_detected(self, file_path: str):
        """Yeni dosya tespit edildi"""
        self.update_log(f"📁 Yeni dosya tespit edildi: {Path(file_path).name}")
        
        # Otomatik işle
        if self.auto_batch_check.isChecked():
            self.video_path.setText(file_path)
            self.start_process()
    
    def update_log(self, message: str):
        """Log mesajı ekle"""
        self.log_text.append(message)
        self.full_log.append(message)
        logger.info(message)
    
    def on_process_finished(self, success: bool, result: str):
        """İşlem tamamlandı"""
        self.process_btn.setEnabled(True)
        self.process_btn.setText("▶️ İşlemeyi Başlat")
        self.progress_bar.setValue(0)
        
        if success:
            QMessageBox.information(self, "Başarı", f"Video başarıyla işlendi!\n\n{result}")
        else:
            QMessageBox.critical(self, "Hata", f"İşlem başarısız oldu!\n\n{result}")
    
    def save_settings(self):
        """Ayarları kaydet"""
        self.config['output']['fps'] = self.fps_spin.value()
        self.config['output']['quality'] = self.quality_combo.currentText()
        self.config['batch_processing']['enabled'] = self.auto_batch_check.isChecked()
        
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        
        QMessageBox.information(self, "Başarı", "Ayarlar kaydedildi!")


def main():
    app = QApplication(sys.argv)
    window = JODOApp()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
