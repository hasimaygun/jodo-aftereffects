"""
Montage Composer - Montaj planı oluşturma
"""

import logging
from typing import Dict, List, Any
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class MontageComposer:
    """Analiz verilerinden montaj planı oluştur"""
    
    def __init__(self, config: dict):
        self.config = config
        self.client = Anthropic()
        self.api_key = config.get("anthropic_api_key")
    
    def create_plan(self, video_path: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Montaj planı oluştur"""
        logger.info("🎯 Montaj planı oluşturuluyor...")
        
        # Analiz verilerinden plan oluştur
        plan = {
            'video_path': video_path,
            'duration': analysis['duration'],
            'speed_ramps': self._create_speed_ramps(analysis['scenes']),
            'transitions': self._create_transitions(analysis['scenes']),
            'cuts': self._find_cut_points(analysis['scenes']),
            'titles': self._generate_titles(analysis),
            'effects': self._select_effects(analysis)
        }
        
        logger.info(f"✅ Montaj planı oluşturuldu")
        logger.info(f"   - Speed Ramps: {len(plan['speed_ramps'])}")
        logger.info(f"   - Transitions: {len(plan['transitions'])}")
        logger.info(f"   - Cut Points: {len(plan['cuts'])}")
        
        return plan
    
    def _create_speed_ramps(self, scenes: List[Dict]) -> List[Dict]:
        """Speed ramp noktaları belirle"""
        speed_ramps = []
        
        for i, scene in enumerate(scenes):
            timestamp = scene.get('timestamp', 0)
            motion = scene.get('motion_level', 'medium')
            suggested_speed = scene.get('suggested_speed', 1.0)
            
            # Hareketli sahneler için ramp
            if motion == 'high':
                # Hızlan
                speed_ramps.append({
                    'timestamp': timestamp,
                    'start_speed': 1.0,
                    'end_speed': suggested_speed,
                    'duration': 0.3,
                    'easing': 'easeInOutQuad',
                    'type': 'speed_up'
                })
            elif motion == 'low':
                # Yavaşlat
                speed_ramps.append({
                    'timestamp': timestamp,
                    'start_speed': 1.0,
                    'end_speed': 0.5,
                    'duration': 0.3,
                    'easing': 'easeInOutQuad',
                    'type': 'slow_down'
                })
        
        return speed_ramps
    
    def _create_transitions(self, scenes: List[Dict]) -> List[Dict]:
        """Geçiş efektleri ekle"""
        transitions = []
        transition_types = self.config.get('transitions', {}).get('types', [])
        transition_duration = self.config.get('transitions', {}).get('duration', 0.3)
        
        for i in range(len(scenes) - 1):
            current_scene = scenes[i]
            next_scene = scenes[i + 1]
            
            # Sahne türü değişirse transition ekle
            if current_scene.get('scene_type') != next_scene.get('scene_type'):
                transition = {
                    'timestamp': current_scene.get('timestamp', 0),
                    'type': transition_types[i % len(transition_types)] if transition_types else 'crossDissolve',
                    'duration': transition_duration,
                    'from_scene': current_scene.get('scene_type', 'unknown'),
                    'to_scene': next_scene.get('scene_type', 'unknown')
                }
                transitions.append(transition)
        
        return transitions
    
    def _find_cut_points(self, scenes: List[Dict]) -> List[Dict]:
        """Kesme noktaları belirle"""
        cuts = []
        
        for i in range(len(scenes) - 1):
            current = scenes[i]
            next_scene = scenes[i + 1]
            
            # Hareket seviyesi önemli ölçüde değişirse kes
            motion_current = current.get('motion_level', 'medium')
            motion_next = next_scene.get('motion_level', 'medium')
            
            motion_values = {'low': 1, 'medium': 2, 'high': 3}
            if abs(motion_values.get(motion_current, 2) - motion_values.get(motion_next, 2)) > 1:
                cuts.append({
                    'timestamp': current.get('timestamp', 0),
                    'reason': f'{motion_current} -> {motion_next}',
                    'fade_duration': 0.1
                })
        
        return cuts
    
    def _generate_titles(self, analysis: Dict) -> List[Dict]:
        """Başlıklar oluştur"""
        titles = []
        
        summary = analysis.get('summary', {})
        scene_types = summary.get('scene_types', {})
        
        # Başında genel başlık
        title = {
            'timestamp': 0,
            'text': 'JODO MONTAGE',
            'duration': 2.0,
            'position': 'center',
            'animation': 'fadeIn',
            'font_size': 48,
            'color': '#FFFFFF'
        }
        titles.append(title)
        
        return titles
    
    def _select_effects(self, analysis: Dict) -> List[Dict]:
        """Efektleri seç"""
        effects = []
        
        summary = analysis.get('summary', {})
        motion_levels = summary.get('motion_levels', {})
        
        # Hareket temelinde efekt seç
        if motion_levels.get('high', 0) > motion_levels.get('low', 0):
            effects.append({
                'name': 'glow',
                'intensity': 0.3,
                'color': '#FF6B6B'
            })
        
        # Renk düzeltmesi
        effects.append({
            'name': 'color_correction',
            'saturation': 1.2,
            'contrast': 1.1
        })
        
        return effects