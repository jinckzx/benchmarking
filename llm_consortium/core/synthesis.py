# from typing import List, Dict
# from openai import AsyncOpenAI
# from ..config.models import LogEntry
# from ..utils.prompt_utils import read_arbiter_prompt, read_arbiter_system_prompt
# from ..utils.extractors import ResponseExtractor
# from ..database.synthesis_db import SynthesisDatabaseHandler
# from ..utils.logging import logger
# from .client_init import llm

# class SynthesisHandler:
#     def __init__(self, extractor: ResponseExtractor):
#         self.client = llm
#         self.extractor = extractor
#         self.db_handler = SynthesisDatabaseHandler()
#         self.arbiter_system_prompt = read_arbiter_system_prompt()

#     async def synthesize(self, prompt: str, responses: List[LogEntry], 
#                         arbiter: str, iteration: int) -> Dict:
#         comparisons = "\n\n".join(
#             f"Model: {entry.model}\nConfidence: {entry.confidence:.2f}\nResponse:\n{entry.response}"
#             for entry in responses
#         )
        
#         synthesis_prompt = read_arbiter_prompt().format(
#             prompt=prompt,
#             comparisons=comparisons,
#             arbiter=arbiter
#         )
#         #Updated messages with system prompt
#         messages = [{"role": "system", "content": self.arbiter_system_prompt},
#                     {"role": "user", "content": synthesis_prompt}]
#         try:
#             response = await self.client.chat(
#                 model=arbiter,
#                 # messages=[{"role": "user", "content": synthesis_prompt}],
#                 messages=messages,
#                 temperature=0.2
#             )
#             content = response["content"]
            
#             result = {
#                 "text": content,
#                 "confidence": self.extractor.extract_confidence(content),
#                 "analysis": self._extract_analysis(content),
#                 "dissenting_views": self._extract_dissent(content),
#                 "arbiter_model": arbiter
#             }

#             # Log to synthesis database
#             self.db_handler.log_synthesis(
#                 iteration=iteration,
#                 prompt=prompt,
#                 arbiter=arbiter,
#                 synthesized_text=result['text'],
#                 confidence=result['confidence'],
#                 analysis=result['analysis'],
#                 dissent=result['dissenting_views']
#             )

#             logger.info(
#                 f"Iteration {iteration} Synthesis Complete - "
#                 f"Confidence: {result['confidence']:.2f}"
#             )
            
#             return result
            
#         except Exception as e:
#             error_msg = f"Arbiter synthesis error: {str(e)}"
#             logger.error(error_msg)
#             return {
#                 "text": error_msg,
#                 "confidence": 0.0,
#                 "analysis": "",
#                 "dissenting_views": "",
#                 "arbiter_model": arbiter
#             }    
#     def _extract_analysis(self, text: str) -> str:
#         return self.extractor.extract_section(
#             text, 
#             "### Analysis of Differences:", 
#             "### Dissenting Views:"
#         )

#     def _extract_dissent(self, text: str) -> str:
#         return self.extractor.extract_section(
#             text, 
#             "### Dissenting Views:"
#         )
# """v1 using random search"""
# from typing import List, Dict
# import numpy as np
# from openai import AsyncOpenAI
# from ..config.models import LogEntry
# from ..utils.prompt_utils import read_arbiter_prompt, read_arbiter_system_prompt
# from ..utils.extractors import ResponseExtractor
# from ..database.synthesis_db import SynthesisDatabaseHandler
# from ..utils.logging import logger
# from .client_init import llm
# from .random_search import ArbiterTemperatureTuner

# class SynthesisHandler:
#     def __init__(self, extractor: ResponseExtractor):
#         self.client = llm
#         self.extractor = extractor
#         self.db_handler = SynthesisDatabaseHandler()
#         self.arbiter_system_prompt = read_arbiter_system_prompt()
#         self.tuner = ArbiterTemperatureTuner()

