"""
Ensemble service for multi-model color analysis.
Implements parallel processing with aggregation and hybrid judge approach.
"""
import json
import asyncio
from typing import List, Dict, Optional, Literal
from PIL import Image
from io import BytesIO
import base64

from google.genai import types as gemini_types
from openai import OpenAI
from anthropic import Anthropic

from src.config import config
from src.models import AnalyzeColorSeasonResponseModel
from src.utils.image_utils import base64_to_image


class EnsembleColorAnalyzer:
    """
    Orchestrates multiple AI models for color analysis.
    
    Supports two modes:
    1. Parallel: All models analyze simultaneously, results aggregated
    2. Hybrid: Two models analyze in parallel, third model judges/evaluates
    """
    
    def __init__(self):
        self.gemini_client = config.get_client()
        self.openai_client = OpenAI(api_key=config.get_openai_key())
        self.anthropic_client = Anthropic(api_key=config.get_anthropic_key())
        
    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string."""
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str
    
    def _prepare_image(self, image_input: str | Image.Image) -> Image.Image:
        """Convert input to PIL Image."""
        if isinstance(image_input, str):
            return base64_to_image(image_input)
        return image_input
    
    async def _analyze_with_gemini(
        self, 
        image: Image.Image,
        model: str = "gemini-2.5-flash"
    ) -> AnalyzeColorSeasonResponseModel:
        """Analyze color with Gemini."""
        try:
            # Run synchronous call in thread pool
            response = await asyncio.to_thread(
                self.gemini_client.models.generate_content,
                model=model,
                config=gemini_types.GenerateContentConfig(
                    system_instruction=config.SYSTEM_PROMPT,
                    response_mime_type="application/json",
                ),
                contents=[image, config.JSON_PROMPT],
            )
            
            response_text = response.text.strip()
            # Clean JSON response
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            data = json.loads(response_text)
            defaults = {
                "undertone": "unknown",
                "season": "unknown",
                "subtype": "unknown",
                "reasoning": ""
            }
            for key, default_value in defaults.items():
                if key not in data or data[key] is None:
                    data[key] = default_value
            
            return AnalyzeColorSeasonResponseModel.model_validate(data)
        except Exception as e:
            raise ValueError(f"Gemini analysis failed: {e}")
    
    async def _analyze_with_openai(
        self, 
        image: Image.Image
    ) -> AnalyzeColorSeasonResponseModel:
        """Analyze color with OpenAI GPT-4 Vision."""
        try:
            # Convert image to base64
            img_base64 = self._image_to_base64(image)
            
            prompt = f"""{config.SYSTEM_PROMPT}

{config.JSON_PROMPT}"""
            
            # Run synchronous call in thread pool
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_base64}"
                                }
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
            )
            
            response_text = response.choices[0].message.content
            data = json.loads(response_text)
            
            defaults = {
                "undertone": "unknown",
                "season": "unknown",
                "subtype": "unknown",
                "reasoning": ""
            }
            for key, default_value in defaults.items():
                if key not in data or data[key] is None:
                    data[key] = default_value
            
            return AnalyzeColorSeasonResponseModel.model_validate(data)
        except Exception as e:
            raise ValueError(f"OpenAI analysis failed: {e}")
    
    async def _analyze_with_claude(
        self, 
        image: Image.Image
    ) -> AnalyzeColorSeasonResponseModel:
        """Analyze color with Claude."""
        try:
            # Convert image to base64
            img_base64 = self._image_to_base64(image)
            
            prompt = f"""{config.SYSTEM_PROMPT}

