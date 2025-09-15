#!/usr/bin/env python3
"""
DMR Model Information Extractor
===============================

This script connects to Docker Model Runner (DMR) and extracts comprehensive
information about available models, their parameters, and supported functions.

Author: XTREMEDEV
Date: September 15, 2025
"""

import requests
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ModelCapabilities:
    """Data class to store model capabilities and test results"""
    supports_function_calling: bool = False
    supports_json_mode: bool = False
    supports_streaming: bool = False
    supports_embeddings: bool = False
    max_context_length: Optional[int] = None
    supported_parameters: List[str] = None
    
    def __post_init__(self):
        if self.supported_parameters is None:
            self.supported_parameters = []


@dataclass
class ModelInfo:
    """Data class to store comprehensive model information"""
    id: str
    object: str
    created: int
    owned_by: str
    capabilities: ModelCapabilities
    last_tested: str
    test_results: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.test_results is None:
            self.test_results = {}


class DMRModelAnalyzer:
    """Analyzer class for Docker Model Runner models"""
    
    def __init__(self, base_url: str = "http://localhost:12434/engines/v1"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
        
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Retrieve list of available models from DMR"""
        try:
            response = self.session.get(f"{self.base_url}/models")
            response.raise_for_status()
            return response.json()["data"]
        except requests.RequestException as e:
            print(f"Error fetching models: {e}")
            return []
    
    def test_function_calling(self, model_id: str) -> Dict[str, Any]:
        """Test if model supports function calling"""
        test_payload = {
            "model": model_id,
            "messages": [
                {
                    "role": "user",
                    "content": "What's the weather like in Paris?"
                }
            ],
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "description": "Get current weather for a location",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "City and country, e.g. Paris, France"
                                },
                                "units": {
                                    "type": "string",
                                    "enum": ["celsius", "fahrenheit"],
                                    "description": "Temperature units"
                                }
                            },
                            "required": ["location"]
                        }
                    }
                }
            ]
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=test_payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            # Check if response contains tool_calls
            has_tool_calls = (
                result.get("choices", [{}])[0]
                .get("message", {})
                .get("tool_calls") is not None
            )
            
            return {
                "supports_function_calling": has_tool_calls,
                "finish_reason": result.get("choices", [{}])[0].get("finish_reason"),
                "response": result
            }
        except Exception as e:
            return {
                "supports_function_calling": False,
                "error": str(e)
            }
    
    def test_json_mode(self, model_id: str) -> Dict[str, Any]:
        """Test if model supports JSON response format"""
        test_payload = {
            "model": model_id,
            "messages": [
                {
                    "role": "user",
                    "content": "Extract person info from: 'Alice Johnson, 28, Data Scientist'. Return as JSON with name, age, job fields."
                }
            ],
            "response_format": {
                "type": "json_object"
            }
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=test_payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Try to parse as JSON
            try:
                json.loads(content)
                is_valid_json = True
            except json.JSONDecodeError:
                is_valid_json = False
            
            return {
                "supports_json_mode": is_valid_json,
                "content": content,
                "response": result
            }
        except Exception as e:
            return {
                "supports_json_mode": False,
                "error": str(e)
            }
    
    def test_streaming(self, model_id: str) -> Dict[str, Any]:
        """Test if model supports streaming responses"""
        test_payload = {
            "model": model_id,
            "messages": [
                {
                    "role": "user",
                    "content": "Count from 1 to 3"
                }
            ],
            "stream": True
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=test_payload,
                stream=True,
                timeout=30
            )
            response.raise_for_status()
            
            chunks = []
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    if line_text.startswith('data: ') and not line_text.endswith('[DONE]'):
                        try:
                            chunk_data = json.loads(line_text[6:])  # Remove 'data: ' prefix
                            chunks.append(chunk_data)
                        except json.JSONDecodeError:
                            continue
            
            return {
                "supports_streaming": len(chunks) > 0,
                "chunk_count": len(chunks),
                "sample_chunks": chunks[:3] if chunks else []
            }
        except Exception as e:
            return {
                "supports_streaming": False,
                "error": str(e)
            }
    
    def test_parameters(self, model_id: str) -> Dict[str, Any]:
        """Test various OpenAI parameters support"""
        test_payload = {
            "model": model_id,
            "messages": [
                {
                    "role": "user",
                    "content": "Write a short creative sentence"
                }
            ],
            "temperature": 0.7,
            "max_tokens": 30,
            "top_p": 0.9,
            "frequency_penalty": 0.3,
            "presence_penalty": 0.3,
            "stop": ["\n"]
        }
        
        supported_params = []
        
        try:
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=test_payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            # If successful, all parameters are supported
            supported_params = ["temperature", "max_tokens", "top_p", 
                              "frequency_penalty", "presence_penalty", "stop"]
            
            return {
                "supported_parameters": supported_params,
                "response": result,
                "usage": result.get("usage", {})
            }
        except Exception as e:
            # Try individual parameters to see which ones work
            base_payload = {
                "model": model_id,
                "messages": [{"role": "user", "content": "Test"}]
            }
            
            for param, value in [
                ("temperature", 0.7),
                ("max_tokens", 20),
                ("top_p", 0.9),
                ("frequency_penalty", 0.3),
                ("presence_penalty", 0.3)
            ]:
                try:
                    test_param_payload = {**base_payload, param: value}
                    param_response = self.session.post(
                        f"{self.base_url}/chat/completions",
                        json=test_param_payload,
                        timeout=15
                    )
                    if param_response.status_code == 200:
                        supported_params.append(param)
                except:
                    continue
            
            return {
                "supported_parameters": supported_params,
                "error": str(e)
            }
    
    def test_embeddings(self, model_id: str) -> Dict[str, Any]:
        """Test if model supports embeddings"""
        test_payload = {
            "model": model_id,
            "input": "This is a test sentence for embeddings"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/embeddings",
                json=test_payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            embeddings = result.get("data", [])
            if embeddings:
                embedding_vector = embeddings[0].get("embedding", [])
                return {
                    "supports_embeddings": True,
                    "dimensions": len(embedding_vector),
                    "usage": result.get("usage", {}),
                    "sample_values": embedding_vector[:5] if embedding_vector else []
                }
            else:
                return {"supports_embeddings": False}
                
        except Exception as e:
            return {
                "supports_embeddings": False,
                "error": str(e)
            }
    
    def analyze_model(self, model_data: Dict[str, Any]) -> ModelInfo:
        """Perform comprehensive analysis of a single model"""
        model_id = model_data["id"]
        print(f"\n🔍 Analyzing model: {model_id}")
        
        # Initialize capabilities
        capabilities = ModelCapabilities()
        test_results = {}
        
        # Test function calling (for chat models)
        if not model_id.lower().startswith(('ai/embed', 'ai/mxbai')):
            print("  Testing function calling...")
            func_test = self.test_function_calling(model_id)
            capabilities.supports_function_calling = func_test["supports_function_calling"]
            test_results["function_calling"] = func_test
            
            # Test JSON mode
            print("  Testing JSON mode...")
            json_test = self.test_json_mode(model_id)
            capabilities.supports_json_mode = json_test["supports_json_mode"]
            test_results["json_mode"] = json_test
            
            # Test streaming
            print("  Testing streaming...")
            stream_test = self.test_streaming(model_id)
            capabilities.supports_streaming = stream_test["supports_streaming"]
            test_results["streaming"] = stream_test
            
            # Test parameters
            print("  Testing parameters...")
            param_test = self.test_parameters(model_id)
            capabilities.supported_parameters = param_test["supported_parameters"]
            test_results["parameters"] = param_test
        
        # Test embeddings
        print("  Testing embeddings...")
        embed_test = self.test_embeddings(model_id)
        capabilities.supports_embeddings = embed_test["supports_embeddings"]
        test_results["embeddings"] = embed_test
        
        return ModelInfo(
            id=model_id,
            object=model_data["object"],
            created=model_data["created"],
            owned_by=model_data["owned_by"],
            capabilities=capabilities,
            last_tested=datetime.now().isoformat(),
            test_results=test_results
        )
    
    def analyze_all_models(self) -> List[ModelInfo]:
        """Analyze all available models"""
        print("🚀 Starting DMR Model Analysis...")
        
        models = self.get_available_models()
        if not models:
            print("❌ No models found or unable to connect to DMR")
            return []
        
        print(f"📋 Found {len(models)} models to analyze")
        
        analyzed_models = []
        for model_data in models:
            try:
                model_info = self.analyze_model(model_data)
                analyzed_models.append(model_info)
                print(f"✅ Completed analysis for {model_info.id}")
            except Exception as e:
                print(f"❌ Error analyzing {model_data['id']}: {e}")
        
        return analyzed_models
    
    def save_results(self, models: List[ModelInfo], filename: str = "dmr_model_analysis.json"):
        """Save analysis results to JSON file"""
        results = {
            "analysis_date": datetime.now().isoformat(),
            "dmr_endpoint": self.base_url,
            "total_models": len(models),
            "models": [asdict(model) for model in models]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to {filename}")
    
    def print_summary(self, models: List[ModelInfo]):
        """Print a summary of capabilities"""
        print("\n" + "="*60)
        print("📊 DMR MODEL CAPABILITIES SUMMARY")
        print("="*60)
        
        for model in models:
            print(f"\n🤖 {model.id}")
            print(f"   Created: {datetime.fromtimestamp(model.created).strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Owner: {model.owned_by}")
            
            caps = model.capabilities
            print(f"   📋 Capabilities:")
            print(f"      🔧 Function Calling: {'✅' if caps.supports_function_calling else '❌'}")
            print(f"      📄 JSON Mode: {'✅' if caps.supports_json_mode else '❌'}")
            print(f"      🌊 Streaming: {'✅' if caps.supports_streaming else '❌'}")
            print(f"      🔢 Embeddings: {'✅' if caps.supports_embeddings else '❌'}")
            
            if caps.supported_parameters:
                print(f"      ⚙️  Parameters: {', '.join(caps.supported_parameters)}")
            
            # Show embedding dimensions if available
            if caps.supports_embeddings and model.test_results.get("embeddings", {}).get("dimensions"):
                dims = model.test_results["embeddings"]["dimensions"]
                print(f"      📐 Embedding Dims: {dims}")


def main():
    """Main execution function"""
    print("🐳 Docker Model Runner (DMR) - Model Analysis Tool")
    print("=" * 50)
    
    analyzer = DMRModelAnalyzer()
    
    # Analyze all models
    models = analyzer.analyze_all_models()
    
    if models:
        # Print summary
        analyzer.print_summary(models)
        
        # Save detailed results
        analyzer.save_results(models)
        
        print(f"\n🎉 Analysis complete! Found {len(models)} models with comprehensive capability data.")
    else:
        print("\n❌ No models analyzed. Check your DMR connection.")


if __name__ == "__main__":
    main()