#     async def synthesize(self, prompt: str, responses: List[LogEntry], 
#                         arbiter: str, iteration: int, 
#                         min_temp: float, max_temp: float, 
#                         num_trials: int) -> Dict:
#         """Perform synthesis with random temperature search for arbiter"""
#         # Generate random temperatures
#         temperatures = self.tuner.generate_temperatures(min_temp, max_temp, num_trials)
#         best_result = None
#         all_trials = []

#         for temp in temperatures:
#             try:
#                 trial_result = await self._run_arbiter(
#                     prompt=prompt,
#                     responses=responses,
#                     arbiter=arbiter,
#                     temperature=temp
#                 )
                
#                 # Track best result
#                 if not best_result or trial_result['confidence'] > best_result['confidence']:
#                     best_result = trial_result

#                 # Store trial data
#                 all_trials.append({
#                     'temperature': temp,
#                     'confidence': trial_result['confidence'],
#                     'text': trial_result['text']
#                 })
                
#                 # Log individual trial
#                 self.db_handler.log_synthesis(
#                     iteration=iteration,
#                     prompt=prompt,
#                     arbiter=arbiter,
#                     synthesized_text=trial_result['text'],
#                     confidence=trial_result['confidence'],
#                     analysis=trial_result['analysis'],
#                     dissent=trial_result['dissenting_views'],
#                     temperature=temp
#                 )

#             except Exception as e:
#                 logger.error(f"Temperature trial {temp} failed: {str(e)}")
#                 continue

#         # Log best result
#         if best_result:
#             self.db_handler.log_synthesis(
#                     iteration=iteration,
#                     prompt=prompt,
#                     arbiter=arbiter,
#                     synthesized_text=best_result['text'],
#                     confidence=best_result['confidence'],
#                     temperature=best_result['temperature'],
#                     analysis=best_result['analysis'],
#                     dissent=best_result['dissenting_views'],
#                     is_best_result=True
#             )

#             logger.info(
#                 f"Iteration {iteration} Best Synthesis - "
#                 f"Temp: {best_result['temperature']:.2f}, "
#                 f"Confidence: {best_result['confidence']:.2f}"
#             )

#         return {
#             'best': best_result or {
#                 'text': "No valid synthesis generated",
#                 'confidence': 0.0,
#                 'temperature': 0.0,
#                 'analysis': '',
#                 'dissenting_views': ''
#             },
#             'trials': all_trials
#         }

#     async def _run_arbiter(self, prompt: str, responses: List[LogEntry], 
#                          arbiter: str, temperature: float) -> Dict:
#         """Execute single arbiter query with specific temperature"""
#         comparisons = "\n\n".join(
#             f"Model: {entry.model}\nConfidence: {entry.confidence:.2f}\nResponse:\n{entry.response}"
#             for entry in responses
#         )
        
#         synthesis_prompt = read_arbiter_prompt().format(
#             prompt=prompt,
#             comparisons=comparisons,
#             arbiter=arbiter
#         )

#         messages = [
#             {"role": "system", "content": self.arbiter_system_prompt},
#             {"role": "user", "content": synthesis_prompt}
#         ]

#         response = await self.client.chat(
#             model=arbiter,
#             messages=messages,
#             temperature=temperature
#         )

#         content = response["content"]
        
#         return {
#             "text": content,
#             "confidence": self.extractor.extract_confidence(content),
#             "analysis": self._extract_analysis(content),
#             "dissenting_views": self._extract_dissent(content),
#             "temperature": temperature,
#             "arbiter_model": arbiter
#         }

#     def _extract_analysis(self, text: str) -> str:
#         return self.extractor.extract_section(
#             text, 
#             "### Analysis of Differences:", 
#             "### Dissenting Views:"
#         )

#     def _extract_dissent(self, text: str) -> str:
#         return self.extractor.extract_section(
#             text, 
#             "### Dissenting Views:"
#         )
# """v2 using random search"""
from typing import List, Dict
import numpy as np
from ..config.models import LogEntry
from ..utils.prompt_utils import read_arbiter_prompt, read_arbiter_system_prompt
from ..utils.extractors import ResponseExtractor
from ..database.synthesis_db import SynthesisDatabaseHandler
from ..utils.logging import logger
from .client_init import llm
from .random_search import ArbiterTemperatureTuner

