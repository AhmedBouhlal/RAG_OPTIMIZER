"""
Model Manager for RAG System
Handles installation and management of local LLM models
"""

import os
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ModelManager:
    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        self.config_file = self.models_dir / "installed_models.json"
        self.installed_models = self.load_installed_models()

    def load_installed_models(self) -> Dict[str, Any]:
        """Load list of installed models"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}

    def save_installed_models(self):
        """Save list of installed models"""
        with open(self.config_file, 'w') as f:
            json.dump(self.installed_models, f, indent=2)

    def get_available_models(self) -> List[str]:
        """Get list of available models for installation"""
        return [
            "llama3",
            "llama2-7b",
            "llama2-13b",
            "llama2-70b",
            "mistral-7b",
            "mixtral-8x7b",
            "codellama-7b",
            "codellama-13b",
            "qwen-7b",
            "qwen-14b",
        ]

    def get_installed_models(self) -> List[str]:
        """Get list of installed models"""
        return list(self.installed_models.keys())

    def install_model(self, model_name: str) -> Dict[str, Any]:
        """Install a model using ollama"""
        try:
            # Check if ollama is available
            result = subprocess.run(['ollama', '--version'],
                                  capture_output=True, text=True)
            if result.returncode != 0:
                return {
                    "success": False,
                    "message": "Ollama not found. Please install ollama first."
                }

            # Install the model
            logger.info(f"Installing model: {model_name}")
            result = subprocess.run(['ollama', 'pull', model_name],
                                  capture_output=True, text=True, timeout=600)

            if result.returncode == 0:
                self.installed_models[model_name] = {
                    "installed_at": str(Path.cwd()),
                    "type": "ollama",
                    "status": "installed"
                }
                self.save_installed_models()
                return {
                    "success": True,
                    "message": f"Model {model_name} installed successfully"
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to install {model_name}: {result.stderr}"
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "message": f"Installation of {model_name} timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error installing {model_name}: {str(e)}"
            }

    def test_model(self, model_name: str) -> Dict[str, Any]:
        """Test if a model is working"""
        try:
            result = subprocess.run(['ollama', 'run', model_name, 'Hello'],
                                  capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                return {
                    "success": True,
                    "message": f"Model {model_name} is working",
                    "response": result.stdout.strip()
                }
            else:
                return {
                    "success": False,
                    "message": f"Model {model_name} test failed: {result.stderr}"
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "message": f"Model {model_name} test timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error testing {model_name}: {str(e)}"
            }

    def remove_model(self, model_name: str) -> Dict[str, Any]:
        """Remove a model"""
        try:
            result = subprocess.run(['ollama', 'rm', model_name],
                                  capture_output=True, text=True)

            if result.returncode == 0:
                if model_name in self.installed_models:
                    del self.installed_models[model_name]
                    self.save_installed_models()
                return {
                    "success": True,
                    "message": f"Model {model_name} removed successfully"
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to remove {model_name}: {result.stderr}"
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error removing {model_name}: {str(e)}"
            }

# Global model manager instance
model_manager = ModelManager()