{config.JSON_PROMPT}"""
            
            # Run synchronous call in thread pool
            message = await asyncio.to_thread(
                self.anthropic_client.messages.create,
                model="claude-sonnet-4-5",
                max_tokens=1024,
                temperature=0.3,
                system=config.SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": img_base64,
                                },
                            },
                            {
                                "type": "text",
                                "text": config.JSON_PROMPT
                            }
                        ]
                    }
                ],
            )
            
            response_text = message.content[0].text
            # Clean JSON response
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            data = json.loads(response_text)
            
            defaults = {
                "undertone": "unknown",
                "season": "unknown",
                "subtype": "unknown",
                "reasoning": ""
            }
            for key, default_value in defaults.items():
                if key not in data or data[key] is None:
                    data[key] = default_value
            
            return AnalyzeColorSeasonResponseModel.model_validate(data)
        except Exception as e:
            raise ValueError(f"Claude analysis failed: {e}")
    
    async def _judge_results(
        self,
        results: List[AnalyzeColorSeasonResponseModel],
        judge_model: Literal["gemini", "openai", "claude"] = "gemini"
    ) -> AnalyzeColorSeasonResponseModel:
        """
        Use a judge model to evaluate and merge results from other models.
        """
        # Prepare results summary
        results_summary = []
        for i, result in enumerate(results):
            results_summary.append({
                "model": f"Model {i+1}",
                "personal_color_type": result.personal_color_type,
                "confidence": result.confidence,
                "undertone": result.undertone,
                "season": result.season,
                "subtype": result.subtype,
                "reasoning": result.reasoning
            })
        
        judge_prompt = f"""You are an expert color analyst judge. Review the following color analysis results from multiple AI models and provide a final, authoritative analysis.

Results from different models:
{json.dumps(results_summary, indent=2)}

Analyze the consistency and quality of these results. Consider:
1. Which analysis is most accurate based on the reasoning provided
2. If there's consensus, use that as the basis
3. If there's disagreement, use your expertise to determine the most likely correct answer
4. Adjust confidence based on agreement level

