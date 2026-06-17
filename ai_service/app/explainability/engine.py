import torch
import numpy as np
from typing import List, Dict, Any, Tuple
from transformers import AutoTokenizer
from sklearn.linear_model import Ridge

class ExplainabilityEngine:
    def __init__(self, model: torch.nn.Module, tokenizer: AutoTokenizer, device: str = "cpu"):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
        self.model.to(self.device)
        self.model.eval()

    def get_attention_explanation(self, text: str, tokens: List[str], attn_weights: torch.Tensor) -> List[Dict[str, Any]]:
        """Extracts and normalizes attention weights for each token."""
        # attn_weights shape: [1, num_heads, seq_len, seq_len] or [1, seq_len, seq_len]
        # We average attention across all heads and summarize it as token-wise score
        # Let's take the mean of attention weights across heads and target tokens (average attention received by each token)
        if len(attn_weights.shape) == 3:
            # [batch_size, seq_len, seq_len]
            weights = attn_weights[0].detach().cpu().numpy()
        else:
            # [batch_size, num_heads, seq_len, seq_len]
            weights = attn_weights[0].mean(dim=0).detach().cpu().numpy()
            
        # Sum attention weights going into each token (columns or rows depending on attention direction)
        # Typically shape is [seq_len, seq_len], where weights[i, j] is attention from token i to token j.
        # We take average attention received by each token j.
        token_attn = weights.mean(axis=0)
        
        # Normalize between 0 and 1
        if token_attn.max() > token_attn.min():
            token_attn = (token_attn - token_attn.min()) / (token_attn.max() - token_attn.min())
            
        explanation = []
        # Exclude special tokens in output if needed, but keep aligned with input tokens
        for i, token in enumerate(tokens):
            if token not in [self.tokenizer.cls_token, self.tokenizer.sep_token, self.tokenizer.pad_token]:
                explanation.append({
                    "word": token.replace(" ", ""), # Clean XLM-RoBERTa wordpiece marker
                    "score": float(token_attn[i])
                })
        return explanation

    def predict_probs_for_perturbed_texts(self, perturbed_texts: List[str], level: int = 1, target_class: int = 0) -> np.ndarray:
        """Helper to get prediction probabilities for a list of texts (used for LIME)."""
        probs = []
        with torch.no_grad():
            for text in perturbed_texts:
                if not text.strip():
                    probs.append(0.5 if level == 1 else 1.0 / 6)
                    continue
                inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=128)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                outputs = self.model(**inputs)
                
                if level == 1:
                    logits = outputs["level1_logits"]
                    prob = torch.softmax(logits, dim=-1)[0][target_class].item()
                else:
                    logits = outputs["level2_logits"]
                    prob = torch.softmax(logits, dim=-1)[0][target_class].item()
                probs.append(prob)
        return np.array(probs)

    def explain_with_lime(self, text: str, level: int = 1, target_class: int = 0, num_samples: int = 60) -> List[Dict[str, Any]]:
        """Generates word importance scores using a custom local perturbation linear model (LIME)."""
        words = text.split()
        num_words = len(words)
        if num_words == 0:
            return []

        # Generate perturbed bags of words
        # 1 means word is present, 0 means word is masked
        features = np.random.binomial(1, 0.7, size=(num_samples, num_words))
        features[0, :] = 1 # Keep the original text as the first sample

        perturbed_texts = []
        for row in features:
            perturbed_words = [words[i] for i in range(num_words) if row[i] == 1]
            perturbed_texts.append(" ".join(perturbed_words))

        # Predict probabilities
        predictions = self.predict_probs_for_perturbed_texts(perturbed_texts, level, target_class)

        # Compute cosine similarities between perturbations and original text (represented as binary vectors)
        # Cosine distance weighting
        weights = []
        for row in features:
            # Intersection over union or simple match ratio
            similarity = np.sum(row) / num_words
            # Exponential kernel
            weights.append(np.exp(-((1 - similarity) ** 2) / 0.25))
        weights = np.array(weights)

        # Fit Ridge regression model
        regressor = Ridge(alpha=1.0, fit_intercept=True)
        regressor.fit(features, predictions, sample_weight=weights)

        importance_scores = regressor.coef_
        
        explanation = []
        for i, word in enumerate(words):
            explanation.append({
                "word": word,
                "score": float(importance_scores[i])
            })
            
        # Sort by absolute score descending
        explanation.sort(key=lambda x: abs(x["score"]), reverse=True)
        return explanation

    def explain_with_shap(self, text: str, level: int = 1, target_class: int = 0) -> List[Dict[str, Any]]:
        """SHAP-like explanation using Integrated Gradients or Leave-One-Out approximation."""
        words = text.split()
        num_words = len(words)
        if num_words == 0:
            return []
            
        # Compute baseline prediction (empty string or masked words)
        with torch.no_grad():
            inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=128)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            outputs = self.model(**inputs)
            if level == 1:
                base_prob = torch.softmax(outputs["level1_logits"], dim=-1)[0][target_class].item()
            else:
                base_prob = torch.softmax(outputs["level2_logits"], dim=-1)[0][target_class].item()

        # Leave-One-Out attribution (SHAP approximation for speed and stability in deployment)
        shap_values = []
        for i in range(num_words):
            loo_words = words[:i] + words[i+1:]
            loo_text = " ".join(loo_words)
            with torch.no_grad():
                loo_inputs = self.tokenizer(loo_text, return_tensors="pt", padding=True, truncation=True, max_length=128)
                loo_inputs = {k: v.to(self.device) for k, v in loo_inputs.items()}
                loo_outputs = self.model(**loo_inputs)
                if level == 1:
                    loo_prob = torch.softmax(loo_outputs["level1_logits"], dim=-1)[0][target_class].item()
                else:
                    loo_prob = torch.softmax(loo_outputs["level2_logits"], dim=-1)[0][target_class].item()
            
            # The attribution is how much the probability drops when this word is removed
            marginal_contribution = base_prob - loo_prob
            shap_values.append(marginal_contribution)

        explanation = []
        for i, word in enumerate(words):
            explanation.append({
                "word": word,
                "score": float(shap_values[i])
            })
        explanation.sort(key=lambda x: abs(x["score"]), reverse=True)
        return explanation

    def generate_human_explanation(self, predictions: Dict[str, Any], lime_scores: List[Dict[str, Any]], level2_labels: List[str]) -> str:
        """Generates a contextual, user-friendly Urdu and English explanation of the model decision."""
        l1_pred = predictions["level1_pred"]
        l1_conf = predictions["level1_conf"]
        
        top_words = [item["word"] for item in lime_scores if item["score"] > 0.05][:3]
        top_words_str = "، ".join([f"'{w}'" for w in top_words]) if top_words else "متن کے عام سیاق و سباق"
        
        if l1_pred == "Violence":
            l2_pred = predictions["level2_pred"]
            l2_conf = predictions.get("level2_conf", 0.0)
            
            explanation_en = (
                f"The system detected Violence Incitation with {l1_conf:.1%} confidence. "
                f"It was categorized as {l2_pred} Violence ({l2_conf:.1%} confidence). "
                f"The decision was primarily influenced by the words: {', '.join([f'\"{w}\"' for w in top_words]) if top_words else 'general context'}."
            )
            explanation_ur = (
                f"سسٹم نے {l1_conf:.1%} اعتماد کے ساتھ تشدد پر اکسانے کا پتہ لگایا ہے۔ "
                f"اسے {l2_pred} تشدد کے طور پر درجہ بندی کیا گیا ہے ({l2_conf:.1%} اعتماد)۔ "
                f"یہ فیصلہ بنیادی طور پر الفاظ {top_words_str} سے متاثر ہوا ہے۔"
            )
        else:
            explanation_en = (
                f"The system detected Non-Violence with {l1_conf:.1%} confidence. "
                f"The post is safe and does not contain violence incitation."
            )
            explanation_ur = (
                f"سسٹم نے {l1_conf:.1%} اعتماد کے ساتھ غیر تشدد کا پتہ لگایا ہے۔ "
                f"یہ پوسٹ محفوظ ہے اور اس میں تشدد پر اکسانے کا کوئی عنصر نہیں ہے۔"
            )
            
        return f"{explanation_en}\n\n{explanation_ur}"