class SynthesisHandler:
    def __init__(self, extractor: ResponseExtractor):
        self.client = llm
        self.extractor = extractor
        self.db_handler = SynthesisDatabaseHandler()
        self.arbiter_system_prompt = read_arbiter_system_prompt()
        self.tuner = ArbiterTemperatureTuner()

    async def synthesize(self, prompt: str, responses: List[LogEntry], 
                        arbiter: str, iteration: int, 
                        min_temp: float, max_temp: float, 
                        num_trials: int) -> Dict:
        """Perform synthesis with random temperature search for arbiter"""
        temperatures = self.tuner.generate_temperatures(min_temp, max_temp, num_trials)
        best_result = None
        all_trials = []

        for temp in temperatures:
            try:
                # Run arbiter with current temperature
                trial_result = await self._run_arbiter(
                    prompt=prompt,
                    responses=responses,
                    arbiter=arbiter,
                    temperature=temp
                )
                
                # Log to temperature_trials table
                self.db_handler.log_temperature_trial(
                    iteration=iteration,
                    temperature=temp,
                    confidence=trial_result['confidence'],
                    synthesized_text=trial_result['text'],
                    analysis=trial_result['analysis'],
                    dissent=trial_result['dissenting_views']
                )

                # Track best result
                if not best_result or trial_result['confidence'] > best_result['confidence']:
                    best_result = trial_result

                all_trials.append({
                    'temperature': temp,
                    'confidence': trial_result['confidence'],
                    'text': trial_result['text']
                })

            except Exception as e:
                logger.error(f"Temperature trial {temp} failed: {str(e)}")
                continue

        # Log best result to synthesis_results table
        if best_result:
            self.db_handler.log_synthesis(
                iteration=iteration,
                prompt=prompt,
                arbiter=arbiter,
                synthesized_text=best_result['text'],
                confidence=best_result['confidence'],
                temperature=best_result['temperature'],
                analysis=best_result['analysis'],
                dissent=best_result['dissenting_views'],
                is_best_result=True  # Explicitly mark as best
            )
            logger.info(
                f"Iteration {iteration} Best Synthesis - "
                f"Temp: {best_result['temperature']:.2f}, "
                f"Confidence: {best_result['confidence']:.2f}"
            )
        else:
            logger.error(f"No valid synthesis generated in iteration {iteration}")

        return {
            'best': best_result or {
                'text': "No valid synthesis generated",
                'confidence': 0.0,
                'temperature': 0.0,
                'analysis': '',
                'dissenting_views': ''
            },
            'trials': all_trials
        }

    async def _run_arbiter(self, prompt: str, responses: List[LogEntry], 
                         arbiter: str, temperature: float) -> Dict:
        """Execute single arbiter query with specific temperature"""
        comparisons = "\n\n".join(
            f"Model: {entry.model}\nConfidence: {entry.confidence:.2f}\nResponse:\n{entry.response}"
            for entry in responses
        )
        
        synthesis_prompt = read_arbiter_prompt().format(
            prompt=prompt,
            comparisons=comparisons,
            arbiter=arbiter
        )

        messages = [
            {"role": "system", "content": self.arbiter_system_prompt},
            {"role": "user", "content": synthesis_prompt}
        ]

        response = await self.client.chat(
            model=arbiter,
            messages=messages,
            temperature=temperature
        )

        content = response["content"]
        
        return {
            "text": content,
            "confidence": self.extractor.extract_confidence(content),
            "analysis": self._extract_analysis(content),
            "dissenting_views": self._extract_dissent(content),
            "temperature": temperature,
            "arbiter_model": arbiter
        }

    def _extract_analysis(self, text: str) -> str:
        return self.extractor.extract_section(
            text, 
            "### Analysis of Differences:", 
            "### Dissenting Views:"
        )

    def _extract_dissent(self, text: str) -> str:
        return self.extractor.extract_section(
            text, 
            "### Dissenting Views:"
        )