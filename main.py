#!/usr/bin/env python3
"""
JODO - After Effects Automation with Claude
Otomatik video analizi ve speed ramp montaj sistemi
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional

from video_analyzer import VideoAnalyzer
from ae_controller import AfterEffectsController
from montage_composer import MontageComposer


def setup_logging(config: dict) -> logging.Logger:
    """Logging ayarlarını yapılandır"""
    log_level = config.get("logging", {}).get("level", "INFO")
    log_file = config.get("logging", {}).get("file", "logs/jodo.log")
    
    # Logs dizinini oluştur
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)


def load_config(config_path: str) -> dict:
    """Konfigürasyon dosyasını yükle"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Konfigürasyon dosyası bulunamadı: {config_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Konfigürasyon dosyası geçersiz JSON: {config_path}")


def process_single_video(
    video_path: str,
    output_dir: str,
    config: dict,
    logger: logging.Logger
) -> bool:
    """Tek bir videoyu işle"""
    try:
        logger.info(f"🎬 Video işleniyor: {video_path}")
        
        # Video analizi
        logger.info("📹 Video analiz ediliyor...")
        analyzer = VideoAnalyzer(config)
        analysis = analyzer.analyze(video_path)
        logger.info(f"✅ Analiz tamamlandı: {len(analysis['scenes'])} sahne tespit edildi")
        
        # Montaj planı oluştur
        logger.info("🎯 Montaj planı oluşturuluyor...")
        composer = MontageComposer(config)
        montage_plan = composer.create_plan(video_path, analysis)
        logger.info(f"✅ Montaj planı hazır")
        
        # After Effects otomasyonu
        logger.info("🎨 After Effects projesine yazılıyor...")
        ae_controller = AfterEffectsController(config)
        project_path = ae_controller.create_project(
            video_path,
            montage_plan,
            output_dir
        )
        logger.info(f"✅ Proje oluşturuldu: {project_path}")
        
        # Render et
        logger.info("🎬 Video render ediliyor...")
        output_path = ae_controller.render(project_path, output_dir)
        logger.info(f"✅ Render tamamlandı: {output_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Hata oluştu: {str(e)}", exc_info=True)
        return False


def process_batch(
    input_dir: str,
    output_dir: str,
    config: dict,
    logger: logging.Logger
) -> None:
    """Klasördeki tüm videoları işle"""
    input_path = Path(input_dir)
    
    if not input_path.exists():
        logger.error(f"Dizin bulunamadı: {input_dir}")
        return
    
    video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv'}
    videos = [f for f in input_path.iterdir() 
              if f.suffix.lower() in video_extensions]
    
    if not videos:
        logger.warning(f"Video bulunamadı: {input_dir}")
        return
    
    logger.info(f"📂 {len(videos)} video bulundu")
    
    success_count = 0
    for i, video_file in enumerate(videos, 1):
        logger.info(f"\n[{i}/{len(videos)}] İşleniyor: {video_file.name}")
        if process_single_video(str(video_file), output_dir, config, logger):
            success_count += 1
    
    logger.info(f"\n{'='*50}")
    logger.info(f"✅ Tamamlandı: {success_count}/{len(videos)} video başarıyla işlendi")


def main():
    """Ana giriş noktası"""
    parser = argparse.ArgumentParser(
        description="JODO - After Effects Automation with Claude"
    )
    
    parser.add_argument(
        "--config",
        default="config.json",
        help="Konfigürasyon dosyası (default: config.json)"
    )
    parser.add_argument(
        "--input", "-i",
        help="Giriş video dosyası"
    )
    parser.add_argument(
        "--batch", "-b",
        help="Batch modu - klasördeki tüm videoları işle"
    )
    parser.add_argument(
        "--output", "-o",
        default="renders",
        help="Çıkış dizini (default: renders)"
    )
    
    args = parser.parse_args()
    
    # Konfigürasyonu yükle
    try:
        config = load_config(args.config)
    except (FileNotFoundError, ValueError) as e:
        print(f"❌ {str(e)}")
        sys.exit(1)
    
    # Logging başlat
    logger = setup_logging(config)
    logger.info("🚀 JODO başlatıldı")
    
    # Çıkış dizinini oluştur
    Path(args.output).mkdir(parents=True, exist_ok=True)
    
    # İşleme başla
    if args.batch:
        logger.info(f"📂 Batch modu: {args.batch}")
        process_batch(args.batch, args.output, config, logger)
    elif args.input:
        logger.info(f"🎬 Tek dosya modu: {args.input}")
        if process_single_video(args.input, args.output, config, logger):
            logger.info("✅ İşlem başarıyla tamamlandı!")
            sys.exit(0)
        else:
            logger.error("❌ İşlem başarısız")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()