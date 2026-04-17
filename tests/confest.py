"""
Конфигурация pytest для добавления корня проекта в PATH.
"""

import sys
import os
from pathlib import Path

# Добавляем корень проекта в sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))