Return ONLY a valid JSON object with the following structure:
{{
    "personal_color_type": "string (e.g., 'Deep Autumn', 'Light Spring', etc.)",
    "confidence": 0.0-1.0 (adjusted based on consensus),
    "undertone": "warm or cool",
    "season": "spring, summer, autumn, or winter",
    "subtype": "string (e.g., 'deep', 'light', 'soft', 'bright', etc.)",
    "reasoning": "brief explanation of your final decision and why"
}}"""
        
        if judge_model == "gemini":
            response = await asyncio.to_thread(
                self.gemini_client.models.generate_content,
                model="gemini-2.5-flash",
                config=gemini_types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
                contents=[judge_prompt],
            )
            response_text = response.text.strip()
        elif judge_model == "openai":
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-4o",
                messages=[
                    {"role": "user", "content": judge_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            response_text = response.choices[0].message.content
        else:  # claude
            message = await asyncio.to_thread(
                self.anthropic_client.messages.create,
                model="claude-sonnet-4-5",
                max_tokens=1024,
                temperature=0.2,
                messages=[
                    {"role": "user", "content": judge_prompt}
                ],
            )
            response_text = message.content[0].text
        
        # Clean JSON response
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        data = json.loads(response_text)
        defaults = {
            "undertone": "unknown",
            "season": "unknown",
            "subtype": "unknown",
            "reasoning": ""
        }
        for key, default_value in defaults.items():
            if key not in data or data[key] is None:
                data[key] = default_value
        
        return AnalyzeColorSeasonResponseModel.model_validate(data)
    
    def _aggregate_results(
        self,
        results: List[AnalyzeColorSeasonResponseModel],
        method: Literal["voting", "weighted_average", "consensus"] = "weighted_average"
    ) -> AnalyzeColorSeasonResponseModel:
        """
        Aggregate results from multiple models.
        
        Methods:
        - voting: Majority vote on categorical fields, average on confidence
        - weighted_average: Weight by confidence scores
        - consensus: Only return result if models agree (≥2/3 consensus)
        """
        if not results:
            raise ValueError("No results to aggregate")
        
        if method == "voting":
            return self._aggregate_voting(results)
        elif method == "weighted_average":
            return self._aggregate_weighted_average(results)
        elif method == "consensus":
            return self._aggregate_consensus(results)
        else:
            raise ValueError(f"Unknown aggregation method: {method}")
    
    def _aggregate_voting(
        self,
        results: List[AnalyzeColorSeasonResponseModel]
    ) -> AnalyzeColorSeasonResponseModel:
        """Majority vote on categorical fields."""
        # Count votes for each category
        personal_color_votes: Dict[str, int] = {}
        undertone_votes: Dict[str, int] = {}
        season_votes: Dict[str, int] = {}
        subtype_votes: Dict[str, int] = {}
        
        total_confidence = 0.0
        all_reasoning = []
        
        for result in results:
            # Vote for personal_color_type
            personal_color_votes[result.personal_color_type] = \
                personal_color_votes.get(result.personal_color_type, 0) + 1
            
            # Vote for undertone
            undertone_votes[result.undertone] = \
                undertone_votes.get(result.undertone, 0) + 1
            
            # Vote for season
            season_votes[result.season] = \
                season_votes.get(result.season, 0) + 1
            
            # Vote for subtype
            subtype_votes[result.subtype] = \
                subtype_votes.get(result.subtype, 0) + 1
            
            total_confidence += result.confidence
            all_reasoning.append(result.reasoning)
        
        # Get majority votes
        personal_color_type = max(personal_color_votes, key=personal_color_votes.get)
        undertone = max(undertone_votes, key=undertone_votes.get)
        season = max(season_votes, key=season_votes.get)
        subtype = max(subtype_votes, key=subtype_votes.get)
        
        # Average confidence
        avg_confidence = total_confidence / len(results)
        
        # Consensus reasoning
        consensus_count = personal_color_votes[personal_color_type]
        consensus_ratio = consensus_count / len(results)
        
        reasoning = f"Ensemble result from {len(results)} models. " \
                   f"Consensus: {consensus_count}/{len(results)} models agree on '{personal_color_type}'. " \
                   f"Individual analyses: {'; '.join(all_reasoning[:2])}"
        
        return AnalyzeColorSeasonResponseModel(
            personal_color_type=personal_color_type,
            confidence=avg_confidence * consensus_ratio,  # Adjust confidence by consensus
            undertone=undertone,
            season=season,
            subtype=subtype,
            reasoning=reasoning
        )
    
    def _aggregate_weighted_average(
        self,
        results: List[AnalyzeColorSeasonResponseModel]
    ) -> AnalyzeColorSeasonResponseModel:
        """Weight results by confidence scores."""
        # Weight by confidence
        total_weight = sum(r.confidence for r in results)
        
        if total_weight == 0:
            # Fallback to simple average
            return self._aggregate_voting(results)
        
        # For categorical fields, use weighted voting
        personal_color_weights: Dict[str, float] = {}
        undertone_weights: Dict[str, float] = {}
        season_weights: Dict[str, float] = {}
        subtype_weights: Dict[str, float] = {}
        
        all_reasoning = []
        
        for result in results:
            weight = result.confidence / total_weight
            
            personal_color_weights[result.personal_color_type] = \
                personal_color_weights.get(result.personal_color_type, 0) + weight
            
            undertone_weights[result.undertone] = \
                undertone_weights.get(result.undertone, 0) + weight
            
            season_weights[result.season] = \
                season_weights.get(result.season, 0) + weight
            
            subtype_weights[result.subtype] = \
                subtype_weights.get(result.subtype, 0) + weight
            
            all_reasoning.append(result.reasoning)
        
        # Get highest weighted choices
        personal_color_type = max(personal_color_weights, key=personal_color_weights.get)
        undertone = max(undertone_weights, key=undertone_weights.get)
        season = max(season_weights, key=season_weights.get)
        subtype = max(subtype_weights, key=subtype_weights.get)
        
        # Weighted average confidence
        weighted_confidence = sum(r.confidence * r.confidence / total_weight for r in results)
        
        # Consensus weight
        consensus_weight = personal_color_weights[personal_color_type]
        
        reasoning = f"Ensemble result (weighted by confidence) from {len(results)} models. " \
                   f"Primary consensus: {consensus_weight:.1%} weighted agreement on '{personal_color_type}'. " \
                   f"Analyses: {'; '.join(all_reasoning[:2])}"
        
        return AnalyzeColorSeasonResponseModel(
            personal_color_type=personal_color_type,
            confidence=weighted_confidence * consensus_weight,
            undertone=undertone,
            season=season,
            subtype=subtype,
            reasoning=reasoning
        )
    
    def _aggregate_consensus(
        self,
        results: List[AnalyzeColorSeasonResponseModel],
        min_consensus: float = 0.67
    ) -> AnalyzeColorSeasonResponseModel:
        """Only return result if models reach consensus (≥67% by default)."""
        # Count votes
        personal_color_votes: Dict[str, int] = {}
        
        for result in results:
            personal_color_votes[result.personal_color_type] = \
                personal_color_votes.get(result.personal_color_type, 0) + 1
        
        # Check if we have consensus
        max_votes = max(personal_color_votes.values())
        consensus_ratio = max_votes / len(results)
        
        if consensus_ratio < min_consensus:
            # No consensus - use weighted average but lower confidence
            result = self._aggregate_weighted_average(results)
            result.confidence *= 0.7  # Penalize for lack of consensus
            result.reasoning = f"Low consensus ({consensus_ratio:.1%}). " + result.reasoning
            return result
        
        # We have consensus - use voting for all fields
        return self._aggregate_voting(results)
    
    async def analyze_parallel(
        self,
        image_input: str | Image.Image,
        aggregation_method: Literal["voting", "weighted_average", "consensus"] = "weighted_average"
    ) -> AnalyzeColorSeasonResponseModel:
        """
        Analyze color using all three models in parallel, then aggregate results.
        
        This is the fastest approach and provides diverse perspectives.
        """
        image = self._prepare_image(image_input)
        
        # Run all analyses in parallel
        tasks = [
            self._analyze_with_gemini(image),
            self._analyze_with_openai(image),
            self._analyze_with_claude(image),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and collect valid results
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Model {i} failed: {result}")
            else:
                valid_results.append(result)
        
        if not valid_results:
            raise ValueError("All models failed to analyze the image")
        
        # Aggregate results
        return self._aggregate_results(valid_results, method=aggregation_method)
    
    async def analyze_hybrid(
        self,
        image_input: str | Image.Image,
        judge_model: Literal["gemini", "openai", "claude"] = "gemini",
        parallel_models: Optional[List[Literal["gemini", "openai", "claude"]]] = None
    ) -> AnalyzeColorSeasonResponseModel:
        """
        Hybrid approach: Two models analyze in parallel, third model judges/evaluates.
        
        This provides deeper analysis and validation.
        """
        image = self._prepare_image(image_input)
        
        # Determine which models to use
        if parallel_models is None:
            # Default: Gemini and OpenAI analyze, Claude judges
            parallel_models = ["gemini", "openai"]
            if judge_model in parallel_models:
                # If judge is in parallel models, use the remaining two
                all_models = ["gemini", "openai", "claude"]
                parallel_models = [m for m in all_models if m != judge_model]
        
        # Run parallel analyses
        parallel_tasks = []
        for model in parallel_models:
            if model == "gemini":
                parallel_tasks.append(self._analyze_with_gemini(image))
            elif model == "openai":
                parallel_tasks.append(self._analyze_with_openai(image))
            elif model == "claude":
                parallel_tasks.append(self._analyze_with_claude(image))
        
        parallel_results = await asyncio.gather(*parallel_tasks, return_exceptions=True)
        
        # Filter valid results
        valid_results = []
        for result in parallel_results:
            if isinstance(result, Exception):
                print(f"Parallel model failed: {result}")
            else:
                valid_results.append(result)
        
        if not valid_results:
            raise ValueError("All parallel models failed")
        
        # Judge evaluates and merges results
        judge_result = await self._judge_results(valid_results, judge_model=judge_model)
        
        return judge_result


# Global instance
ensemble_analyzer = EnsembleColorAnalyzer()

