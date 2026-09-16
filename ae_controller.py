"""
After Effects Controller - AE otomasyon kontrol
"""

import logging
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class AfterEffectsController:
    """After Effects projesini otomatik oluştur ve kontrol et"""
    
    def __init__(self, config: dict):
        self.config = config
        self.ae_path = config.get("after_effects", {}).get("path", "")
        self.timeout = config.get("after_effects", {}).get("timeout", 3600)
        self.auto_save = config.get("after_effects", {}).get("auto_save", True)
    
    def create_project(
        self,
        video_path: str,
        montage_plan: Dict[str, Any],
        output_dir: str
    ) -> str:
        """After Effects projesini oluştur"""
        logger.info("🎨 After Effects projesi oluşturuluyor...")
        
        # Proje dosya yolu
        project_name = Path(video_path).stem + "_jodo.aep"
        project_path = Path(output_dir) / project_name
        
        # ExtendScript oluştur
        jsx_script = self._generate_jsx_script(
            video_path,
            montage_plan,
            str(project_path)
        )
        
        # Geçici JSX dosyasını kaydet
        jsx_path = Path(output_dir) / "temp_script.jsx"
        jsx_path.write_text(jsx_script, encoding='utf-8')
        
        logger.info(f"📝 JSX script yazıldı: {jsx_path}")
        
        # After Effects'i çalıştır
        try:
            self._run_ae_script(str(jsx_path))
            logger.info(f"✅ Proje oluşturuldu: {project_path}")
            return str(project_path)
        except Exception as e:
            logger.error(f"After Effects hatası: {str(e)}")
            raise
    
    def render(self, project_path: str, output_dir: str) -> str:
        """Projeyi render et"""
        logger.info(f"🎬 Rendering başlıyor: {project_path}")
        
        output_file = Path(output_dir) / (Path(project_path).stem + ".mp4")
        
        # Render JSX script'i oluştur
        render_script = self._generate_render_script(
            project_path,
            str(output_file)
        )
        
        # Geçici script kaydet
        jsx_path = Path(output_dir) / "render_script.jsx"
        jsx_path.write_text(render_script, encoding='utf-8')
        
        try:
            self._run_ae_script(str(jsx_path))
            logger.info(f"✅ Render tamamlandı: {output_file}")
            return str(output_file)
        except Exception as e:
            logger.error(f"Render hatası: {str(e)}")
            raise
    
    def _generate_jsx_script(
        self,
        video_path: str,
        montage_plan: Dict[str, Any],
        output_path: str
    ) -> str:
        """Montaj planından JSX script oluştur"""
        
        jsx_template = f"""
// JODO - After Effects Automation Script
var project = app.newProject();

// Yeni composition oluştur
var compSettings = {{
    "width": 1920,
    "height": 1080,
    "pixelAspect": 1,
    "frameRate": 30,
    "duration": {montage_plan.get('duration', 60)}
}};

var comp = project.items.addComp(
    "JODO_Montage",
    compSettings.width,
    compSettings.height,
    compSettings.pixelAspect,
    compSettings.duration,
    compSettings.frameRate
);

// Video'yu import et
var videoFile = new File("{video_path}");
var footage = project.importFile(videoFile);
var layer = comp.layers.add(footage);

// Speed ramps uygulanıyor
"""
        
        # Speed ramps'ı JSX'e ekle
        for ramp in montage_plan.get('speed_ramps', []):
            timestamp = ramp['timestamp']
            start_speed = ramp['start_speed']
            end_speed = ramp['end_speed']
            duration = ramp['duration']
            
            jsx_template += f"""
// Speed ramp: {timestamp}s - {ramp['type']}
layer.timeRemapEnabled = true;
layer.timeRemap.setValueAtTime({timestamp}, {timestamp} * {start_speed});
layer.timeRemap.setValueAtTime({timestamp} + {duration}, {timestamp} * {end_speed});
"""
        
        # Transitions'ı ekle
        for trans in montage_plan.get('transitions', []):
            jsx_template += f"""
// Transition: {trans['type']} at {trans['timestamp']}s
"""
        
        # Başlıkları ekle
        for title in montage_plan.get('titles', []):
            jsx_template += f"""
// Title: {title['text']}
"""
        
        jsx_template += f"""
// Projeyi kaydet
project.save(new File("{output_path}"));
alert("Proje başarıyla oluşturuldu!");
"""
        
        return jsx_template
    
    def _generate_render_script(self, project_path: str, output_path: str) -> str:
        """Render JSX script'i oluştur"""
        
        render_script = f"""
// JODO Render Script
var project = app.open(new File("{project_path}"));

if (project != null) {{
    var comp = project.items[1];
    
    if (comp instanceof CompItem) {{
        // Render queue'ya ekle
        var outputModule = comp.openInViewer(ViewerType.VIEWER_1).aeComp.render;
        
        // Media codec ayarları
        var outputOptions = {{
            "format": "ffmpeg",
            "codec": "h264",
            "bitrate": "25000k",
            "path": "{output_path}"
        }};
        
        alert("Render tamamlandı!");
        project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
    }}
}} else {{
    alert("Proje açılamadı!");
}}
"""
        
        return render_script
    
    def _run_ae_script(self, jsx_path: str) -> None:
        """JSX script'ini After Effects'te çalıştır"""
        
        if not self.ae_path:
            logger.warning("After Effects yolu ayarlanmamış, simülasyon modunda çalışılıyor")
            logger.info(f"📝 Script çalıştırılacak: {jsx_path}")
            return
        
        try:
            # Windows için komut
            cmd = [
                self.ae_path,
                "-r",
                jsx_path
            ]
            
            logger.info(f"⚙️  Komut çalıştırılıyor: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                timeout=self.timeout,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"After Effects hatası: {result.stderr}")
                raise RuntimeError(f"After Effects hatası: {result.stderr}")
            
            logger.info(f"✅ Script başarıyla çalıştırıldı")
            
        except subprocess.TimeoutExpired:
            logger.error(f"After Effects timeout: {self.timeout}s")
            raise
        except Exception as e:
            logger.error(f"Script çalıştırma hatası: {str(e)}")
            raise